import pytesseract
from PIL import Image
import numpy as np

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

try:
    # Test with a sample image
    test_image_path = r'C:\Users\NANDANA\backend_weather\tourmate_back\media\places\muzhapilangad_beach_hhDiDdV.jpg'
    
    img = Image.open(test_image_path)
    print(f"✓ Image opened successfully")
    print(f"  - Mode: {img.mode}")
    print(f"  - Size: {img.size}")
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
        print(f"✓ Image converted to RGB")
    
    # Convert to numpy array
    img_array = np.array(img)
    print(f"✓ Converted to numpy array")
    
    # Try OCR with Malayalam
    print("⏳ Running OCR with Malayalam language...")
    text = pytesseract.image_to_string(img_array, lang='mal')
    print(f"✓ OCR completed")
    print(f"  - Extracted text: {text[:100] if text else 'No text found'}")
    
except FileNotFoundError as e:
    print(f"✗ File not found: {e}")
except pytesseract.TesseractNotFoundError as e:
    print(f"✗ Tesseract not found: {e}")
    print("  Please ensure Tesseract-OCR is installed at:")
    print("  C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
