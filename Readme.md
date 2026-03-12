# ImgDownload

- **Многопоточная версия** (на базе `threading` и `concurrent.futures`)
- **Асинхронная версия** (на базе `asyncio`, `aiohttp`, `aiofiles`)

## Требования

- Python 3.12+

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/R1bell/ImgDownloader.git
cd ImgDownloader

# Установка всех зависимостей
pip install -r requirements.txt
```

## Измените config.json при желании
```json
{
    "max_workers": 2,
    "urls": [
        "https://picsum.photos/400/300?random=1",
        "https://picsum.photos/400/300?random=2"
    ],
    "dir_path": "downloaded_images"
}
```

## Запуск
### Multithreading downloader
`python img_downloader.py`
### Async downloader
`python async_img_downloader.py`