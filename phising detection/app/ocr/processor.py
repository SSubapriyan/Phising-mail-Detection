import pytesseract
from PIL import Image
import os
import logging
from pdf2image import convert_from_path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tesseract Configuration for Windows
# Common installation paths for Tesseract
TESSERACT_PATHS = [
    r'C:\Program Files\PDF24\tesseract\tesseract.exe',
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Users\asus\AppData\Local\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
]

def configure_tesseract():
    if os.name == 'nt':  # Windows
        for path in TESSERACT_PATHS:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract found at: {path}")
                return True
        logger.error("Tesseract OCR not found. Please install it from https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    return True # Assume it's in PATH for Linux/Mac

# Initial configuration
TESSERACT_AVAILABLE = configure_tesseract()

def extract_text_from_image(file_path):
    """
    Extracts text from an image or PDF file using Tesseract OCR.
    """
    if not TESSERACT_AVAILABLE:
        logger.error("OCR skipped: Tesseract not configured.")
        return "ERROR: Tesseract OCR engine not found on the system. Please install it."

    try:
        ext = os.path.splitext(file_path)[1].lower()
        
        # Check if we need to set TESSDATA_PREFIX (especially for PDF24 version)
        if 'PDF24' in pytesseract.pytesseract.tesseract_cmd:
            tessdata_dir = os.path.join(os.path.dirname(pytesseract.pytesseract.tesseract_cmd), 'tessdata')
            os.environ['TESSDATA_PREFIX'] = tessdata_dir

        if ext == '.pdf':
            logger.info(f"Processing PDF: {file_path}")
            # Convert PDF to list of images
            images = convert_from_path(file_path)
            full_text = ""
            for i, img in enumerate(images):
                logger.info(f"Processing page {i+1}")
                text = pytesseract.image_to_string(img)
                full_text += text + "\n"
            return full_text.strip()
        
        else:
            logger.info(f"Processing Image: {file_path}")
            with Image.open(file_path) as img:
                text = pytesseract.image_to_string(img)
                return text.strip()

    except Exception as e:
        error_msg = str(e)
        logger.error(f"OCR Exception: {error_msg}")
        if "tessdata" in error_msg.lower() or "eng" in error_msg.lower():
            return "ERROR: Tesseract language data (eng.traineddata) is missing. Please install the full Tesseract OCR package."
        return f"ERROR: OCR failed - {error_msg}"
