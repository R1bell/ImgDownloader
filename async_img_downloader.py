import json
import os
import uuid
import asyncio
import aiohttp
import aiofiles
import time
from functools import wraps


def async_timer(func):
    """
    Декоратор для измерения времени работы функций.

    :param func:Передаваемая функция.
    :return: Возвращает функцию wrapper, которая вернёт результат func.
    """

    # декоратор для сохранения метаданных передаваемой функции
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"Асинхронная функция {func.__name__} выполнялась "
              f"{end_time - start_time:.4f} секунд"
              )
        return result

    return wrapper


class AsyncImageDownloader:
    def __init__(self, max_workers=2):
        # максимальное количество одновременных соединений
        self.max_workers: int = max_workers

    async def _download_image(self,
                              session: aiohttp.ClientSession,
                              url: str,
                              save_path: str
                              ) -> None:

        try:
            # отправляем запрос с пользовательским User-Agent
            # и ожидаем ответ от сервера
            async with session.get(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=30
            ) as response:

                # если сервер вернул ошибку (например 404),
                # будет выброшено исключение
                response.raise_for_status()

                # читаем данные из ответа
                image_data = await response.read()

            # создаём директорию для файла
            # exist_ok=True чтобы не было ошибок, если директория существует
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

            # открываем файл на запись в бинарном режиме (асинхронно)
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(image_data)

        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")

    @async_timer
    async def download_all(
            self,
            image_urls: list[str],
            dir_path: str = "."
    ) -> None:

        # создаём коннектор, который ограничивает количество
        # одновременных соединений
        connector = aiohttp.TCPConnector(limit=self.max_workers)

        # создаём асинхронную сессию для выполнения всех запросов
        async with aiohttp.ClientSession(connector=connector) as session:
            # создаём таски для запросов и заполняем список tasks
            tasks = [
                asyncio.create_task(
                    self._download_image(session, url, os.path.join(dir_path, f"{uuid.uuid4()}.jpg"))
                )
                for url in image_urls
            ]

            # ожидаем завершения всех задач
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    asyncio.run(
        AsyncImageDownloader(config["max_workers"]).download_all(
            config["urls"],
            config["dir_path"]
        )
    )
