def validar_archivo_pdf(nombre_archivo: str, tamanio: int):
    # Esta es la lógica inicial para que el test pase
    if not nombre_archivo.endswith(".pdf"):
        return False, "Formato no permitido"
    
    # Límite de 5MB como ejemplo (5 * 1024 * 1024 bytes)
    if tamanio > 5242880: 
        return False, "Tamaño excedido"
        
    return True, "Archivo válido"