# server.py
from mcp.server.fastmcp import FastMCP
import config

# 1. Inicialización del servidor FastMCP
# Se utiliza la configuración desde config.py para mantener este archivo limpio.
mcp = FastMCP(
    title=config.SERVER_TITLE,
    description=config.SERVER_DESCRIPTION,
    version=config.SERVER_VERSION,
)

# 2. Registro de herramientas
# Simplemente importando los módulos de herramientas, las funciones decoradas con @mcp.tool()
# se registrarán automáticamente en la instancia 'mcp'.
# Esto hace que agregar nuevos grupos de herramientas sea tan fácil como agregar una nueva línea de importación.
from app.tools import articulos_tools, colores_tools, talles_tools, ConsultasStockYPrecios_tools, tipificaciones_artículos_tools, equivalencias_tools
from utils import exportar_a_excel_tools

# La lógica para ejecutar el servidor (if __name__ == "__main__":) se ha movido a main.py
# para seguir las mejores prácticas.