from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
# from typing import Annotated

import os
from loguru import logger
import torch
from ultralytics import YOLO

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Running on {DEVICE}")

model = YOLO("last.pt").to(DEVICE)

app = FastAPI()

@app.get("/")
async def read_root():
    return JSONResponse({"Hello": "FastAPI"})

# @app.post("/files/")
# async def create_file(file: Annotated[bytes, File()]):
#     return {"file_size": len(file)}


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     return {"filename": file.filename}

# @app.post("/file/upload-bytes")
# def upload_file_bytes(file_bytes: bytes = File()):
#   return {'file_bytes': str(file_bytes)}


@app.post("/file/upload-file")
def upload_file(file: UploadFile):
  return file


@app.post("/upload_file/")
async def upload_file(file: UploadFile = File(...)):
    file_name = file.filename
    file_extension = os.path.splitext(file_name)[1]

    if file_extension not in [".docx",".pdf"]:
        logger.error(f"Неподдерживаемое расширение файла: {file_extension}")
        return JSONResponse(content={"error": "Поддерживаются только файлы DOCX и PDF"}, status_code=400)

    file_location = f"upload_file/{file_name}"
    try:
        os.makedirs("upload_file", exist_ok=True)
        with open(file_location, 'wb') as destination:
            destination.write(await file.read())
        logger.info(f"Файл сохранён: {file_location}")

        results = model.predict(file_location, device=DEVICE)
        prediction = results[0]

        pred_classes = prediction.boxes.cls.cpu().numpy()
        class_names = [model.names[int(cls)] for cls in pred_classes]

        logger.info(f"Предсказание для {file_name}: {class_names}")
        return JSONResponse(content={"message": f"Предсказано: {class_names}", "file_location": file_location})

    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        return JSONResponse(content={"message": "Ошибка при обработке файла."}, status_code=500)

@app.get("/file/{file_name}")
async def get_file(file_name: str):
    file_path = f"upload_file/{file_name}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(content={"error": "Файл не найден"}, status_code=404)