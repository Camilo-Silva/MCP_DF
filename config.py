import os
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env
# Esto es útil para no tener que configurar las variables en el sistema operativo durante el desarrollo.
load_dotenv()

# --- Configuración de la API de Dragonfish ---

# Lee la URL base de la API desde una variable de entorno.
# Si no se encuentra, usa una URL por defecto.
API_BASE_URL = os.getenv("API_BASE_URL")

# Lee las credenciales desde variables de entorno para mayor seguridad.
# Es una mala práctica tener secretos como tokens o IDs directamente en el código.
ID_CLIENTE = os.getenv("ID_CLIENTE")
JW_TOKEN = os.getenv("JW_TOKEN")

# --- Configuración del Servidor MCP ---
SERVER_TITLE = "MCP Server para Dragonfish"
SERVER_DESCRIPTION = "Un conjunto de herramientas para interactuar con la API de Dragonfish a través de un asistente de IA."
SERVER_VERSION = "1.0.0"
