from minio import Minio
from minio.error import S3Error
import os
# http://45.144.64.108:9002/browser - WEB UI
# Конфигурация MinIO
minio_endpoint = os.environ.get('MINIO_URL')  # Или "45.144.64.108:9000" для удаленного доступа
access_key = os.environ.get('MINIO_PUB')
secret_key = os.environ.get('MINIO_PRI')
bucket_name = "my-bucket"
secure = False  # False, если не используете HTTPS

# Инициализация клиента MinIO
client = Minio(
    minio_endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=secure
)


def create_bucket(bucket_name):
    """Создает бакет, если он еще не существует."""
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Бакет '{bucket_name}' успешно создан.")
        else:
            print(f"Бакет '{bucket_name}' уже существует.")
    except S3Error as err:
        print(f"Ошибка при создании бакета: {err}")


def upload_file(bucket_name, object_name, file_path):
    """Загружает файл в бакет."""
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        client.fput_object(bucket_name, object_name, file_path)
        print(f"Файл '{file_path}' успешно загружен как '{object_name}' в бакет '{bucket_name}'.")
    except S3Error as err:
        print(f"Ошибка при загрузке файла: {err}")
    except FileNotFoundError as err:
        print(err)


def download_file(bucket_name, object_name, file_path):
    """Скачивает файл из бакета."""
    try:
        client.fget_object(bucket_name, object_name, file_path)
        print(f"Файл '{object_name}' успешно скачан из бакета '{bucket_name}' в '{file_path}'.")
    except S3Error as err:
        print(f"Ошибка при скачивании файла: {err}")


def main():
    # Создаем бакет
    create_bucket(bucket_name)

    # Пример загрузки файла
    local_file = "example.txt"  # Локальный файл для загрузки
    object_name = "example.txt"  # Имя объекта в MinIO

    # Создаем тестовый файл, если его нет
    if not os.path.exists(local_file):
        with open(local_file, "w") as f:
            f.write("Это тестовый файл для MinIO!")
        print(f"Создан тестовый файл '{local_file}'.")

    # Загружаем файл в MinIO
    upload_file(bucket_name, object_name, local_file)

    # Пример скачивания файла
    downloaded_file = "downloaded_example.txt"
    download_file(bucket_name, object_name, downloaded_file)


if __name__ == "__main__":
    main()