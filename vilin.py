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

from commands.help import CONFIG


"""
MODULE Fishing
By Vladuk(@Vladislav_225)
Please subscribe to channel!!!
@gamechat225
@bisnessbotlive
This is the very first user module.
"""


CONFIG['help_game'] += '\n🎣 Рыбалка'


wins_fishing = [
    "🎣🐟 | Отлично! Вы поймали щуку, вот ваша награда: {}$",
    "🎣🐠 | Поздравляем! Вы поймали окуня, вот ваша награда: {}$",
    "🎣🐡 | Отлично! Вы поймали судака, вот ваша награда: {}$",
    "🎣🐬 | Прекрасно! Вы поймали дельфина, вот ваша награда: {}$",
    "🎣🦈 | Невероятно! Вы поймали акулу, вот ваша награда: {}$",
    "🎣🦑 | Фантастика! Вы поймали кальмара, вот ваша награда: {}$"
]


losses_fishing = [
    "🎣🪱 | О нет! Ваша наживка съедена червем, попробуйте еще раз!",
    "🎣🌿 | Увы! Вы поймали только водоросли. Не расстраивайтесь, в следующий раз повезет!",
    "🎣🗑️ | Что за неудача! Вы поймали старую консервную банку. Пора менять место рыбалки!",
    "🎣🐢 | Упс! Вы поймали черепаху. Она смотрит на вас осуждающе.",
    "🎣🐍 | Будьте осторожны! Вместо рыбы на крючке змея. Лучше отпустить ее!",
    "🎣🌧️ | Плохие новости! Начался дождь, и рыбалка сорвалась. Возвращайтесь, когда погода улучшится."
]


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
async def game(message: types.Message):
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
		await message.answer(f'{url}, вы не ввели ставку для игры {rloser}')
		return

	gt = await gametime(uid)
	if gt == 1:
		await message.answer(f'{url}, играть можно каждые 5 секунд. Подождите немного {rloser}')
		return

	if summ < 100:
		await message.answer(f'{url}, ваша ставка не может быть меньше 100$ {rloser}')
		return

	if balance < summ:
		await message.answer(f'{url}, у вас недостаточно денег {rloser}')
		return

	chance = random.random()

	if chance < 0.45:
		su = int(summ * 0.5)
		txt = random.choice(wins_fishing).format(tr(su))
		await upd_balance(uid, su, 'win')
	elif chance < 0.50:
		txt = '💥❎ | Вы никого не словили... деньги остаются при вас.'
	else:
		txt = random.choice(losses_fishing)
		await upd_balance(uid, summ, 'lose')

	msg = await message.answer("💥 | Кидаем удочку... посмотрим в кого вы выловите")
	await asyncio.sleep(2)
	await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=txt)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(game, lambda message: message.text.lower().startswith('рыбалка'))
	

MODULE_DESCRIPTION = {
	'name': '🎣 Рыбалка',
	'description': 'Новая игра "рыбалка"'
}
