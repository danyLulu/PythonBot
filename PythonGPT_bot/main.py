from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import openai
import os
from dotenv import load_dotenv
from util import (
    send_photo, send_text, load_message, load_prompt,
    show_main_menu, Dialog
)
from gpt_service.gpt import gpt, gpt_dialog
from osnov_servis.random_facts import get_random_fact
from osnov_servis.talk import talk, talk_dialog, load_character_prompt
from osnov_servis.shared import dialog, chatgpt
from osnov_servis.image_service import ImageGenerationService
from osnov_servis.quiz import (
    quiz_command, quiz_start, topic_selected,
    handle_quiz_answer, handle_quiz_callback,
    SELECTING_TOPIC, ANSWERING_QUESTION
)
from telegram import InputMediaPhoto

# Загружаем переменные окружения
load_dotenv()

# Проверяем наличие необходимых переменных окружения
required_env_vars = ["TG_BOT_TOKEN", "CHATGPT_TOKEN"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Отсутствуют необходимые переменные окружения: {', '.join(missing_vars)}")

# Инициализируем генератор изображений
try:
    image_generator = ImageGenerationService(
        api_key=os.getenv("CHATGPT_TOKEN")
    )
except Exception as e:
    raise RuntimeError(f"Ошибка при инициализации генератора изображений: {e}")

# Инициализируем приложение Telegram
try:
    application = Application.builder().token(os.getenv("TG_BOT_TOKEN")).build()
except Exception as e:
    raise RuntimeError(f"Ошибка при инициализации Telegram бота: {e}")

async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        "start": "главное меню бота",
        "gpt": "задать вопрос чату GPT 🧠",
        "talk": "переписка со звездами 😈",
        "fact": "рандомный факт",
        "images": "генирация картинок",
        "quiz": "проверь свои знания 🎯"
    })


async def talk_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_text(update, context, "отличный выбор! Можете начать общаться!")

    # Загружаем промпт для выбранного персонажа
    prompt = load_character_prompt(query)
    chatgpt.set_prompt(prompt)


async def random_fact(update, context):
    fact = get_random_fact()
    await send_photo(update,context, "facts")
    await send_text(update, context, f"📚 Интересный факт:\n\n{fact}")



async def images(update, context):

    dialog.mode = "images"
    await send_photo(update, context, "images")
    try:
        text = load_message("images")
    except FileNotFoundError:
        text = "Напишите, какую картинку вы хотите сгенерировать." # Текст по умолчанию
    # Убрал отправку фото здесь
    # await send_photo(update, context, "generate_image")
    await send_text(update, context, text)


async def images_dialog(update, context):
    prompt = update.message.text
    my_message = await send_text(update, context, "Генерирую картинку...")

    # Отправляем промпт модели генерации изображений
    image_bytes = await image_generator.create_images(prompt)
    await my_message.delete() # Удаляем сообщение "Генерирую..."

    # Отправляем сгенерированное изображение
    await update.message.reply_photo(photo=image_bytes, caption=f"Картинка по запросу: {prompt}")


# Добавляем обработчики для квиза
quiz_handler = ConversationHandler(
    entry_points=[
        CommandHandler('quiz', quiz_command),
        CallbackQueryHandler(quiz_start, pattern='^quiz_interface$')
    ],
    states={
        SELECTING_TOPIC: [
            CallbackQueryHandler(topic_selected, pattern=r'^quiz_topic_'),
            CallbackQueryHandler(handle_quiz_callback, pattern=r'^quiz_')
        ],
        ANSWERING_QUESTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_answer),
            CallbackQueryHandler(handle_quiz_callback, pattern=r'^quiz_')
        ]
    },
    fallbacks=[
        CommandHandler('quiz', quiz_command),
        CallbackQueryHandler(quiz_start, pattern='^quiz_interface$')
    ],
    per_chat=True,
    name="quiz_conversation"
)

# Добавляем обработчики в правильном порядке
application.add_handler(quiz_handler)  # Сначала добавляем ConversationHandler
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("gpt", gpt))
application.add_handler(CommandHandler("talk", talk))
application.add_handler(CommandHandler("fact", random_fact))
application.add_handler(CommandHandler("images", images))
application.add_handler(CommandHandler("quiz", quiz_command))
# Добавляем обработчики для диалогов
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, talk_dialog))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, images_dialog))

application.add_handler(CallbackQueryHandler(talk_button, pattern="^talk_.*"))
application.run_polling()

