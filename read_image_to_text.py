from PIL import Image
import pytesseract

def read_image_to_text(image_path: str) -> str:
    """
    Reads text from an image file.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The extracted text from the image.
    """
    try:
        # Open the image file
        image = Image.open(image_path)
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise RuntimeError(f"Failed to read text from image: {e}")
