import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL
from typing import List, Dict

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
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        
        # Recopilar todas las listas de precios disponibles dinámicamente
        listas_disponibles = set()
        for articulo in articulos:
            precios_articulo = articulo.get("Precios", [])
            if precios_articulo and isinstance(precios_articulo, list):
                for precio_info in precios_articulo:
                    lista_nombre = precio_info.get("Lista", "")
                    if lista_nombre:
                        listas_disponibles.add(lista_nombre)
        
        # Convertir a lista ordenada para mantener consistencia
        listas_ordenadas = sorted(listas_disponibles)
        
        # Crear tabla dinámica con columnas de precios según las listas encontradas
        columnas_base = ["Artículo", "Descripción", "Cod.Color", "Color", "Cod.Talle", "Talle", "Stock", "Disponible"]
        columnas_precios = [f"Precio {lista}" for lista in listas_ordenadas]
        
        table = PrettyTable()
        table.field_names = columnas_base + columnas_precios
        
        # Crear un diccionario para agrupar por artículo, color y talle
        articulos_agrupados = {}
        for articulo in articulos:
            key = (articulo.get("Articulo", ""), articulo.get("Color", ""), articulo.get("Talle", ""))
            if key not in articulos_agrupados:
                articulos_agrupados[key] = {
                    "info": articulo,
                    "precios": {}
                }
            
            # Procesar precios desde el array "Precios"
            precios_articulo = articulo.get("Precios", [])
            if precios_articulo and isinstance(precios_articulo, list):
                for precio_info in precios_articulo:
                    lista_nombre = precio_info.get("Lista", "")
                    precio_valor = precio_info.get("Precio", 0)
                    if lista_nombre:
                        articulos_agrupados[key]["precios"][lista_nombre] = precio_valor
        
        # Llenar tabla dinámicamente
        for key, data_item in articulos_agrupados.items():
            articulo = data_item["info"]
            precios = data_item["precios"]
            
            # Datos base del artículo
            fila_base = [
                articulo.get("Articulo", ""),
                articulo.get("ArticuloDescripcion", "")[:20] + "..." if len(articulo.get("ArticuloDescripcion", "")) > 20 else articulo.get("ArticuloDescripcion", ""),
                articulo.get("ColorDescripcion", ""),
                articulo.get("Color", ""),  # Código de color
                articulo.get("TalleDescripcion", ""),
                articulo.get("Talle", ""),  # Código de talle
                articulo.get("Stock", 0),
                articulo.get("Disponible", 0)
            ]
            
            # Agregar precios dinámicamente según las listas encontradas
            precios_fila = []
            for lista in listas_ordenadas:
                precio_valor = precios.get(lista, 0)
                precios_fila.append(f"${precio_valor}" if precio_valor > 0 else "-")
            
            table.add_row(fila_base + precios_fila)
        
        # Configurar alineación de la tabla
        table.align = "l"
        table.align["Stock"] = "r"
        table.align["Disponible"] = "r"
        
        # Alinear columnas de precios a la derecha
        for lista in listas_ordenadas:
            table.align[f"Precio {lista}"] = "r"
        
        total = data.get("TotalRegistros", 0)
        mostrados = len(articulos_agrupados)
        
        resultado = "💰📦 **Consulta de Stock y Precios**\n\n"
        resultado += f"Total de registros: {total}, Mostrando: {mostrados}\n\n"
        resultado += table.get_string()
        
        # Agregar información sobre las listas encontradas
        if listas_disponibles:
            resultado += f"\n\n📋 **Listas de Precios Encontradas:** {', '.join(listas_ordenadas)}"
        
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
            "Comprometido", "Pendiente"
        ]
        
        # Detectar todas las listas de precios disponibles
        listas_precios_disponibles = set()
        for articulo in articulos_filtrados:
            precios_articulo = articulo.get("Precios", [])
            if precios_articulo and isinstance(precios_articulo, list):
                for precio_info in precios_articulo:
                    lista_nombre = precio_info.get("Lista", "")
                    if lista_nombre:
                        listas_precios_disponibles.add(lista_nombre)
        
        # Agregar columnas de precios dinámicamente
        listas_ordenadas = sorted(listas_precios_disponibles)
        for lista in listas_ordenadas:
            table.field_names.append(f"Precio {lista}")
        
        total_stock = 0
        total_disponible = 0
        
        for articulo in articulos_filtrados:
            stock = articulo.get("Stock", 0)
            disponible = articulo.get("Disponible", 0)
            total_stock += stock
            total_disponible += disponible
            
            # Datos base de la fila
            fila_base = [
                articulo.get("ColorDescripcion", ""),
                articulo.get("TalleDescripcion", ""),
                stock,
                disponible,
                articulo.get("Comprometido", 0),
                articulo.get("PendienteEntrega", 0)
            ]
            
            # Agregar precios dinámicamente
            precios_fila = []
            precios_articulo = articulo.get("Precios", [])
            precios_dict = {}
            
            if precios_articulo and isinstance(precios_articulo, list):
                for precio_info in precios_articulo:
                    lista_nombre = precio_info.get("Lista", "")
                    precio_valor = precio_info.get("Precio", 0)
                    if lista_nombre:
                        precios_dict[lista_nombre] = precio_valor
            
            for lista in listas_ordenadas:
                precio_valor = precios_dict.get(lista, 0)
                precios_fila.append(f"${precio_valor}")
            
            table.add_row(fila_base + precios_fila)
        
        # Configurar alineación de la tabla
        table.align = "l"
        table.align["Stock"] = "r"
        table.align["Disponible"] = "r"
        table.align["Comprometido"] = "r"
        table.align["Pendiente"] = "r"
        
        # Alinear columnas de precios
        for lista in listas_ordenadas:
            table.align[f"Precio {lista}"] = "r"
        
        resultado += table.get_string()
        resultado += "\n\n**📊 Resumen Total:**\n"
        resultado += f"- Stock total: {total_stock}\n"
        resultado += f"- Disponible total: {total_disponible}\n"
        resultado += f"- Combinaciones: {len(articulos_filtrados)}\n"
        
        # Mostrar todas las listas de precios disponibles dinámicamente
        if listas_precios_disponibles:
            resultado += "\n**💰 Listas de Precios Disponibles:**\n"
            # Tomar el primer artículo para mostrar los precios como ejemplo
            if articulos_filtrados:
                primer_articulo = articulos_filtrados[0]
                precios_articulo = primer_articulo.get("Precios", [])
                if precios_articulo and isinstance(precios_articulo, list):
                    for precio_info in precios_articulo:
                        lista_nombre = precio_info.get("Lista", "")
                        precio_valor = precio_info.get("Precio", 0)
                        if lista_nombre:
                            resultado += f"- {lista_nombre}: ${precio_valor}\n"
        
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
        
        resultado = "🚫📦 **Artículos Sin Stock**\n\n"
        resultado += f"Total sin stock encontrados: {mostrados} (de {total_original} registros consultados)\n\n"
        resultado += table.get_string()
        
        return resultado
        
    except Exception as e:
        return f"Error al consultar artículos sin stock: {str(e)}"


def procesar_articulo_para_exportacion(articulo, base_datos):
    dato = {
        "Articulo": articulo.get("Articulo", ""),
        "Descripcion": articulo.get("ArticuloDescripcion", ""),
        "Codigo_Color": articulo.get("Color", ""),
        "Color": articulo.get("ColorDescripcion", ""),
        "Codigo_Talle": articulo.get("Talle", ""),
        "Talle": articulo.get("TalleDescripcion", ""),
        "Stock": articulo.get("Stock", 0),
        "Disponible": articulo.get("Disponible", 0),
        "Comprometido": articulo.get("Comprometido", 0),
        "Pendiente": articulo.get("PendienteEntrega", 0),
        "Base_Datos": base_datos
        
    }
    precios_articulo = articulo.get("Precios", [])
    if precios_articulo and isinstance(precios_articulo, list):
        for precio_info in precios_articulo:
            lista_nombre = precio_info.get("Lista", "")
            precio_valor = precio_info.get("Precio", 0)
            if lista_nombre:
                dato[f"Precio_{lista_nombre}"] = precio_valor
    return dato

@mcp.tool()
def obtener_datos_stock_y_precios(
    limite: int | None = None,
    query: str | None = None,
    lista: str | None = None,
    preciocero: bool | None = None,
    stockcero: bool | None = None,
    exacto: bool | None = None,
    base_datos: str = "ECOMMECS"
) -> List[Dict]:
    try:
        headers = get_headers_with_db(base_datos)
        url = f"{API_BASE_URL}/ConsultaStockYPrecios/"
        params = {"limit": limite if limite else 5000}
        if query: params["query"] = query
        if lista: params["lista"] = lista
        if preciocero is not None: params["preciocero"] = preciocero
        if stockcero is not None: params["stockcero"] = stockcero
        if exacto is not None: params["exacto"] = exacto

        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        return [procesar_articulo_para_exportacion(art, base_datos) for art in articulos]
    except Exception as e:
        return [{"Error": f"Error al obtener datos de stock y precios: {str(e)}"}]

