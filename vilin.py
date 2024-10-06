import asyncio
import random
from bot import bot
from aiogram import types, Dispatcher
from commands.db import conn, cursor, url_name, get_balance
from assets.transform import transform_int as tr
from commands.games.db import gametime
from commands.main import win_luser
from assets.antispam import antispam
from decimal import Decimal
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from commands.help import CONFIG


"""
MODULE Vilin
By Vladuk(@Vladislav_225)
Please subscribe to channel!!!
@gamechat225
@bisnessbotlive
"""


CONFIG['help_game'] += '\n✅❌ Вилин'


async def upd_balance(uid, summ, type):
    balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (uid,)).fetchone()[0]
    if type == "win":
        summ = Decimal(balance) + Decimal(summ)
    else:
        summ = Decimal(balance) - Decimal(summ)

    cursor.execute(f"UPDATE users SET balance = ? WHERE user_id = ?", (str(summ), uid))
    cursor.execute(f"UPDATE users SET games = games + 1 WHERE user_id = ?", (uid,))
    conn.commit()


@antispam
async def vilin(message: types.Message):
    uid = message.from_user.id
    rwin, rloser = await win_luser()
    balance = await get_balance(uid)
    url = await url_name(uid)

    try:
        if message.text.lower().split()[1] in ['все', 'всё']:
            summ = balance
        else:
            summ = message.text.split()[1].replace('е', 'e')
            summ = int(float(summ))
    except:
        await message.answer(f'{url}, пожалуйста, введите корректную сумму для ставки. {rloser} 🧐')
        return

    gt = await gametime(uid)
    if gt == 1:
        await message.answer(f'{url}, пожалуйста, подождите 5 секунд перед следующей игрой. {rloser} ⏳')
        return

    if summ < 100:
        await message.answer(f'{url}, минимальная ставка — 100 монет. Попробуйте снова, {rloser}. 💰')
        return

    if balance < summ:
        await message.answer(f'{url}, у вас недостаточно средств для ставки. Пополните баланс и попробуйте снова. {rloser} 💸')
        return

    markup = InlineKeyboardMarkup(resize_keyboard=True)
    yes = InlineKeyboardButton(text='🎯 Да, играю!', callback_data=f'yes_{uid}_{summ}')
    no = InlineKeyboardButton(text='❌ Нет, отмена', callback_data=f'no_{uid}')
    markup.add(yes, no)
    
    await message.answer(f'''
🎮 <b>Готовы сыграть в "Вилин"?</b>
Ставка: <b>{summ} монет</b>
    
Для подтверждения нажмите "Да", если хотите начать игру, или "Нет" для отмены. 
''', reply_markup=markup, parse_mode='HTML')


async def callback_vilin_yes(callback: types.CallbackQuery):
    data = callback.data.split('_')
    owner_button = int(float(data[1]))
    summ = int(float(data[2]))

    if callback.from_user.id == owner_button:
        chance = random.random()

        if chance < 0.45:
            su = int(summ * 0.5)
            txt = f'🎉 Удача на вашей стороне! Вы выиграли <b>{su} монет!</b> 🤑'
            await upd_balance(owner_button, su, 'win')
        elif chance < 0.50:
            txt = '🤷‍♂️ Ничья! Вы не потеряли свои деньги и можете попробовать снова.'
        else:
            txt = f'😔 Увы, вы проиграли <b>{summ} монет</b>. Не сдавайтесь и удача обязательно улыбнется!'
            await upd_balance(owner_button, summ, 'lose')

        await asyncio.sleep(2)
        await callback.message.edit_text(text=txt, parse_mode='HTML')
    else:
        await callback.answer('Эта кнопка не для вас! 🎮')


async def callback_vilin_no(callback: types.CallbackQuery):
    owner_button = int(callback.data.split('_')[1])

    if callback.from_user.id == owner_button:
        txt = '🚫 Игра отменена. Возвращайтесь, когда будете готовы! ✔'
        await callback.message.edit_text(text=txt)
    else:
        await callback.answer('Эта кнопка не для вас! 🎮')


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(vilin, lambda message: message.text.lower().startswith('вилин'))
    dp.register_callback_query_handler(callback_vilin_yes, lambda callback: callback.data.startswith("yes_"))
    dp.register_callback_query_handler(callback_vilin_no, lambda callback: callback.data.startswith("no_"))
	

MODULE_DESCRIPTION = {
	'name': '✅❌ Вилин',
	'description': 'Новая игра "вилин"'
}
