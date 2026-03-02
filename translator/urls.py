from django.urls import path
from .views import TranslateView, BatchTranslateView, OCRView, OCRTranslateView

urlpatterns = [
    path('translate/', TranslateView.as_view(), name='translate'),
    path('translate/batch/', BatchTranslateView.as_view(), name='batch_translate'),
    path('ocr/', OCRView.as_view(), name='ocr'),
    path('ocr/translate/', OCRTranslateView.as_view(), name='ocr_translate'),
]
