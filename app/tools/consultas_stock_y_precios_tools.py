import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL
from typing import List, Dict
from app.resources.consultas_stock_y_precios_resources import (
    crear_parametros_consulta,
    extraer_listas_precios,
    agrupar_articulos,
    crear_tabla_stock_precios,
    procesar_articulo_para_exportacion,
    filtrar_articulo_por_codigo,
    crear_encabezado_articulo,
    crear_tabla_articulo_especifico,
    crear_resumen_articulo,
    crear_tabla_articulos_sin_stock
)

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
        
        # Crear parámetros de consulta
        params = crear_parametros_consulta(limite, query, lista, preciocero, stockcero, exacto)
        
        # Realizar la consulta
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        
        # Extraer listas de precios
        listas_ordenadas = extraer_listas_precios(articulos)
        
        # Agrupar artículos
        articulos_agrupados = agrupar_articulos(articulos)
        
        # Crear tabla
        table = crear_tabla_stock_precios(articulos_agrupados, listas_ordenadas)
        
        # Preparar resultado
        total = data.get("TotalRegistros", 0)
        mostrados = len(articulos_agrupados)
        
        resultado = "💰📦 **Consulta de Stock y Precios**\n\n"
        resultado += f"Total de registros: {total}, Mostrando: {mostrados}\n\n"
        resultado += table.get_string()
        
        # Agregar información sobre las listas encontradas
        if listas_ordenadas:
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
        
        # Realizar la consulta
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        
        if not articulos:
            return f"No se encontró stock para el artículo {codigo_articulo}"
        
        # Filtrar solo el artículo específico
        articulos_filtrados = filtrar_articulo_por_codigo(articulos, codigo_articulo)
        
        if not articulos_filtrados:
            return f"No se encontró stock para el artículo {codigo_articulo}"
        
        # Obtener primer artículo para información básica
        primer_articulo = articulos_filtrados[0]
        
        # Crear encabezado con información del artículo
        resultado = crear_encabezado_articulo(primer_articulo, codigo_articulo)
        
        # Extraer listas de precios
        listas_ordenadas = extraer_listas_precios(articulos_filtrados)
        
        # Crear tabla y obtener totales
        tabla, total_stock, total_disponible = crear_tabla_articulo_especifico(articulos_filtrados, listas_ordenadas)
        resultado += tabla.get_string()
        
        # Agregar resumen con totales y precios
        resultado += crear_resumen_articulo(total_stock, total_disponible, articulos_filtrados, 
                                          listas_ordenadas, primer_articulo)
        
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
        
        # Realizar la consulta
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        
        # Filtrar solo los que realmente tienen stock 0
        articulos_sin_stock = [art for art in articulos if art.get("Stock", 0) == 0]
        
        # Crear tabla
        table = crear_tabla_articulos_sin_stock(articulos_sin_stock)
        
        # Preparar resultado
        total_original = data.get("TotalRegistros", 0)
        mostrados = len(articulos_sin_stock)
        
        resultado = "🚫📦 **Artículos Sin Stock**\n\n"
        resultado += f"Total sin stock encontrados: {mostrados} (de {total_original} registros consultados)\n\n"
        resultado += table.get_string()
        
        return resultado
        
    except Exception as e:
        return f"Error al consultar artículos sin stock: {str(e)}"

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
    """
    Obtiene datos en formato procesable de stock y precios para exportación o análisis.
    
    Args:
        limite: Número máximo de registros a obtener
        query: Filtro de búsqueda por texto
        lista: Filtro por lista de precios específica
        preciocero: Incluir artículos con precio cero
        stockcero: Incluir artículos con stock cero
        exacto: Búsqueda exacta
        base_datos: Base de datos a consultar
        
    Returns:
        Lista de diccionarios con datos de artículos procesados
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
        url = f"{API_BASE_URL}/ConsultaStockYPrecios/"
        
        # Crear parámetros de consulta
        params = crear_parametros_consulta(limite, query, lista, preciocero, stockcero, exacto)
        
        # Realizar la consulta
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
            
        # Procesar artículos para exportación
        return [procesar_articulo_para_exportacion(art, base_datos) for art in articulos]
    
    except Exception as e:
        return [{"Error": f"Error al obtener datos de stock y precios: {str(e)}"}]

