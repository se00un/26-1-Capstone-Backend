import base64
import json
import os
from typing import Any, Dict

from openai import OpenAI

from app.prompts import SYSTEM_PROMPT, USER_PROMPT

RECEIPT_SCHEMA = {
    "amount_original": "number",
    "currency": "string",
    "expense_date": "string",  # YYYY-MM-DD
    "category": "null",
    "raw_ocr_text": "string",
}


class ReceiptProcessor:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        self.model = os.getenv("OPENAI_MODEL", "gemini-2.5-flash")

    def process_receipt(self, image_bytes: bytes) -> Dict[str, Any]:
        # 이미지 base64 인코딩
        img_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # 프롬프트에 스키마 주입
        system_prompt = SYSTEM_PROMPT.format(
            json_schema_content=json.dumps(RECEIPT_SCHEMA, indent=2)
        )

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                        },
                    ],
                },
            ],
        )

        # JSON 파싱
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse OCR result"}