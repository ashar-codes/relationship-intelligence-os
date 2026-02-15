import pytesseract
from PIL import Image
import io


def extract_text_from_image(uploaded_file):

    try:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception:
        return None
