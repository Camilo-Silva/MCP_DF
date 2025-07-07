import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL

@mcp.tool()
def consultar_stock_y_precios(
    limite: int | None = None,
    query: str | None = None,
    lista: str | None = None,
    preciocero: bool | None = None,
    stockcero: bool | None = None,
    exacto: bool | None = None,
    base_datos: str = "ECOMMECS"
) -> str:
    """
    Consulta el stock y precios de todos los artículos del sistema.
    
    Args:
        limite: Número máximo de registros a mostrar (opcional)
        query: Filtro de búsqueda por texto (opcional)
        lista: Filtro por lista de precios específica (opcional)
        preciocero: Incluir artículos con precio cero (opcional)
        stockcero: Incluir artículos con stock cero (opcional)
        exacto: Búsqueda exacta (opcional)
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con stock y precios de artículos
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/ConsultaStockYPrecios/"
        
        # Construir parámetros de la consulta
        params = {}
        
        # Si se especifica un límite, lo usamos; si no, obtenemos muchos registros
        params["limit"] = limite if limite else 5000
        
        # Agregar parámetros opcionales si se proporcionan
        if query:
            params["query"] = query
        if lista:
            params["lista"] = lista
        if preciocero is not None:
            params["preciocero"] = preciocero
        if stockcero is not None:
            params["stockcero"] = stockcero
        if exacto is not None:
            params["exacto"] = exacto
        
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = [
            "Artículo", "Descripción", "Color", "Cod.Color", "Talle", "Cod.Talle", 
            "Stock", "Disponible", "Precio", "Lista"
        ]
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        
        # Recopilar listas disponibles encontradas
        listas_encontradas = set()
        for articulo in articulos:
            if articulo.get("Lista"):
                listas_encontradas.add(articulo.get("Lista"))
        
        # Llenar tabla
        for articulo in articulos:
            table.add_row([
                articulo.get("Articulo", ""),
                articulo.get("ArticuloDescripcion", "")[:25] + "..." if len(articulo.get("ArticuloDescripcion", "")) > 25 else articulo.get("ArticuloDescripcion", ""),
                articulo.get("ColorDescripcion", ""),
                articulo.get("Color", ""),  # Código de color
                articulo.get("TalleDescripcion", ""),
                articulo.get("Talle", ""),  # Código de talle
                articulo.get("Stock", 0),
                articulo.get("Disponible", 0),
                f"${articulo.get('Precio', 0)}",
                articulo.get("Lista", "")
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.align["Stock"] = "r"
        table.align["Disponible"] = "r"
        table.align["Precio"] = "r"
        
        total = data.get("TotalRegistros", 0)
        mostrados = len(articulos)
        
        resultado = "💰📦 **Consulta de Stock y Precios**\n\n"
        resultado += f"Total de registros: {total}, Mostrando: {mostrados}\n\n"
        resultado += table.get_string()
        
        # Agregar información sobre las listas encontradas
        if listas_encontradas:
            resultado += f"\n\n📋 **Listas de Precios Encontradas:** {', '.join(sorted(listas_encontradas))}"
        
        return resultado
        
    except Exception as e:
        return f"Error al consultar stock y precios: {str(e)}"

@mcp.tool()
def consultar_stock_articulo_especifico(
    codigo_articulo: str,
    base_datos: str = "ECOMMECS"
) -> str:
    """
    Consulta el stock y precios de un artículo específico con todas sus combinaciones de color y talle.
    
    Args:
        codigo_articulo: Código del artículo a consultar
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Información detallada de stock y precios del artículo específico
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/ConsultaStockYPrecios/"
        
        # Buscar por código específico
        params = {
            "query": codigo_articulo,
            "exacto": True,
            "limit": 1000
        }
        
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        articulos = data.get("Resultados", [])
        
        if not articulos:
            return f"No se encontró stock para el artículo {codigo_articulo}"
        
        # Filtrar solo el artículo específico
        articulos_filtrados = [art for art in articulos if art.get("Articulo") == codigo_articulo]
        
        if not articulos_filtrados:
            return f"No se encontró stock para el artículo {codigo_articulo}"
        
        # Crear resultado detallado
        primer_articulo = articulos_filtrados[0]
        resultado = f"## 📦💰 Stock y Precios del Artículo: {codigo_articulo}\n\n"
        resultado += f"**📋 Descripción**: {primer_articulo.get('ArticuloDescripcion', '')}\n"
        if primer_articulo.get('ArticuloDescripcionAdicional'):
            resultado += f"**📝 Descripción adicional**: {primer_articulo.get('ArticuloDescripcionAdicional')}\n"
        resultado += "\n"
        
        # Crear tabla detallada
        table = PrettyTable()
        table.field_names = [
            "Color", "Talle", "Stock", "Disponible", 
            "Comprometido", "Pendiente", "Precio Principal"
        ]
        
        total_stock = 0
        total_disponible = 0
        
        for articulo in articulos_filtrados:
            stock = articulo.get("Stock", 0)
            disponible = articulo.get("Disponible", 0)
            total_stock += stock
            total_disponible += disponible
            
            table.add_row([
                articulo.get("ColorDescripcion", ""),
                articulo.get("TalleDescripcion", ""),
                stock,
                disponible,
                articulo.get("Comprometido", 0),
                articulo.get("PendienteEntrega", 0),
                f"${articulo.get('Precio', 0)}"
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.align["Stock"] = "r"
        table.align["Disponible"] = "r"
        table.align["Comprometido"] = "r"
        table.align["Pendiente"] = "r"
        table.align["Precio Principal"] = "r"
        
        resultado += table.get_string()
        resultado += f"\n\n**📊 Resumen Total:**\n"
        resultado += f"- Stock total: {total_stock}\n"
        resultado += f"- Disponible total: {total_disponible}\n"
        resultado += f"- Combinaciones: {len(articulos_filtrados)}\n"
        
        # Mostrar todas las listas de precios si están disponibles
        if articulos_filtrados and articulos_filtrados[0].get("Precios"):
            resultado += f"\n**💰 Listas de Precios Disponibles:**\n"
            precios = articulos_filtrados[0].get("Precios", [])
            for precio in precios:
                resultado += f"- {precio.get('Lista', '')}: ${precio.get('Precio', 0)}\n"
        
        return resultado
        
    except Exception as e:
        return f"Error al consultar stock del artículo específico: {str(e)}"

@mcp.tool()
def consultar_articulos_sin_stock(
    limite: int | None = None,
    base_datos: str = "ECOMMECS"
) -> str:
    """
    Consulta artículos que no tienen stock disponible.
    
    Args:
        limite: Número máximo de artículos a mostrar (opcional)
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con artículos sin stock
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/ConsultaStockYPrecios/"
        
        # Filtrar por artículos sin stock
        params = {
            "stockcero": True,
            "limit": limite if limite else 2000
        }
        
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = [
            "Artículo", "Descripción", "Color", "Talle", "Precio"
        ]
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        
        # Filtrar solo los que realmente tienen stock 0
        articulos_sin_stock = [art for art in articulos if art.get("Stock", 0) == 0]
        
        # Llenar tabla
        for articulo in articulos_sin_stock:
            table.add_row([
                articulo.get("Articulo", ""),
                articulo.get("ArticuloDescripcion", "")[:35] + "..." if len(articulo.get("ArticuloDescripcion", "")) > 35 else articulo.get("ArticuloDescripcion", ""),
                articulo.get("ColorDescripcion", ""),
                articulo.get("TalleDescripcion", ""),
                f"${articulo.get('Precio', 0)}"
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.align["Precio"] = "r"
        
        total_original = data.get("TotalRegistros", 0)
        mostrados = len(articulos_sin_stock)
        
        resultado = f"🚫📦 **Artículos Sin Stock**\n\n"
        resultado += f"Total sin stock encontrados: {mostrados} (de {total_original} registros consultados)\n\n"
        resultado += table.get_string()
        
        return resultado
        
    except Exception as e:
        return f"Error al consultar artículos sin stock: {str(e)}"
