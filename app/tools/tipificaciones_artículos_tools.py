import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL

# Configuración de tipificaciones según swagger.json
TIPIFICACIONES_CONFIG = {
    "Familia": {
        "endpoint": "Familia",
        "nombre_display": "Familias",
        "descripcion": "Grupos de productos similares"
    },
    "Tipodearticulo": {
        "endpoint": "Tipodearticulo", 
        "nombre_display": "Tipos de Artículo",
        "descripcion": "Clasificación del tipo de producto"
    },
    "Linea": {
        "endpoint": "Linea",
        "nombre_display": "Líneas",
        "descripcion": "Marcas o líneas comerciales"
    },
    "Grupo": {
        "endpoint": "Grupo",
        "nombre_display": "Grupos",
        "descripcion": "Agrupaciones de artículos"
    },
    "Material": {
        "endpoint": "Material",
        "nombre_display": "Materiales", 
        "descripcion": "Materiales de fabricación"
    },
    "Clasificacionarticulo": {
        "endpoint": "Clasificacionarticulo",
        "nombre_display": "Clasificaciones de Artículo",
        "descripcion": "Clasificaciones específicas de artículos"
    },
    "Categoriadearticulo": {
        "endpoint": "Categoriadearticulo",
        "nombre_display": "Categorías de Artículo", 
        "descripcion": "Categorías comerciales de artículos"
    },
    "Proveedor": {
        "endpoint": "Proveedor",
        "nombre_display": "Proveedores",
        "descripcion": "Empresas proveedoras",
        "campo_descripcion": "Nombre"  # Caso especial
    },
    "Unidaddemedida": {
        "endpoint": "Unidaddemedida",
        "nombre_display": "Unidades de Medida",
        "descripcion": "Unidades de medida para artículos"
    },
    "Temporada": {
        "endpoint": "Temporada",
        "nombre_display": "Temporadas",
        "descripcion": "Temporadas comerciales"
    },
    "Paletadecolores": {
        "endpoint": "Paletadecolores",
        "nombre_display": "Paletas de Colores",
        "descripcion": "Conjuntos de colores disponibles"
    },
    "Curvadetalles": {
        "endpoint": "Curvadetalles",
        "nombre_display": "Curvas de Talles",
        "descripcion": "Conjuntos de talles disponibles"
    }
}

def obtener_tipificacion_generica(tipo_tipificacion: str, base_datos: str = "ECOMMECS") -> str:
    """
    Helper genérico para obtener cualquier tipificación de artículos.
    
    Args:
        tipo_tipificacion: Tipo de tipificación (debe estar en TIPIFICACIONES_CONFIG)
        base_datos: Base de datos a consultar
    
    Returns:
        Una tabla formateada con la tipificación solicitada
    """
    if tipo_tipificacion not in TIPIFICACIONES_CONFIG:
        return f"Error: Tipificación '{tipo_tipificacion}' no válida. Opciones válidas: {', '.join(TIPIFICACIONES_CONFIG.keys())}"
    
    config = TIPIFICACIONES_CONFIG[tipo_tipificacion]
    
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/{config['endpoint']}/"
        params = {"limit": 1000}
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = ["Código", "Descripción"]
        
        # Obtener resultados
        items = data.get("Resultados", [])
        
        # Determinar el campo de descripción (Proveedor usa "Nombre", otros usan "Descripcion")
        campo_desc = config.get("campo_descripcion", "Descripcion")
        
        # Llenar tabla
        for item in items:
            table.add_row([
                item.get("Codigo", ""),
                item.get(campo_desc, "")
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.max_width["Descripción"] = 50
        
        total = len(items)
        
        resultado = f"📋 **{config['nombre_display']} - BD: {base_datos}**\n"
        resultado += f"💡 {config['descripcion']}\n\n"
        resultado += f"Total de {config['nombre_display'].lower()}: {total}\n\n"
        resultado += table.get_string()
        
        return resultado
        
    except Exception as e:
        return f"Error al obtener {config['nombre_display'].lower()}: {str(e)}"

# Tools específicas usando el helper genérico

@mcp.tool()
def listar_familias(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las familias de artículos disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las familias
    """
    return obtener_tipificacion_generica("Familia", base_datos)

@mcp.tool()
def listar_tipos_articulo(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los tipos de artículo disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con los tipos de artículo
    """
    return obtener_tipificacion_generica("Tipodearticulo", base_datos)

@mcp.tool()
def listar_lineas(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las líneas comerciales disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las líneas
    """
    return obtener_tipificacion_generica("Linea", base_datos)

@mcp.tool()
def listar_grupos(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los grupos de artículos disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con los grupos
    """
    return obtener_tipificacion_generica("Grupo", base_datos)

@mcp.tool()
def listar_materiales(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los materiales disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con los materiales
    """
    return obtener_tipificacion_generica("Material", base_datos)

@mcp.tool()
def listar_clasificaciones_articulo(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las clasificaciones de artículos disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las clasificaciones de artículo
    """
    return obtener_tipificacion_generica("Clasificacionarticulo", base_datos)

@mcp.tool()
def listar_categorias_articulo(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las categorías de artículos disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las categorías de artículo
    """
    return obtener_tipificacion_generica("Categoriadearticulo", base_datos)

@mcp.tool()
def listar_proveedores(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los proveedores disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con los proveedores
    """
    return obtener_tipificacion_generica("Proveedor", base_datos)

@mcp.tool()
def listar_unidades_medida(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las unidades de medida disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las unidades de medida
    """
    return obtener_tipificacion_generica("Unidaddemedida", base_datos)

@mcp.tool()
def listar_temporadas(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las temporadas disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las temporadas
    """
    return obtener_tipificacion_generica("Temporada", base_datos)

@mcp.tool()
def listar_paletas_colores(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las paletas de colores disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las paletas de colores
    """
    return obtener_tipificacion_generica("Paletadecolores", base_datos)

@mcp.tool()
def listar_curvas_talles(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las curvas de talles disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las curvas de talles
    """
    return obtener_tipificacion_generica("Curvadetalles", base_datos)

@mcp.tool()
def listar_todas_las_tipificaciones(base_datos: str = "ECOMMECS") -> str:
    """
    Lista un resumen de todas las tipificaciones disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Un resumen con los conteos de cada tipificación
    """
    resultado = f"📊 **Resumen de Tipificaciones - BD: {base_datos}**\n\n"
    
    # Crear tabla resumen
    table = PrettyTable()
    table.field_names = ["Tipificación", "Total Items", "Descripción"]
    
    for key, config in TIPIFICACIONES_CONFIG.items():
        try:
            # Obtener headers con la base de datos especificada
            headers = get_headers_with_db(base_datos)
                
            url = f"{API_BASE_URL}/{config['endpoint']}/"
            params = {"limit": 1000}
            response = httpx.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            total = len(data.get("Resultados", []))
            
            table.add_row([
                config['nombre_display'],
                str(total),
                config['descripcion']
            ])
        except:
            table.add_row([
                config['nombre_display'],
                "Error",
                config['descripcion']
            ])
    
    # Configurar la tabla
    table.align = "l"
    table.max_width["Descripción"] = 40
    
    resultado += table.get_string()
    resultado += "\n\n💡 **Uso**: Utiliza las tools específicas como `listar_familias`, `listar_materiales`, etc. para obtener detalles completos."
    
    return resultado
