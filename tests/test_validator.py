import pytest
# Intentamos importar la función que TODAVÍA NO EXISTE
# Esto es puro TDD: definir la interfaz antes que la implementación.
from src.services.pdf_service import validar_archivo_pdf

def test_debe_rechazar_archivo_que_no_es_pdf():
    """Prueba que el validador rechace extensiones incorrectas."""
    resultado, mensaje = validar_archivo_pdf("documento.txt", 1024)
    assert resultado is False
    assert "Formato no permitido" in mensaje

def test_debe_rechazar_archivo_muy_grande():
    """Prueba que el validador rechace archivos que superen el tamaño."""
    # Suponiendo un límite de 5MB (5 * 1024 * 1024 bytes)
    tamanio_excedido = 6 * 1024 * 1024 
    resultado, mensaje = validar_archivo_pdf("proyecto.pdf", tamanio_excedido)
    assert resultado is False
    assert "Tamaño excedido" in mensaje
    