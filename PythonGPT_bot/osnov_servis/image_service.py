from openai import OpenAI
import base64
import io
from PIL import Image

class ImageGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    async def create_images(self, prompt: str) -> bytes:
        try:
            # Генерируем изображение
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            # Получаем URL изображения
            image_url = response.data[0].url

            # Скачиваем изображение
            import requests
            response = requests.get(image_url)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"Failed to download image: {response.status_code}")

        except Exception as e:
            print(f"Error in image generation: {e}")
            raise 