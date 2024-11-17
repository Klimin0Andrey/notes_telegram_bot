from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить заметку")],
        [KeyboardButton(text="Мои задачи")],
    ],
    resize_keyboard=True,
)

# Меню создания заметки
note_creation_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оглавление", callback_data="set_title")],
        [InlineKeyboardButton(text="Описание", callback_data="set_description")],
        [InlineKeyboardButton(text="Таймер", callback_data="set_timer")],
        [InlineKeyboardButton(text="Создать заметку", callback_data="create_note")],
    ]
)

# Меню управления задачей

def create_task_details_menu(note_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Задача выполнена", callback_data=f"task_done:{note_id}")],
            [InlineKeyboardButton(text="Удалить задачу", callback_data=f"delete_task:{note_id}")],
            [InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
        ]
    )
