from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Данные о темах квиза
QUIZ_TOPICS = {
    'programming': {
        'name': 'Программирование',
        'emoji': '💻',
        'prompt': 'Создай вопрос о программировании, языках программирования или технологиях. Вопрос должен быть с вариантами ответов A, B, C, D. В конце укажи правильный ответ.'
    },
    'history': {
        'name': 'История',
        'emoji': '🏛️',
        'prompt': 'Создай вопрос по истории, историческим событиям или личностям. Вопрос должен быть с вариантами ответов A, B, C, D. В конце укажи правильный ответ.'
    },
    'science': {
        'name': 'Наука',
        'emoji': '🔬',
        'prompt': 'Создай вопрос по физике, химии или биологии. Вопрос должен быть с вариантами ответов A, B, C, D. В конце укажи правильный ответ.'
    },
    'geography': {
        'name': 'География',
        'emoji': '🌍',
        'prompt': 'Создай вопрос по географии, странам, столицам или природе. Вопрос должен быть с вариантами ответов A, B, C, D. В конце укажи правильный ответ.'
    },
    'movies': {
        'name': 'Кино',
        'emoji': '🎬',
        'prompt': 'Создай вопрос о фильмах, актерах или кинематографе. Вопрос должен быть с вариантами ответов A, B, C, D. В конце укажи правильный ответ.'
    }
}

def get_quiz_topics_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с темами квиза"""
    keyboard = []
    for topic_key, topic_data in QUIZ_TOPICS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{topic_data['emoji']} {topic_data['name']}",
                callback_data=f"quiz_topic_{topic_key}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)

def get_quiz_topic_data(topic_key: str) -> dict:
    """Возвращает данные о теме квиза"""
    return QUIZ_TOPICS.get(topic_key)

def get_quiz_continue_keyboard(topic_key: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру для продолжения квиза"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Следующий вопрос", callback_data=f"quiz_continue_{topic_key}"),
            InlineKeyboardButton("🔄 Сменить тему", callback_data="quiz_change_topic")
        ],
        [InlineKeyboardButton("🏁 Завершить квиз", callback_data="quiz_finish")]
    ]
    return InlineKeyboardMarkup(keyboard) 