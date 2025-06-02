import openai
import requests
from io import BytesIO
import httpx

class ImageGenerationService:
    def __init__(self, api_key):
        self.api_key = api_key
        proxies = {
            "http://": "http://18.199.183.77:49232",
            "https://": "http://18.199.183.77:49232"
        }
        self.client = openai.OpenAI(
            http_client=httpx.Client(transport=httpx.HTTPTransport(proxy=proxies["http://"])),
            api_key=api_key
        )

    async def create_images(self, prompt):
        # Отправляем запрос к DALL-E
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # Получаем URL сгенерированного изображения
        image_url = response.data[0].url

        # Загружаем изображение по URL
        image_response = requests.get(image_url)
        image_bytes = BytesIO(image_response.content).getvalue()

        return image_bytes


class ImageGenerator:
    pass