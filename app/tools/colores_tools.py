import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL

@mcp.tool()
def listar_colores(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los colores disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con los colores
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/Color/"
        # Agregamos el parámetro limit con un valor alto para obtener todos los colores
        params = {"limit": 1000}  # Un número suficientemente alto para obtener todos los colores
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = ["Código", "Descripción", "RGB"]
        
        # Obtener resultados
        colores = data.get("Resultados", [])
        
        # Llenar tabla
        for color in colores:
            # Formatear el RGB como un código de color hexadecimal
            r = color.get("R", 0)
            g = color.get("G", 0)
            b = color.get("B", 0)
            rgb = f"#{r:02x}{g:02x}{b:02x}"
            
            table.add_row([
                color.get("Codigo", ""),
                color.get("Descripcion", ""),
                rgb
            ])
        
        # Configurar la tabla
        table.align = "l"
        
        total = len(colores)
        
        return f"Total de colores: {total}\n\n{table.get_string()}"
        
    except Exception as e:
        return f"Error al obtener los colores: {str(e)}"
