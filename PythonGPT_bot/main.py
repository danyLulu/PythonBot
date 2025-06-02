from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import openai
from util import *
import os
from gpt_service.gpt import gpt, gpt_dialog
from osnov_servis.random_facts import get_random_fact
from util import load_prompt, show_main_menu
from osnov_servis.talk import talk, talk_dialog, load_character_prompt
from osnov_servis.shared import dialog, chatgpt
from osnov_servis.image_service import ImageGenerator
from telegram import InputMediaPhoto


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
        "images": "генирация картинок "
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
    await send_text(update, context, f"📚 Интересный факт:\n\n{fact}")


async def handle_images(update, context):
    dialog.mode = "images"
    try:
        text = load_message("images")
    except FileNotFoundError:
        text = "Напишите, какую картинку вы хотите сгенерировать. Например: 'Кот в космосе' или 'Город будущего'"
    await send_text(update, context, text)


async def images_dialog(update, context):
    if dialog.mode != "images":
        return

    prompt = update.message.text
    my_message = await send_text(update, context, "🎨 Генерирую картинку... Это может занять несколько секунд.")

    try:
        # Отправляем промпт модели генерации изображений
        image_bytes = await image_generator.create_images(prompt)
        await my_message.delete()  # Удаляем сообщение "Генерирую..."

        # Отправляем сгенерированное изображение
        await update.message.reply_photo(
            photo=image_bytes,
            caption=f"🎨 Картинка по запросу: {prompt}"
        )
    except Exception as e:
        print(f"Error generating image: {e}")
        await my_message.edit_text(
            "😔 Извините, произошла ошибка при генерации изображения. Попробуйте еще раз или измените описание.")


# Инициализируем генератор изображений
image_generator = ImageGenerator(
    api_key=os.getenv("CHATGPT_TOKEN")
)

application = Application.builder().token(os.getenv("TG_BOT_TOKEN")).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("gpt", gpt))
application.add_handler(CommandHandler("talk", talk))
application.add_handler(CommandHandler("fact", random_fact))
application.add_handler(CommandHandler("images", handle_images))

# Добавляем обработчики для диалогов
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, talk_dialog))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, images_dialog))

application.add_handler(CallbackQueryHandler(talk_button, pattern="^talk_.*"))
application.run_polling()

