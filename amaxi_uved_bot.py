from config import TOKEN, DICT_EMPLOYEE
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from datetime import datetime
from work_with_api import create_ship
# from work_with_api import change_status_pos  # TODO Статусы пока не меняем


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.callback_query_handler(Text(startswith="start_assembly"))
async def callbacks(call: types.CallbackQuery) -> None:
    """
    При нажатии на кнопку "🔴 Начать сборку" (callback_data="start_assembly*") заменяем ИнЛайн клавиатуру.
    Выводим две кнопки в ряд:
        "🟢 Начать" - callback_data=f"start_ass_{time_create_order}",
        "🔴 Отмена" - callback_data=f"cancel_ass_{time_create_order}",
        где time_create_order это время создания заказа в формате HH:MM.
        time_create_order берём из полученного callback_data кнопки "🔴 Начать сборку", после второго знака "_".
    Пример получаемого callback_data="start_assembly_13:39".
    Пример формируемого callback_data="cancel_ass_13:39".
    """
    time_create_order: str = call.data.split('_')[2]
    buttons = [
        types.InlineKeyboardButton(text="🟢 Начать", callback_data=f"start_ass_{time_create_order}"),
        types.InlineKeyboardButton(text="🔴 Отмена", callback_data=f"cancel_ass_{time_create_order}")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith="cancel_ass"))
async def callbacks(call: types.CallbackQuery) -> None:
    """
    При нажатии на кнопку "🔴 Отмена" (callback_data="cancel_ass*") заменяем ИнЛайн клавиатуру на исходную.
    Возвращаем(выводим) кнопку "🔴 Начать сборку" - callback_data=f"start_assembly_{time_create_order}, как и в
    исходном сообщении, где time_create_order это время создания заказа в формате HH:MM.
    time_create_order берём из полученного callback_data кнопки "🔴 Отмена", после второго знака "_".
    Пример получаемого callback_data="cancel_ass_13:39".
    Пример формируемого callback_data="start_assembly_13:39".
    """
    time_create_order: str = call.data.split('_')[2]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="🔴 Начать сборку",
                                            callback_data=f"start_assembly_{time_create_order}"))
    await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith="start_ass"))
async def callbacks(call: types.CallbackQuery):
    """
    При нажатии на кнопку "🟢 Начать" (callback_data="start_ass*"):
    Переводим на платформе abcp все позиции заказа в статус "Готов к выдаче"
    Если позиции перевелись без ошибок, то:
        Получаем время последнего редактирования сообщения из call.message.edit_date в формате HH:MM:SS
        Добавляем это время к тексту сообщения в формате HH:MM
        Заменяем клавиатуру ИнЛайн клавиатуру и выводим одну кнопку:
            "🟡 Завершить сборку (С: {merch_name})", где merch_name - имя сборщика,
            callback_data=stop_assembly_{time_create_order}_{time_trans_ass_order}, где
                time_create_order - время создания заказа в формате HH:MM
                time_trans_ass_order - время нажатия на кнопку "🟢 Начать" в формате HH:MM:SS
        time_create_order берём из полученного callback_data кнопки "🟢 Начать", после второго знака "_".

        Пример получаемого callback_data="start_ass_13:39".
        Пример формируемого callback_data="stop_assembly_13:39_13:41:12".
    Если при изменении статуса позиций возникла ошибка, то:
        Заменяем клавиатуру ИнЛайн клавиатуру и выводим одну кнопку:
            "⚠️Ошибка - требует обработки"
            callback_data="pass".
    """
    print(call)
    # Меняем статус позиций в заказе на “готов к выдаче”
    order_number = call.message.text.split(' ')[1]
    print(f'Отрабатывается заказ №{order_number}')
    # result = await change_status_pos(order_number)  # TODO Пока не используем перевод статуса заказа
    result = True  # TODO Удалить, если начнём использовать перевод статусов заказа
    print(result)

    # Получаем данные по времени из data
    time_create_order: str = call.data.split('_')[2]
    time_trans_ass_order = call.message.edit_date.strftime("%H:%M:%S")
    message_text = call.message.text
    merch_name = DICT_EMPLOYEE[call.from_user.id]

    if result:
        # Дополняем текст сообщения
        message_text = call.message.text + f'      C: {time_trans_ass_order[:5]}'

        # Добавляем клавиатуру
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f"🟡 Завершить сборку (С: {merch_name})",
            callback_data=f"stop_assembly_{time_create_order}_{time_trans_ass_order}_{call.from_user.id}"
        ))
    else:
        # Добавляем только клавиатуру. Текст сообщения не меняем.
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f"⚠️Ошибка - требует обработки",
            callback_data="pass"
        ))
    await call.message.edit_text(message_text, entities=call.message.entities, reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith="stop_assembly"))
async def callbacks(call: types.CallbackQuery) -> None:
    """
    При нажатии на кнопку "🟡 Завершить сборку (С: {merch_name})" (callback_data="stop_assembly*"):
    Если кнопку нажал тот же пользователь, что и переводил статус сообщения в "Завершить сборку".
    Заменяем эту кнопку на две кнопки в ряд:
        "🟢 Завершить" - callback_data=f"stop_assembl_yes_{time}",
        "🔴 Отмена" - callback_data=f"stop_assembl_no_{time}",
    где time это время создания заказа в формате HH:MM и время начала сборки в формате HH:MM:SS через знак "_".
    Данные времени берём из полученного callback_data кнопки "🟡 Завершить сборку (С: {merch_name})",
    после второго и третьего знака "_".
    Пример получаемого callback_data="stop_assembly_13:39_13:41:12".
    Пример формируемого callback_data="stop_assembl_no_13:39_13:41:12".
    """
    split_call = call.data.split('_')
    time = split_call[2] + '_' + split_call[3]
    correct_user = split_call[4]

    if call.from_user.id != int(correct_user):
        await call.answer("Вы не можете завершить сборку этого заказа!", show_alert=True)
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="🟢 Завершить", callback_data=f"stop_assembl_yes_{time}"),
        types.InlineKeyboardButton(text="🔴 Отмена", callback_data=f"stop_assembl_no_{time}")
    ]
    keyboard.add(*buttons)
    await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith="stop_assembl_no"))
async def callbacks(call: types.CallbackQuery) -> None:
    """
    При нажатии на кнопку "🔴 Отмена" (callback_data="stop_assembl_no*") заменяем ИнЛайн клавиатуру.
    Заменяем клавиатуру ИнЛайн клавиатуру и выводим одну кнопку:
        "🟡 Завершить сборку (С: {merch_name})", где merch_name - имя сборщика,
        callback_data=stop_assembly_{time_create_order}_{time_trans_ass_order}, где
        time_create_order - время создания заказа в формате HH:MM
        time_trans_ass_order - время нажатия на кнопку "🟢 Начать" в формате HH:MM:SS
    time_create_order и time_trans_ass_order берём из полученного callback_data кнопки "🔴 Отмена",
    после второго и третьего знака "_".

    Пример получаемого callback_data="stop_assembl_no_13:39_13:41:12".
    Пример формируемого callback_data="stop_assembly_13:39_13:41:12".
    """
    time = call.data.split('_')
    time = time[3] + '_' + time[4]
    merch_name = DICT_EMPLOYEE[call.from_user.id]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text=f"🟡 Завершить сборку (С: {merch_name})", callback_data=f"stop_assembly_{time}_{call.from_user.id}"
        )
    )
    await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith="stop_assembl_yes"))
async def callbacks(call: types.CallbackQuery):
    """
    При нажатии на кнопку "🟢 Завершить" (callback_data="stop_assembl_yes*") заменяем ИнЛайн клавиатуру
    и выводим одну кнопку:
        "Собран за {time_assem} мин (С: {merch_name})", где
            merch_name - имя сборщика,
            time_assem - время потраченное на сборку, которое мы получаем в результате разницы между временем взятия
            на сборку из полученного call_data после третьего знака "_" и временем последнего редактирования сообщения
            из call.message.edit_date в формате HH:MM:SS,
    callback_data="pass".
    Добавляем к сообщению время окончанию сборки в формате HH:MM, которое получаем из времени
    последнего редактирования сообщения.
    """
    # Создаём отгрузку по заказу
    order_number = call.message.text.split(' ')[1]
    print(f'Отгружаем позиции по заказ №{order_number}')
    result = await create_ship(order_number)

    merch_name = DICT_EMPLOYEE[call.from_user.id]

    time_finish_ass_order = call.message.edit_date
    date = call.data.split('_')[4]
    time_assem = round((time_finish_ass_order - datetime.strptime(date, '%H:%M:%S')).seconds / 60, 1)

    message_text = call.message.text
    if result:
        # Дополняем текст сообщения
        message_text = call.message.text + f'      В: {time_finish_ass_order.strftime("%H:%M")}'
        # Добавляем клавиатуру
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f"🟢 Собран за {time_assem} мин ({merch_name})",
            callback_data="pass"
        ))
    else:
        # Добавляем только клавиатуру. Текст сообщения не меняем.
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f"⚠️Ошибка - требует обработки",
            callback_data="pass"
        ))
    await call.message.edit_text(message_text, entities=call.message.entities, reply_markup=keyboard)


@dp.callback_query_handler(text="pass")
async def callbacks(call: types.CallbackQuery):
    """
    Если сотрудник нажимает на кнопку с информацией о времени сборки, то выдаём сообщение, что действия завершены.
    """
    await call.answer('По этому заказу все действия завершены.', show_alert=True)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp)

