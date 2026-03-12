import json
import urllib.request
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
import time
from functools import wraps


def timer(func):
    """
    Декоратор для измерения времени работы функций.

    :param func:Передаваемая функция.
    :return: Возвращает функцию wrapper, которая вернёт результат func.
    """

    # декоратор для сохранения метаданных передаваемой функции
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Функция {func.__name__} выполнялась {end_time - start_time:.4f} секунд")
        return result

    return wrapper


class ImageDownloader:
    def __init__(self, max_workers=2):
        self.max_workers: int = max_workers

    def _download_image(self, url: str, dir_path: str) -> None:
        try:
            # создаём объект реквеста и настраиваем юзер-агента
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0'
            })

            # Читаем данные из запроса, с таймаутом в 30 сек
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status >= 400:
                    raise Exception(f"HTTP error {response.status}")
                image_data = response.read()

            # создаём директорию для файла
            # exist_ok=True предотвращает ошибку, если директория уже существует
            os.makedirs(os.path.dirname(dir_path) or ".", exist_ok=True)

            # открываем файл на запись в бинарном режиме
            with open(dir_path, 'wb') as f:
                f.write(image_data)

        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")

    @timer
    def download_all(self, image_urls: list[str], dir_path: str = ".") -> tuple[int, int]:
        # создаём пул потоков для параллельной загрузки изображений
        # одновременно будет работать не больше max_workers потоков
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for url in image_urls:
                filename = f"{uuid.uuid4()}.jpg"
                target_path = os.path.join(dir_path, filename)
                # отправляем задачу в пул потоков
                # когда освободится поток, он выполнит функцию download_image
                executor.submit(self._download_image, url, target_path)


if __name__ == "__main__":
    with open("config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    ImageDownloader(config["max_workers"]).download_all(config["urls"], config["dir_path"])
