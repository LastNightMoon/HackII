Для запуска бэкенда и и ИИ нужно

```bash
git clone https://github.com/LastNightMoon/HackII.git
cd HackII
nano .env
docker compose up
```
В файле .env должны быть прописаны
```
DBUSER = <Пользователь БД>
DBPASSWORD=<Пароль для Пользователь БД>
DBHOST=<Хост БД ip:port>
DBNAME=<Название БД>
RABBITMQ_URL=<amqp://login:pass@ip:5672/>
MINIO_PUB=<MINIO LOGIN>
MINIO_PRI=<MINIO PASSWORD>
MINIO_URL=<MINIO LINK>
```
Можно проверить распознавание и улучшение с помощью
[final_audio_pipeline.ipynb](final_audio_pipeline.ipynb)