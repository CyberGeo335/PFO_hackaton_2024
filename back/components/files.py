from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/file/download")
def download_file():
  return FileResponse(path='data.xlsx', filename='Статистика покупок.xlsx', media_type='multipart/form-data')