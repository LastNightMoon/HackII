import io
import os
import uuid
from typing import List

import sqlalchemy
import uvicorn
from fastapi import Depends
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from DataBaseManager import Category, MusicQueue
from DataBaseManager import MusicMeta
from DataBaseManager.minio_manager import minio_manager
from api.models import AudioFilterRequest, AudioBaseInfo
from api.models import CategoryFilter, AudioFullInfo
from utils.generate_sql_stmz import pipeline_sql, select_music_by_id

app = FastAPI(title="Голос Победы API", description="API для работы с архивом военных песен")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/get_audio_list", response_model=List[AudioBaseInfo])
async def get_audio_list():
    # try:
    query = sqlalchemy.select(MusicMeta)
    queries: list[MusicMeta] = pipeline_sql(query, MusicMeta)
    print(queries)
    return [{
        "id": q.music_id,
        "name": q.name,
        "author": getattr(q, 'author', None),
        "url": f"/get_audio_file/{q.music_id}"
    } for q in queries]
    # except Exception as e:
    #     raise HTTPException(500, str(e))


@app.get("/get_audio_info/{file_id}", response_model=AudioFullInfo)
async def get_audio_info(file_id: int):
    query: MusicMeta = select_music_by_id(file_id)
    if not query:
        raise HTTPException(404, "Запись не найдена")

    return {
        "id": query.music_id,
        "name": query.name,
        "author": getattr(query, 'Author', ''),
        "music_category":
            pipeline_sql(sqlalchemy.select(Category).filter_by(category_id=query.music_category), Category)[0].label,
        "text": query.text_music,
        "url": f"/get_audio_file/{query.music_id}"
    }


@app.get("/get_category_list", response_model=List[CategoryFilter])
async def get_category_list():
    try:
        queries: list[Category] = pipeline_sql(sqlalchemy.select(Category), Category)
        return [{
            "id": q.category_id,
            "name": q.label
        } for q in queries]
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/filter_music_list", response_model=List[AudioBaseInfo])
async def filter_music_list(filter: AudioFilterRequest):
    filters = []
    if filter.music_category:
        filters.append(MusicMeta.music_category.in_(filter.music_category))

    if filter.text:
        query = sqlalchemy.select(MusicMeta).where(*filters, MusicMeta.name.ilike(f"%{filter.text}%"))
        results = pipeline_sql(query, MusicMeta)
        if results:
            return [
                AudioBaseInfo(
                    id=r.music_id,
                    name=r.name,
                    author=getattr(r, "author", None),
                    url=f"/get_audio_file/{r.music_id}"
                ) for r in results
            ]

    if filter.text and hasattr(MusicMeta, "author"):
        query = select(MusicMeta).where(*filters, MusicMeta.author.ilike(f"%{filter.text}%"))
        results = pipeline_sql(query, MusicMeta)
        if results:
            return [
                AudioBaseInfo(
                    id=r.music_id,
                    name=r.name,
                    author=getattr(r, "author", None),
                    url=f"/get_audio_file/{r.music_id}"
                ) for r in results
            ]

    if filter.text:
        query_text = filter.text.replace("'", "''")  # Escape single quotes for SQL safety
        categories_clause = ""
        if filter.music_category:
            # Format categories as a PostgreSQL array literal, escaping values
            categories = [str(cat) for cat in filter.music_category]
            categories_clause = f"music_category = ANY(ARRAY[{', '.join(categories)}]) AND "

        # Build the SQL query with embedded parameters
        sql = f"""
                        SELECT * FROM music_meta
                        WHERE {categories_clause}search_vector @@ plainto_tsquery('russian', '{query_text}')
                    """

        # Pass only the query to pipeline_sql
        results = pipeline_sql(sql, table=MusicMeta)
        return [
            AudioBaseInfo(
                id=r.music_id,
                name=r.name,
                author=getattr(r, "author", None),
                url=f"/get_audio_file/{r.music_id}"
            ) for r in results
        ]

    return []


@app.get("/get_audio_file/{file_id}")
async def get_audio_file(file_id: int):
    query = select_music_by_id(file_id)
    if not query or not query.url:
        raise HTTPException(404, "Файл не найден")

    try:
        file_data = minio_manager.download_file("music", query.url)
        if not file_data:
            raise HTTPException(500, "Файл не найден или пустой")
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f'attachment; filename=\"{query.url}\"'}
        )
    except Exception as e:
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")


# @app.post("/upload_audio")
# async def upload_audio(file: UploadFile = File(...)):
#     if not file.filename.endswith(('.mp3', '.wav')):
#         raise HTTPException(400, "Только MP3/WAV файлы")
#
#     try:
#         file_id = str(uuid.uuid4())
#         file_ext = os.path.splitext(file.filename)[1]
#         file_name = f"{file_id}{file_ext}"
#
#         file_content = await file.read()
#         minio_manager.upload_file("music", file_content, file_name)
#         with db.get_session() as session:
#             session.execute(sqlalchemy.insert(MusicMeta).
#                             values(name=file.filename,
#                                    url=file_name, music_category=0))
#             session.commit()
#             new_record = db.select(MusicMeta, {"url": file_name})[0]
#
#         return JSONResponse({
#             "status": "success",
#             "file_id": new_record.music_id,
#             "url": f"/get_audio_file/{new_record.music_id}"
#         }, status_code=201)
#
#     except Exception as e:
#         raise HTTPException(500, f"Ошибка загрузки: {str(e)}")

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp3', '.wav')):
        raise HTTPException(400, "Только MP3/WAV файлы")

    try:
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{file_id}{file_ext}"

        file_content = await file.read()
        minio_manager.upload_file("music", file_content, file_name)
        new_record = \
            pipeline_sql(sqlalchemy.insert(MusicQueue).values(url=file_name).returning(MusicQueue), MusicQueue)[0]

        return JSONResponse({
            "status": "success",
            "file_id": new_record.id,
            "url": f"/get_audio_file/{new_record.id}"
        }, status_code=201)

    except Exception as e:
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")


@app.delete("/delete_audio")
async def delete_audio(audio_id: int):
    query = pipeline_sql(sqlalchemy.select(MusicMeta).filter_by(music_id=audio_id), MusicMeta)
    if not query:
        raise HTTPException(status_code=404, detail="Аудиозапись не найдена")

    if query.url:
        try:
            minio_manager.delete_file("music", query.url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении файла: {str(e)}")
    pipeline_sql(sqlalchemy.delete(MusicMeta).filter_by(music_id=audio_id), MusicMeta)


@app.get("/moderation_queue", response_model=List[AudioBaseInfo])
async def moderation_queue():
    queue = pipeline_sql(sqlalchemy.select(MusicQueue), MusicQueue)
    result = []
    for item in queue:
        result.append(AudioBaseInfo(
            id=item.id,
            name=item.url,
            author=None,
            url=f"/get_queue_audio_file/{item.id}"
        ))
    return result


@app.get("/get_queue_audio_file/{queue_id}")
async def get_queue_audio_file(queue_id: int):
    record = pipeline_sql(sqlalchemy.select(MusicQueue).filter_by(id=queue_id), MusicQueue)[0]
    if not record or not record.url:
        raise HTTPException(404, "Файл не найден")

    try:

        pipeline_sql(sqlalchemy.insert(MusicMeta).
                     values(name=record.url,
                            url=record.url, music_category=1), MusicMeta)
        print(record.url)
        pipeline_sql(sqlalchemy.delete(MusicQueue).where(MusicQueue.id == queue_id))
        stream = minio_manager.stream_file("music", record.url)
        return StreamingResponse(
            stream,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f'attachment; filename="{record.name}"'}
        )
    except Exception as e:
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")


@app.delete("/reject_audio/{queue_id}")
async def reject_audio(queue_id: int):
    record = pipeline_sql(sqlalchemy.select(MusicQueue).where(MusicQueue.id == queue_id), MusicQueue)[0]
    if not record:
        raise HTTPException(404, "Файл не найден")

    try:
        print(record)
        minio_manager.delete_file("music", record.url)
    except Exception as e:
        raise HTTPException(500, f"Ошибка удаления из MinIO: {str(e)}")

    pipeline_sql(sqlalchemy.delete(MusicQueue).where(MusicQueue.id == queue_id))

    return {"detail": "Аудиофайл отклонён и удалён"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
