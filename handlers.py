from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import add_note, get_notes, delete_note
from datetime import datetime, timedelta

router = Router()


# Состояния FSM
class CreateNoteState(StatesGroup):
    set_title = State()
    set_description = State()
    set_timer = State()
    confirm_creation = State()


# Временное хранилище данных заметки
TEMP_NOTE = {}

# Главное меню (инлайн-кнопки)
main_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Добавить заметку", callback_data="add_note")],
        [InlineKeyboardButton(text="Мои задачи", callback_data="view_tasks")]
    ]
)

# Меню создания заметки
note_creation_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оглавление", callback_data="set_title")],
        [InlineKeyboardButton(text="Описание", callback_data="set_description")],
        [InlineKeyboardButton(text="Таймер", callback_data="set_timer")],
        [InlineKeyboardButton(text="Создать заметку", callback_data="create_note")]
    ]
)

# Меню управления задачей
task_details_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Задача выполнена", callback_data="task_done")],
        [InlineKeyboardButton(text="Удалить задачу", callback_data="delete_task")],
        [InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
)


# Команда /start
@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Я бот для заметок. Выбери действие:", reply_markup=main_menu_inline)


# Обработчик кнопки "Добавить заметку"
@router.callback_query(lambda c: c.data == "add_note")
async def start_note_creation(callback_query: CallbackQuery, state: FSMContext):
    TEMP_NOTE[callback_query.from_user.id] = {"title": "", "description": "", "timer": None}
    message_to_edit = await callback_query.message.edit_text(
        "Выберите, что хотите добавить в заметку:", reply_markup=note_creation_menu
    )
    await state.update_data(message_id=message_to_edit.message_id)
    await state.set_state(CreateNoteState.set_title)


# Оглавление заметки
@router.callback_query(lambda c: c.data == "set_title")
async def set_title(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите оглавление заметки:")
    await state.set_state(CreateNoteState.set_title)


@router.message(CreateNoteState.set_title)
async def save_title(message: Message, state: FSMContext):
    TEMP_NOTE[message.from_user.id]["title"] = message.text
    data = await state.get_data()
    message_id = data.get("message_id")
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text=f"Оглавление сохранено: {message.text}\n\nВыберите следующее действие:",
        reply_markup=note_creation_menu
    )
    await state.set_state(CreateNoteState.set_description)


# Описание заметки
@router.callback_query(lambda c: c.data == "set_description")
async def set_description(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите описание заметки:")
    await state.set_state(CreateNoteState.set_description)


@router.message(CreateNoteState.set_description)
async def save_description(message: Message, state: FSMContext):
    TEMP_NOTE[message.from_user.id]["description"] = message.text
    data = await state.get_data()
    message_id = data.get("message_id")
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text=f"Описание сохранено: {message.text}\n\nВыберите следующее действие:",
        reply_markup=note_creation_menu
    )
    await state.set_state(CreateNoteState.set_timer)


# Таймер
@router.callback_query(lambda c: c.data == "set_timer")
async def set_timer(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите время (в минутах) до конца задачи:")
    await state.set_state(CreateNoteState.set_timer)


@router.message(CreateNoteState.set_timer)
async def save_timer(message: Message, state: FSMContext):
    try:
        minutes = int(message.text)
        timer_end = datetime.now() + timedelta(minutes=minutes)
        TEMP_NOTE[message.from_user.id]["timer"] = timer_end.strftime("%Y-%m-%d %H:%M:%S")
        TEMP_NOTE[message.from_user.id]["initial_minutes"] = minutes
        data = await state.get_data()
        message_id = data.get("message_id")
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text=f"Таймер установлен на {minutes} минут.\n\nВыберите следующее действие:",
            reply_markup=note_creation_menu
        )
        await state.set_state(CreateNoteState.confirm_creation)
    except ValueError:
        await message.answer("Пожалуйста, введите число в минутах.")


# Завершение создания заметки
@router.callback_query(lambda c: c.data == "create_note")
async def create_note(callback_query: CallbackQuery, state: FSMContext):
    note = TEMP_NOTE.pop(callback_query.from_user.id, None)
    if note:
        title = note["title"]
        description = note["description"]
        timer = note["timer"]
        initial_minutes = note.get("initial_minutes", "Не указано")
        content = (
            f"{title}\n{description}\n"
            f"Таймер: {timer}\n"
            f"Изначальное время: {initial_minutes} минут"
        )
        add_note(user_id=callback_query.from_user.id, content=content)

        # Инлайн-кнопка для возвращения в главное меню
        back_to_menu_button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
            ]
        )

        await callback_query.message.edit_text(
            "Заметка успешно создана!",
            reply_markup=back_to_menu_button
        )
        await state.clear()


        await callback_query.message.edit_text(
            "Заметка успешно создана!",
            reply_markup=completion_menu
        )
        await state.clear()


@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Выберите действие:", reply_markup=main_menu_inline)


# Просмотр задач
@router.callback_query(lambda c: c.data == "view_tasks")
async def view_tasks_command(callback_query: CallbackQuery):
    notes = get_notes(user_id=callback_query.from_user.id)
    if not notes:
        await callback_query.message.edit_text("У вас нет задач.", reply_markup=main_menu_inline)
    else:
        task_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=content.split("\n")[0], callback_data=f"view_task:{note_id}")]
                for note_id, content in notes
            ]
        )
        await callback_query.message.edit_text("Ваши задачи:", reply_markup=task_keyboard)


# Детали задачи
@router.callback_query(lambda c: c.data.startswith("view_task:"))
async def handle_task_details(callback_query: CallbackQuery):
    note_id = int(callback_query.data.split(":")[1])
    notes = get_notes(callback_query.from_user.id)
    note = next((content for nid, content in notes if nid == note_id), None)

    if note:
        title, *details = note.split("\n")
        description = "\n".join(detail for detail in details if
                                not detail.startswith("Таймер:") and not detail.startswith("Изначальное время:"))

        initial_minutes = "Не указано"
        remaining_minutes = "Не указано"

        for detail in details:
            if detail.startswith("Изначальное время:"):
                initial_minutes = detail.split("Изначальное время:")[1].strip().split()[0]
            if detail.startswith("Таймер:"):
                timer_data = detail.split("Таймер:")[1].strip()
                try:
                    timer_datetime = datetime.strptime(timer_data, "%Y-%m-%d %H:%M:%S")
                    delta = timer_datetime - datetime.now()
                    remaining_minutes = max(0, int(delta.total_seconds() // 60))
                except ValueError:
                    remaining_minutes = "Ошибка в данных таймера"

        message_text = (
            f"**{title}**\n\n"
            f"Описание:\n{description}\n\n"
            f"Изначальное время таймера:\n{initial_minutes} минут\n"
            f"Осталось времени:\n{remaining_minutes} минут"
        )
        await callback_query.message.edit_text(
            message_text,
            reply_markup=task_details_menu
        )
    else:
        await callback_query.message.edit_text(
            "Ошибка: Задача не найдена.",
            reply_markup=main_menu_inline
        )


@router.callback_query(lambda c: c.data == "task_done")
async def mark_task_done(callback_query: CallbackQuery):
    # Извлечение ID задачи из callback_data
    try:
        note_id = int(callback_query.message.reply_markup.inline_keyboard[0][0].callback_data.split(":")[1])
        # Удаление задачи из базы данных
        delete_note(note_id)
        # Уведомление об успешном выполнении
        await callback_query.message.edit_text("Задача выполнена и удалена из базы данных.", reply_markup=None)
    except Exception as e:
        await callback_query.message.edit_text(f"Ошибка при выполнении задачи: {e}", reply_markup=None)


@router.callback_query(lambda c: c.data == "delete_task")
async def delete_task(callback_query: CallbackQuery):
    # Извлечение ID задачи из callback_data
    try:
        note_id = int(callback_query.message.reply_markup.inline_keyboard[0][0].callback_data.split(":")[1])
        # Удаление задачи из базы данных
        delete_note(note_id)
        # Уведомление об успешном удалении
        await callback_query.message.edit_text("Задача успешно удалена из базы данных.", reply_markup=None)
    except Exception as e:
        await callback_query.message.edit_text(f"Ошибка при удалении задачи: {e}", reply_markup=None)
