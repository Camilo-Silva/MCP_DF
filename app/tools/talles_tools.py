import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL

@mcp.tool()
def listar_talles(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los talles disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con los talles
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/Talle/"
        # Agregamos el parámetro limit con un valor alto para obtener todos los talles
        params = {"limit": 1000}
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = ["Código", "Descripción", "Orden"]
        
        # Obtener resultados
        talles = data.get("Resultados", [])
        
        # Llenar tabla
        for talle in talles:
            table.add_row([
                talle.get("Codigo", ""),
                talle.get("Descripcion", ""),
                talle.get("Orden", 0)
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.align["Orden"] = "r"  # Alinear orden a la derecha
        
        total = len(talles)
        
        return f"Total de talles: {total}\n\n{table.get_string()}"
        
    except Exception as e:
        return f"Error al obtener los talles: {str(e)}"
