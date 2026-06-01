import io
import re
from typing import Any, Dict
from PIL import Image

try:
    import pytesseract
except Exception:
    pytesseract = None


AMOUNT_RE = re.compile(r"\d+[\.,]?\d{0,2}")
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")


def ocr_image(image_bytes: bytes) -> Dict[str, Any]:
    """Perform OCR on image bytes and return extracted text and simple parsing.

    Returns dict: {text, amounts: [], dates: []}
    If pytesseract not available, returns an error message.
    """
    if pytesseract is None:
        return {'error': 'pytesseract not installed or tesseract binary not available'}

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except Exception as e:
        return {'error': f'Could not open image: {e}'}

    try:
        text = pytesseract.image_to_string(img)
    except Exception as e:
        return {'error': f'OCR failed: {e}'}

    amounts = AMOUNT_RE.findall(text)
    dates = DATE_RE.findall(text)

    # Normalize amounts
    normalized = []
    for a in amounts:
        a_norm = a.replace(',', '')
        try:
            normalized.append(float(a_norm))
        except Exception:
            pass

    return {
        'text': text,
        'amounts': normalized,
        'dates': dates
    }
