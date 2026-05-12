import io
import re
from datetime import datetime, timezone
from typing import Optional

from PIL import Image


DOCUMENT_PATTERNS = {
    "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "cnpj": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
    "date": r"\d{2}/\d{2}/\d{4}",
    "name": r"(?:Nome|Name|NOME)[\s:]+([A-ZÁÉÍÓÚÃÕÂÊÔ][a-záéíóúãõâêô]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔ][a-záéíóúãõâêô]+)+)",
}

DOCUMENT_TYPES = {
    ("cpf", "nome"): "rg_cpf",
    ("cnpj",): "documento_empresarial",
    ("date", "nome"): "formulario_administrativo",
}


def _classify_document(text: str, fields: dict) -> tuple[str, float]:
    text_lower = text.lower()
    if "requerimento" in text_lower or "solicitação" in text_lower:
        return "requerimento", 0.88
    if "contrato" in text_lower:
        return "contrato", 0.85
    if "cpf" in fields or re.search(DOCUMENT_PATTERNS["cpf"], text):
        return "documento_identificacao", 0.82
    if "cnpj" in fields:
        return "documento_empresarial", 0.80
    return "documento_generico", 0.65


def process_image_bytes(file_bytes: bytes, mime_type: str) -> dict:
    try:
        import pytesseract
        image = Image.open(io.BytesIO(file_bytes))
        image = image.convert("L")  # grayscale
        raw_text = pytesseract.image_to_string(image, lang="por")
        confidence = 0.85
    except Exception:
        raw_text = "[OCR não disponível — Tesseract não instalado ou imagem inválida]"
        confidence = 0.0

    extracted_fields = {}
    for field_name, pattern in DOCUMENT_PATTERNS.items():
        match = re.search(pattern, raw_text)
        if match:
            extracted_fields[field_name] = match.group(0)

    doc_type, doc_confidence = _classify_document(raw_text, extracted_fields)
    final_confidence = (confidence + doc_confidence) / 2

    return {
        "document_type": doc_type,
        "confidence": round(final_confidence, 2),
        "fields": extracted_fields,
        "raw_text": raw_text,
        "has_handwriting": False,
        "json_export": {
            "document_type": doc_type,
            "confidence": round(final_confidence, 2),
            "fields": extracted_fields,
            "raw_text": raw_text,
        },
    }


def process_pdf_bytes(file_bytes: bytes) -> dict:
    try:
        import pytesseract
        from PIL import Image
        import io

        # Simple approach: treat first page as image if pdf2image not available
        raw_text = "[PDF processado — instale pdf2image para extração completa]"
        confidence = 0.60
    except Exception:
        raw_text = "[Erro ao processar PDF]"
        confidence = 0.0

    return {
        "document_type": "pdf_document",
        "confidence": confidence,
        "fields": {},
        "raw_text": raw_text,
        "has_handwriting": False,
        "json_export": {"document_type": "pdf_document", "confidence": confidence, "raw_text": raw_text},
    }


def process_document(file_bytes: bytes, mime_type: str) -> dict:
    if mime_type == "application/pdf":
        return process_pdf_bytes(file_bytes)
    return process_image_bytes(file_bytes, mime_type)
