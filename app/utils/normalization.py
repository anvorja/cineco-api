# app/utils/normalization.py
import re

class NameNormalizer:
    """
    Clase para normalizar nombres y apellidos con casos especiales.
    """

    # Palabras que deben permanecer en minúsculas (excepto si están al inicio)
    LOWERCASE_PARTICLES = {
        'de', 'del', 'la', 'los', 'las', 'y', 'el',
        'von', 'van', 'da', 'di', 'bin', 'ibn'
    }

    # Prefijos especiales que requieren capitalización especial
    SPECIAL_PREFIXES = {
        'mc': 'Mc',
        'mac': 'Mac',
        'o\'': 'O\'',
        'san': 'San',
        'santa': 'Santa'
    }

    @staticmethod
    def normalize_name(name: str, use_advanced_rules: bool = True) -> str:
        """
        Normalizar nombre aplicando reglas de capitalización.

        Args:
            name: Nombre a normalizar
            use_advanced_rules: Si aplicar reglas avanzadas para casos especiales

        Returns:
            Nombre normalizado
        """
        if not name or not isinstance(name, str):
            return name

        # Trim y verificar que no esté vacío
        trimmed_name = name.strip()
        if not trimmed_name:
            return ''

        if use_advanced_rules:
            return NameNormalizer._normalize_advanced(trimmed_name)
        else:
            return NameNormalizer._normalize_simple(trimmed_name)

    @staticmethod
    def _normalize_simple(name: str) -> str:
        """
        Normalización simple: primera letra de cada palabra en mayúscula.

        Ejemplos:
        - "AnDrEs" -> "Andres"
        - "borjA" -> "Borja"
        - "maría   josé" -> "María José"
        """
        # Dividir por espacios y filtrar espacios vacíos
        words = [word for word in name.split() if word]

        normalized_words = []
        for word in words:
            # Primera letra mayúscula, resto minúsculas
            normalized_word = word[0].upper() + word[1:].lower()
            normalized_words.append(normalized_word)

        # Unir con un solo espacio
        return ' '.join(normalized_words)

    @staticmethod
    def _normalize_advanced(name: str) -> str:
        """
        Normalización avanzada con casos especiales.

        Ejemplos:
        - "juan de la cruz" -> "Juan de la Cruz"
        - "maría del carmen" -> "María del Carmen"
        - "o'connor" -> "O'Connor"
        - "mcdonald" -> "McDonald"
        """
        # Dividir por espacios y filtrar espacios vacíos
        words = [word for word in name.split() if word]
        if not words:
            return ''

        normalized_words = []

        for i, word in enumerate(words):
            word_lower = word.lower()

            # Si es la primera palabra, siempre capitalizar
            if i == 0:
                normalized_words.append(NameNormalizer._capitalize_word(word))
                continue

            # Verificar partículas que van en minúsculas
            if word_lower in NameNormalizer.LOWERCASE_PARTICLES:
                normalized_words.append(word_lower)
                continue

            # Capitalizar normalmente
            normalized_words.append(NameNormalizer._capitalize_word(word))

        return ' '.join(normalized_words)

    @staticmethod
    def _capitalize_word(word: str) -> str:
        """
        Capitalizar una palabra considerando prefijos especiales.
        """
        word_lower = word.lower()

        # Verificar prefijos especiales
        for prefix, correct_form in NameNormalizer.SPECIAL_PREFIXES.items():
            if word_lower.startswith(prefix):
                # Caso especial para O'
                if prefix == "o'":
                    if len(word) > 2:
                        return correct_form + word[2].upper() + word[3:].lower()
                    return correct_form

                # Caso especial para Mc/Mac
                elif prefix in ['mc', 'mac']:
                    prefix_len = len(prefix)
                    if len(word) > prefix_len:
                        return correct_form + word[prefix_len].upper() + word[prefix_len + 1:].lower()
                    return correct_form

                # Otros casos especiales
                else:
                    return correct_form + word[len(prefix):].lower()

        # Capitalización normal
        return word[0].upper() + word[1:].lower()

    @staticmethod
    def validate_name_format(name: str) -> bool:
        """
        Validar que el nombre solo contenga caracteres permitidos.

        Args:
            name: Nombre a validar

        Returns:
            True si el formato es válido
        """
        if not name or not isinstance(name, str):
            return False

        # Permitir letras, espacios, tildes, ñ, apóstrofes y guiones
        pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\'\-\s]+$'
        return bool(re.match(pattern, name.strip()))
