import logging
import asyncio
import math

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode,ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# через pip install необходимо установить aiogram, logging, asyncio


# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token="YOur_token_bot")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# определяем состояния для конечного автомата
class Form(StatesGroup):
    waiting_for_price = State()

# обработчик команды /start
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    # инициализируем FSM (Finite State Machine) для пользователя
    await Form.waiting_for_price.set()
    await message.answer("Здравствуйте, введите стоимость товара в юанях:")

# start - Запуск бота
# reset - Обнулить общую сумму заказа
# formula - По какой вообще формуле считается цена окончательная цена
# delivery - Стоимость доставки
# link - Написать насчёт заказа

# обработчик ввода стоимости товара
@dp.message_handler(state=Form.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    try:
        # пытаемся преобразовать введенный текст в число
        price = float(message.text)
    except ValueError:
        if (message.text=="/reset"):
            # устанавливаем значение переменной "total_price" в 0 для текущего пользователя
            current_state = await state.get_data()
            current_state["total_price"] = 0
            await state.set_data(current_state)

            # отправляем сообщение об успешном обнулении и возвращаемся в состояние ожидания ввода стоимости
            await message.answer("Сумма заказа успешно обнулена.")
            await message.answer("Введите стоимость товара в юанях")

            await Form.waiting_for_price.set()

        elif (message.text=="/start"):
            await Form.waiting_for_price.set()
            current_state = await state.get_data()
            current_state["total_price"] = 0
            await state.set_data(current_state)

            await message.answer("Здравствуйте, введите стоимость товара в юанях:")

        elif (message.text=="/delivery"):
            await Form.waiting_for_price.set()
            current_state = await state.get_data()
            await state.set_data(current_state)

            await message.answer("📦Примерная цена доставки: 1600 - 2400 за единицу товара.")

        elif (message.text=="/formula"):
            await Form.waiting_for_price.set()
            current_state = await state.get_data()
            await state.set_data(current_state)

            await message.answer("💰Формула -> ((цена в юанях + 18ю) * 1.05 * 11.85(курс юани к рублю)) + 1000(наша комиссия)")

        elif (message.text=="/link"):
            await Form.waiting_for_price.set()
            current_state = await state.get_data()
            await state.set_data(current_state)

            await message.answer("По поводу заказов писать: https://t.me/poizon_1 или https://t.me/honeymad_7")

        else:
            # если введенный текст нельзя преобразовать в число, отправляем сообщение об ошибке и возвращаемся в состояние ввода стоимости
            await message.answer("Пожалуйста, введите число")
        return

    # получаем текущее состояние пользователя из FSM
    current_state = await state.get_data()

    # получаем текущую стоимость из текущего состояния (если она есть) или устанавливаем ее в 0
    current_price = current_state.get("price", 0)

    # вычисляем новую стоимость товара и обновляем текущее состояние
    new_price = math.ceil(math.ceil((price+18)*1.05) * 11.85)+1000
    current_state["price"] = new_price

    # получаем текущую сумму заказа из текущего состояния (если она есть) или устанавливаем ее в 0
    total_price = current_state.get("total_price", 0)

    # вычисляем новую сумму заказа и обновляем текущее состояние
    total_price += new_price
    current_state["total_price"] = total_price

    # сохраняем текущее состояние FSM
    await state.set_data(current_state)

    # отправляем сообщение с новой стоимостью и общей суммой заказа
    await message.answer(f"Стоимость товара: {new_price} руб.\nОбщая сумма заказа: {total_price} руб.\nВведите следующую стоимость товара.")

if __name__ == '__main__':
    # запускаем бота
    executor.start_polling(dp, skip_updates=True)