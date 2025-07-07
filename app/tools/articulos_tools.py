import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL

@mcp.tool()
def listar_articulos(limite: int | None = None, base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los artículos con su código y descripción.
    
    Args:
        limite: Número máximo de artículos a mostrar (opcional)
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con los artículos
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/Articulo/"
        # Si se especifica un límite, lo usamos; si no, obtenemos todos los artículos
        params = {"limit": limite if limite else 10000}
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = ["Código", "Descripción"]
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        
        # Llenar tabla
        for articulo in articulos:
            table.add_row([
                articulo.get("Codigo", ""),
                articulo.get("Descripcion", "")
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.max_width["Descripción"] = 50
        
        total = data.get("TotalRegistros", 0)
        mostrados = len(articulos)
        
        return f"Total de artículos: {total}, Mostrando: {mostrados}\n\n{table.get_string()}"
        
    except Exception as e:
        return f"Error al obtener los artículos: {str(e)}"

@mcp.tool()
def listar_articulos_con_familia(limite: int | None = None, base_datos: str = "ECOMMECS") -> str:
    """
    Lista artículos con su código, descripción, código de familia y tipo de artículo.
    
    Args:
        limite: Número máximo de artículos a mostrar (opcional)
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con los artículos y sus familias
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/Articulo/"
        # Si se especifica un límite, lo usamos; si no, obtenemos todos los artículos
        params = {"limit": limite if limite else 10000}
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = ["Código", "Descripción", "Familia", "Tipo"]
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        
        # Llenar tabla
        for articulo in articulos:
            table.add_row([
                articulo.get("Codigo", ""),
                articulo.get("Descripcion", ""),
                articulo.get("Familia", ""),
                articulo.get("TipodeArticulo", "")
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.max_width["Descripción"] = 40
        
        total = data.get("TotalRegistros", 0)
        mostrados = len(articulos)
        
        return f"Total de artículos: {total}, Mostrando: {mostrados}\n\n{table.get_string()}"
        
    except Exception as e:
        return f"Error al obtener los artículos: {str(e)}"

@mcp.tool()
def obtener_detalle_articulo(codigo: str, base_datos: str = "ECOMMECS") -> str:
    """
    Obtiene información detallada de un artículo específico por su código.
    
    Args:
        codigo: Código del artículo a buscar
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Información detallada del artículo en formato legible
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        # Primero obtenemos la lista completa (podría optimizarse con un endpoint específico)
        url = f"{API_BASE_URL}/Articulo/"
        # Obtenemos todos los artículos para buscar el específico
        params = {"limit": 10000}
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Buscar el artículo por código
        articulo_encontrado = None
        for articulo in data.get("Resultados", []):
            if articulo.get("Codigo") == codigo:
                articulo_encontrado = articulo
                break
        
        if not articulo_encontrado:
            return f"No se encontró ningún artículo con el código {codigo}"
        
        # Crear una representación más legible del artículo
        resultado = f"## 📋 Información del artículo: {codigo}\n\n"
        resultado += f"**🏷️ Descripción**: {articulo_encontrado.get('Descripcion', '')}\n"
        resultado += f"**👥 Familia**: {articulo_encontrado.get('Familia', '')} (Grupo de productos similares)\n"
        resultado += f"**📦 Tipo de artículo**: {articulo_encontrado.get('TipodeArticulo', '')} (Clasificación del producto)\n"
        resultado += f"**🏪 Línea**: {articulo_encontrado.get('Linea', '')} (Marca o línea comercial)\n"
        resultado += f"**📂 Categoría**: {articulo_encontrado.get('CategoriaDeArticulo', '')} (Categoría comercial)\n"
        resultado += f"**🏭 Proveedor**: {articulo_encontrado.get('Proveedor', '')} (Código del proveedor)\n"
        resultado += f"**🌍 Importado**: {'Sí' if articulo_encontrado.get('Importado') else 'No'} (Origen del producto)\n"
        
        # Agregar información adicional si existe
        if articulo_encontrado.get("DescripcionAdicional"):
            resultado += f"**📝 Descripción adicional**: {articulo_encontrado.get('DescripcionAdicional')}\n"
        
        # Agregar más campos útiles si están disponibles
        if articulo_encontrado.get("Codigo"):
            resultado += f"**🔢 Código interno**: {articulo_encontrado.get('Codigo')}\n"
        
        if articulo_encontrado.get("CodigoBarras"):
            resultado += f"**📊 Código de barras**: {articulo_encontrado.get('CodigoBarras')}\n"
        
        if articulo_encontrado.get("UnidadMedida"):
            resultado += f"**📏 Unidad de medida**: {articulo_encontrado.get('UnidadMedida')}\n"
        
        if articulo_encontrado.get("Peso"):
            resultado += f"**⚖️ Peso**: {articulo_encontrado.get('Peso')} (en la unidad configurada)\n"
        
        if articulo_encontrado.get("PrecioVenta"):
            resultado += f"**💰 Precio de venta**: ${articulo_encontrado.get('PrecioVenta')}\n"
        
        if articulo_encontrado.get("Estado"):
            estado = "Activo" if articulo_encontrado.get('Estado') else "Inactivo"
            resultado += f"**🔄 Estado**: {estado}\n"
        
        # Información de participantes/componentes si es un kit
        if articulo_encontrado.get("ParticipantesDetalle") and len(articulo_encontrado.get("ParticipantesDetalle")) > 0:
            resultado += "\n### Componentes del kit:\n\n"
            
            # Crear tabla para los componentes
            comp_table = PrettyTable()
            comp_table.field_names = ["Artículo", "Descripción", "Cantidad", "Color", "Talle"]
            
            for componente in articulo_encontrado.get("ParticipantesDetalle"):
                comp_table.add_row([
                    componente.get("Articulo", ""),
                    componente.get("ArticuloDetalle", ""),
                    componente.get("Cantidad", ""),
                    componente.get("ColorDetalle", ""),
                    componente.get("Talle", "")
                ])
            
            comp_table.align = "l"
            resultado += comp_table.get_string()
        
        return resultado
        
    except Exception as e:
        return f"Error al obtener el detalle del artículo: {str(e)}"

@mcp.tool()
def listar_familias(base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las familias de artículos disponibles en el sistema.
    
    Args:
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las familias
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/Familia/"
        # Agregamos el parámetro limit para obtener todas las familias
        params = {"limit": 1000}
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = ["Código", "Descripción"]
        
        # Obtener resultados
        familias = data.get("Resultados", [])
        
        # Llenar tabla
        for familia in familias:
            table.add_row([
                familia.get("Codigo", ""),
                familia.get("Descripcion", "")
            ])
        
        # Configurar la tabla
        table.align = "l"
        
        total = len(familias)
        
        return f"Total de familias: {total}\n\n{table.get_string()}"
        
    except Exception as e:
        return f"Error al obtener las familias: {str(e)}"
