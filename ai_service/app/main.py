from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile
from app.processor import ReceiptProcessor

app = FastAPI(
    title="Trip-log OCR Service",
    description="영수증 이미지에서 구조화된 데이터를 추출하는 AI 서비스",
    version="1.0.0",
)

processor = ReceiptProcessor()
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/ocr")
async def ocr_receipt(file: UploadFile):
    # 이미지 파일 검증
    if not file.content_type in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다 (jpeg, png)")

    # 파일 크기 검증
    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="파일 크기는 5MB 이하여야 합니다")

    # OCR 처리
    result = processor.process_receipt(image_bytes)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result