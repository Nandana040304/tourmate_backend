from rest_framework import serializers


class TranslationSerializer(serializers.Serializer):
    """Serializer for translation requests"""
    text = serializers.CharField(required=True, help_text="Text to translate")
    source_language = serializers.CharField(
        default='ml',
        required=False,
        help_text="Source language code (default: 'ml' for Malayalam)"
    )
    target_language = serializers.CharField(
        default='en',
        required=False,
        help_text="Target language code (default: 'en' for English)"
    )


class TranslationResponseSerializer(serializers.Serializer):
    """Serializer for translation response"""
    original_text = serializers.CharField()
    translated_text = serializers.CharField()
    source_language = serializers.CharField()
    target_language = serializers.CharField()
