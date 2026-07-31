import logging

logger = logging.getLogger(__name__)

def detect_language(text):
    try:
        from langdetect import detect, detect_langs
        
        if not text or len(text.strip()) < 20:
            return "es"
        
        # Intentar detectar múltiples idiomas y tomar el más probable
        try:
            langs = detect_langs(text)
            detected = str(langs[0]).split(':')[0]
        except:
            detected = detect(text)
        
        # Si detecta portugués pero ve palabras españolas, es español
        if detected == 'pt':
            text_lower = text.lower()
            spanish_words = ['el ', 'la ', 'que ', 'de ', 'para ', 'por ', 'en ', 'con ', 'su ', 'es ', 'son ', 'está ', 'están ', 'fue ', 'fueron ']
            count = sum(1 for word in spanish_words if word in text_lower)
            if count > 5:
                detected = 'es'
        
        logger.info(f"Idioma: {detected}")
        return detected
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return "es"
