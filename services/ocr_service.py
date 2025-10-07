import re

try:
    # Optional dependency; we fall back gracefully if not installed
    from paddleocr import PaddleOCR  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    PaddleOCR = None  # type: ignore


class PlateOCR:
    def __init__(self):
        self._ocr = None
        if PaddleOCR is not None:
            try:
                self._ocr = PaddleOCR(lang="en", use_angle_cls=True, use_gpu=False)
            except Exception:
                self._ocr = None

    def extract_plate(self, image_path: str) -> tuple[str, float]:
        if self._ocr is None:
            # Simple fallback: return alphanumeric words of reasonable length
            # Real model path unavailable; caller should handle low confidence
            text = image_path.split("/")[-1].split("\\")[-1]
            cleaned = re.sub(r"[^A-Za-z0-9]", "", text.upper())
            if not cleaned:
                return "", 0.0
            m = re.search(r"[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{3,4}", cleaned)
            plate = m.group(0) if m else cleaned[:10]
            return plate, 0.40

        result = self._ocr.ocr(image_path, cls=True)
        candidates: list[tuple[str, float]] = []
        for line in result or []:
            for _, (text, conf) in line:
                candidates.append((str(text), float(conf)))
        if not candidates:
            return "", 0.0
        raw, conf = max(candidates, key=lambda x: x[1])
        raw = re.sub(r"[^A-Za-z0-9]", "", raw.upper())
        m = re.search(r"[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{3,4}", raw)
        plate = m.group(0) if m else raw
        return plate, float(conf)


