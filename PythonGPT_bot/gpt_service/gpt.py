from util import send_photo, send_text, load_message, load_prompt
from osnov_servis.shared import dialog, chatgpt
import logging

logger = logging.getLogger(__name__)

WAITING_FOR_MESSAGE = 1

async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_photo(update, context, "gpt")
    await send_text(update, context, text)
    # Устанавливаем промпт для GPT
    chatgpt.set_prompt(load_prompt("gpt"))

async def gpt_dialog(update, context):
    if dialog.mode != "gpt":
        return
        
    text = update.message.text
    
    # Показываем сообщение о генерации
    my_message = await send_text(update, context,
                                "ChatGPT генерирует информацию. Это может занять несколько секунд...")
    
    try:
        # Получаем ответ от GPT
        answer = await chatgpt.add_message(text)
        await my_message.edit_text(answer)
    except Exception as e:
        logger.error(f"Error in GPT dialog: {e}")
        await my_message.edit_text("Извините, произошла ошибка при генерации ответа. Попробуйте еще раз.")







