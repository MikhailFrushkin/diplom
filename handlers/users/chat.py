from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.bestdeal import bestdeal
from handlers.users.help import bot_help
from handlers.users.history import history

from loader import dp


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    if message.text == 'Поиск по возрастанию цены':
        pass
    elif message.text == 'Поиск по убыванию цены':
        pass
    elif message.text == 'Поиск по точным параметрам':
        await bestdeal(message)
    elif message.text == 'Помощь':
        await bot_help(message)
    elif message.text == 'История':
        await history(message)
    else:
        await message.answer('{} - неверная команда. Для справки введите /help'.format(message.text))


@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message, state: FSMContext):
    state = await state.get_state()
    await message.answer(f"Эхо в состоянии <code>{state}</code>.\n"
                         f"\nСодержание сообщения:\n"
                         f"<code>{message}</code>")
