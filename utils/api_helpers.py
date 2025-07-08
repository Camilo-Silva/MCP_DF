from config import ID_CLIENTE, JW_TOKEN, API_BASE_URL

def get_headers_with_db(base_datos: str) -> dict:
    """
    Construye el diccionario de cabeceras para las solicitudes a la API de Dragonfish.
    """
    return {
        "accept": "application/json",
        "Authorization": JW_TOKEN, # Token JWT para autenticación
        "BaseDeDatos": base_datos,
        "IdCliente": ID_CLIENTE,
    }
