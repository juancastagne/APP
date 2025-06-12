import os
import re
import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta
from functools import wraps
from .logger import logger

class SecurityManager:
    """
    Gestor de seguridad para la aplicación Stream Views.
    
    Maneja la validación de entradas, sanitización de datos, y protección
    contra ataques comunes.
    """
    
    def __init__(self):
        """Inicializa el gestor de seguridad."""
        self.rate_limits = {}
        self.max_requests = 100  # Máximo de requests por ventana de tiempo
        self.time_window = 3600  # Ventana de tiempo en segundos (1 hora)
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            logger.warning("No se encontró la clave API de YouTube en las variables de entorno")
    
    def validate_video_id(self, video_id: str) -> bool:
        """
        Valida que el ID del video de YouTube sea válido.
        
        Args:
            video_id (str): ID del video a validar
            
        Returns:
            bool: True si el ID es válido, False en caso contrario
        """
        if not video_id:
            return False
        
        # Patrón de ID de video de YouTube
        pattern = r'^[a-zA-Z0-9_-]{11}$'
        return bool(re.match(pattern, video_id))
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitiza texto de entrada para prevenir XSS y otros ataques.
        
        Args:
            text (str): Texto a sanitizar
            
        Returns:
            str: Texto sanitizado
        """
        if not text:
            return ""
        
        # Eliminar caracteres potencialmente peligrosos
        text = re.sub(r'[<>]', '', text)
        # Escapar caracteres especiales
        text = text.replace('&', '&amp;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        return text
    
    def check_rate_limit(self, ip: str) -> bool:
        """
        Verifica si una IP ha excedido el límite de requests.
        
        Args:
            ip (str): Dirección IP a verificar
            
        Returns:
            bool: True si la IP está dentro del límite, False si lo ha excedido
        """
        now = datetime.now()
        
        # Limpiar entradas antiguas
        self.rate_limits = {
            k: v for k, v in self.rate_limits.items()
            if now - v['timestamp'] < timedelta(seconds=self.time_window)
        }
        
        if ip not in self.rate_limits:
            self.rate_limits[ip] = {
                'count': 1,
                'timestamp': now
            }
            return True
        
        if self.rate_limits[ip]['count'] >= self.max_requests:
            return False
        
        self.rate_limits[ip]['count'] += 1
        return True
    
    def generate_csrf_token(self) -> str:
        """
        Genera un token CSRF.
        
        Returns:
            str: Token CSRF generado
        """
        return secrets.token_hex(32)
    
    def verify_csrf_token(self, token: str, stored_token: str) -> bool:
        """
        Verifica un token CSRF.
        
        Args:
            token (str): Token a verificar
            stored_token (str): Token almacenado
            
        Returns:
            bool: True si el token es válido, False en caso contrario
        """
        return secrets.compare_digest(token, stored_token)
    
    def hash_sensitive_data(self, data: str) -> str:
        """
        Hashea datos sensibles usando SHA-256.
        
        Args:
            data (str): Datos a hashear
            
        Returns:
            str: Hash de los datos
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def validate_api_key(self) -> bool:
        """
        Valida que la clave API esté presente y tenga el formato correcto.
        
        Returns:
            bool: True si la clave API es válida, False en caso contrario
        """
        if not self.api_key:
            return False
        
        # Patrón básico para validar formato de clave API de Google
        pattern = r'^AIza[0-9A-Za-z-_]{35}$'
        return bool(re.match(pattern, self.api_key))

def require_api_key(func):
    """
    Decorador para proteger endpoints que requieren clave API.
    
    Args:
        func: Función a decorar
        
    Returns:
        function: Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        security = SecurityManager()
        if not security.validate_api_key():
            logger.error("Intento de acceso sin clave API válida")
            raise ValueError("API key no válida o no configurada")
        return func(*args, **kwargs)
    return wrapper

def rate_limit(func):
    """
    Decorador para implementar rate limiting.
    
    Args:
        func: Función a decorar
        
    Returns:
        function: Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        security = SecurityManager()
        # En una aplicación real, obtendríamos la IP del request
        ip = "127.0.0.1"  # IP de ejemplo
        if not security.check_rate_limit(ip):
            logger.warning(f"Rate limit excedido para IP: {ip}")
            raise Exception("Demasiadas solicitudes. Por favor, intente más tarde.")
        return func(*args, **kwargs)
    return wrapper

# Instancia global del gestor de seguridad
security_manager = SecurityManager() 