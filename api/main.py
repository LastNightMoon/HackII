import io
import uvicorn
from fastapi import status
from sqlalchemy import or_, and_
from sqlalchemy.sql import func
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
from datetime import datetime
from DataBaseManager import Category as DBCategory, MusicMeta as DBMusicMeta
from DataBaseManager import db
from DataBaseManager.minio_manager import minio_manager
from utils.variable_environment import VarEnv
from fastapi.middleware.cors import CORSMiddleware
from models import AudioBaseInfo, AudioFileResponse, AudioUploadRequest, AudioVersionComparison, AudioUploadResponse, AudioFilterRequest, AudioFullInfo
from fastapi.responses import StreamingResponse


app = FastAPI(title="Голос Победы API", description="API для работы с архивом военных песен")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_session():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

@app.get("/get_audio_list", response_model=List[AudioBaseInfo])
async def get_audio_list():
    try:
        records = db.select(DBMusicMeta)
        return [{
            "id": r.music_id,
            "name": r.name,
            "author": getattr(r, 'author', None),
            "url": f"/get_audio_file/{r.music_id}"
        } for r in records]
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/get_audio_info/{file_id}", response_model=AudioFullInfo)
async def get_audio_info(file_id: int):
    record = db.select_music_by_id(file_id)
    if not record:
        raise HTTPException(404, "Запись не найдена")

    return {
        "id": record.music_id,
        "name": record.name,
        "author": getattr(record, 'author', None),
        "text": getattr(record, 'text_music', ''),
        "url": f"/get_audio_file/{record.music_id}"
    }


@app.get("/get_audio_file/{file_id}")
async def get_audio_file(file_id: int):
    record = db.select_music_by_id(file_id)
    if not record or not record.url:
        raise HTTPException(404, "Файл не найден")

    try:
        file_data = minio_manager.download_file("audio-bucket", record.url)
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f'attachment; filename="{record.name}"'}
        )
    except Exception as e:
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")


@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp3', '.wav')):
        raise HTTPException(400, "Только MP3/WAV файлы")

    try:
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{file_id}{file_ext}"

        file_content = await file.read()
        minio_manager.upload_file("audio-bucket", file_content, file_name)

        new_record = DBMusicMeta(
            name=file.filename,
            url=file_name,
            text_music=""
        )
        db_session = db.get_session()
        db_session.add(new_record)
        db_session.commit()

        return JSONResponse({
            "status": "success",
            "file_id": new_record.music_id,
            "url": f"/get_audio_file/{new_record.music_id}"
        }, status_code=201)

    except Exception as e:
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)