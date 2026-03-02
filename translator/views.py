from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from translate import Translator  # retained for compatibility
from deep_translator import GoogleTranslator
from PIL import Image
import pytesseract
from pytesseract import TesseractError
import numpy as np
import io
from .serializers import TranslationSerializer, TranslationResponseSerializer

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class TranslateView(APIView):
    """API endpoint to translate text from one language to another"""

    def post(self, request):
        """
        Translate text from source language to target language
        
        Request body:
        {
            "text": "Malayalam text to translate",
            "source_language": "ml",  # Optional, defaults to "ml"
            "target_language": "en"   # Optional, defaults to "en"
        }
        """
        serializer = TranslationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            text = serializer.validated_data['text']
            source_lang = serializer.validated_data.get('source_language', 'ml')
            target_lang = serializer.validated_data.get('target_language', 'en')

            # Initialize translator
            # translate line-by-line   
            segments = str(text).splitlines()
            translated_segments = []
            for seg in segments:
                if seg.strip():
                    translated_segments.append(
                        GoogleTranslator(source=source_lang, target=target_lang).translate(seg)
                    )
                else:
                    translated_segments.append('')
            translated_text = "\n".join(translated_segments)

            # Prepare response
            response_data = {
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang
            }

            response_serializer = TranslationResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Translation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BatchTranslateView(APIView):
    """API endpoint to translate multiple texts at once"""

    def post(self, request):
        """
        Translate multiple texts
        
        Request body:
        {
            "texts": ["text1", "text2", "text3"],
            "source_language": "ml",  # Optional, defaults to "ml"
            "target_language": "en"   # Optional, defaults to "en"
        }
        """
        if 'texts' not in request.data:
            return Response(
                {"error": "Missing 'texts' field"},
                status=status.HTTP_400_BAD_REQUEST
            )

        texts = request.data.get('texts', [])
        source_lang = request.data.get('source_language', 'ml')
        target_lang = request.data.get('target_language', 'en')

        if not isinstance(texts, list):
            return Response(
                {"error": "'texts' must be a list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            translations = []
            for text in texts:
                segments = str(text).splitlines()
                translated_segments = []
                for seg in segments:
                    if seg.strip():
                        translated_segments.append(
                            GoogleTranslator(source=source_lang, target=target_lang).translate(seg)
                        )
                    else:
                        translated_segments.append('')
                translated_text = "\n".join(translated_segments)
                translations.append({
                    "original_text": text,
                    "translated_text": translated_text,
                    "source_language": source_lang,
                    "target_language": target_lang
                })

            return Response(
                {"translations": translations},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"Batch translation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OCRView(APIView):
    """API endpoint to extract text from images using OCR"""
    
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """
        Extract text from image using OCR
        
        Request: multipart/form-data
        - image: Image file (JPG, PNG, etc.)
        - language: "ml" for Malayalam (optional, defaults to "ml")
        """
        if 'image' not in request.FILES:
            return Response(
                {"error": "Missing 'image' field"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_file = request.FILES['image']
            language = request.data.get('language', 'mal')  # mal = Malayalam
            
            # Read and process image
            image = Image.open(image_file)
            
            # Convert image to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL Image to numpy array
            image_array = np.array(image)
            
            # Extract text using Tesseract OCR
            extracted_text = pytesseract.image_to_string(
                image_array,
                lang=language
            ).strip()

            if not extracted_text:
                return Response(
                    {"error": "No text found in image. Please ensure the image contains clear text."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "extracted_text": extracted_text,
                    "language": language,
                    "success": True
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"OCR failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OCRTranslateView(APIView):
    """API endpoint to extract text from image and translate it in one go"""
    
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """
        Extract text from image and translate it
        
        Request: multipart/form-data
        - image: Image file (JPG, PNG, etc.)
        - source_language: "ml" (optional, defaults to "ml")
        - target_language: "en" (optional, defaults to "en")
        """
        if 'image' not in request.FILES:
            return Response(
                {"error": "Missing 'image' field"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_file = request.FILES['image']
            source_lang = request.data.get('source_language', 'ml')
            target_lang = request.data.get('target_language', 'en')
            ocr_language = request.data.get('ocr_language', 'mal')  # mal = Malayalam
            
            # Read and process image
            image = Image.open(image_file)
            
            # Convert image to RGB if necessary (handles RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL Image to numpy array for better pytesseract compatibility
            image_array = np.array(image)
            
            # Step 1: Extract text using Tesseract OCR
            try:
                extracted_text = pytesseract.image_to_string(
                    image_array,
                    lang=ocr_language
                ).strip()
            except pytesseract.TesseractError as e:
                if 'mal' in str(e).lower():
                    return Response(
                        {
                            "error": f"Malayalam language pack not installed. "
                                    f"Download mal.traineddata from "
                                    f"https://github.com/UB-Mannheim/tesseract/wiki/Data-Files",
                            "details": str(e)
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                raise

            if not extracted_text:
                return Response(
                    {"error": "No text found in image. Please ensure the image contains clear text."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Step 2: Translate extracted text
            segments = str(extracted_text).splitlines()
            translated_segments = []
            for seg in segments:
                if seg.strip():
                    translated_segments.append(
                        GoogleTranslator(source=source_lang, target=target_lang).translate(seg)
                    )
                else:
                    translated_segments.append('')
            translated_text = "\n".join(translated_segments)

            return Response(
                {
                    "extracted_text": extracted_text,
                    "translated_text": translated_text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "success": True
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"OCR or translation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
