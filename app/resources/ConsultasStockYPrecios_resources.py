# Constantes para los nombres de columnas comunes
COL_ARTICULO = "Artículo"
COL_DESCRIPCION = "Descripción"
COL_COLOR = "Color"
COL_COD_COLOR = "Cod.Color"
COL_TALLE = "Talle"
COL_COD_TALLE = "Cod.Talle"
COL_STOCK = "Stock"
COL_DISPONIBLE = "Disponible"
COL_PRECIO = "Precio"

from prettytable import PrettyTable
from typing import List, Dict

def crear_parametros_consulta(
    limite: int | None = None,
    query: str | None = None,
    lista: str | None = None,
    preciocero: bool | None = None,
    stockcero: bool | None = None,
    exacto: bool | None = None
) -> dict:
    """
    Crea los parámetros para la consulta de stock y precios.
    """
    params = {"limit": limite if limite else 5000}
    
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
        
    return params

def extraer_listas_precios(articulos: list) -> list:
    """
    Extrae y ordena las listas de precios disponibles en los artículos.
    """
    listas_disponibles = set()
    
    for articulo in articulos:
        precios_articulo = articulo.get("Precios", [])
        if precios_articulo and isinstance(precios_articulo, list):
            for precio_info in precios_articulo:
                lista_nombre = precio_info.get("Lista", "")
                if lista_nombre:
                    listas_disponibles.add(lista_nombre)
    
    return sorted(listas_disponibles)

def agrupar_articulos(articulos: list) -> dict:
    """
    Agrupa los artículos por código, color y talle.
    """
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
    
    return articulos_agrupados

def crear_tabla_stock_precios(articulos_agrupados: dict, listas_ordenadas: list) -> PrettyTable:
    """
    Crea y configura la tabla de stock y precios.
    """
    # Crear tabla dinámica con columnas de precios según las listas encontradas
    columnas_base = [
        COL_ARTICULO, COL_DESCRIPCION, COL_COD_COLOR, COL_COLOR, 
        COL_COD_TALLE, COL_TALLE, COL_STOCK, COL_DISPONIBLE
    ]
    columnas_precios = [f"Precio {lista}" for lista in listas_ordenadas]
    
    table = PrettyTable()
    table.field_names = columnas_base + columnas_precios
    
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
    table.align[COL_STOCK] = "r"
    table.align[COL_DISPONIBLE] = "r"
    
    # Alinear columnas de precios a la derecha
    for lista in listas_ordenadas:
        table.align[f"Precio {lista}"] = "r"
    
    return table

def procesar_articulo_para_exportacion(articulo, base_datos):
    """
    Procesa un artículo para exportación, extrayendo sus datos y precios.
    """
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

def filtrar_articulo_por_codigo(articulos: list, codigo_articulo: str) -> list:
    """
    Filtra los artículos por un código específico.
    """
    return [art for art in articulos if art.get("Articulo") == codigo_articulo]

def crear_encabezado_articulo(articulo, codigo_articulo: str) -> str:
    """
    Crea el encabezado con la información básica del artículo.
    """
    resultado = f"## 📦💰 Stock y Precios del Artículo: {codigo_articulo}\n\n"
    resultado += f"**📋 Descripción**: {articulo.get('ArticuloDescripcion', '')}\n"
    
    if articulo.get('ArticuloDescripcionAdicional'):
        resultado += f"**📝 Descripción adicional**: {articulo.get('ArticuloDescripcionAdicional')}\n"
    
    resultado += "\n"
    return resultado

def crear_fila_articulo(articulo, listas_ordenadas):
    """
    Crea una fila de datos para un artículo específico.
    """
    stock = articulo.get("Stock", 0)
    disponible = articulo.get("Disponible", 0)
    
    # Datos base de la fila
    fila_base = [
        articulo.get("Articulo", ""),
        articulo.get("ArticuloDescripcion", ""),
        articulo.get("ColorDescripcion", ""),
        articulo.get("Color", ""),
        articulo.get("TalleDescripcion", ""),
        articulo.get("Talle", ""),
        stock,
        disponible
    ]
    
    # Procesar precios
    precios_fila = obtener_precios_articulo(articulo, listas_ordenadas)
    
    return fila_base + precios_fila, stock, disponible

def obtener_precios_articulo(articulo, listas_ordenadas):
    """
    Obtiene los precios de un artículo según las listas ordenadas.
    """
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
        precios_fila.append(f"${precio_valor}" if precio_valor > 0 else "-")
    
    return precios_fila

def crear_tabla_articulo_especifico(articulos_filtrados: list, listas_ordenadas: list) -> tuple:
    """
    Crea la tabla detallada para un artículo específico y calcula totales.
    """
    # Crear tabla detallada
    table = PrettyTable()
    
    # Definir las columnas base
    columnas_base = [
        COL_ARTICULO, COL_DESCRIPCION, COL_COLOR, COL_COD_COLOR, 
        COL_TALLE, COL_COD_TALLE, COL_STOCK, COL_DISPONIBLE
    ]
    
    # Agregar columnas de precios dinámicamente
    columnas_precios = [f"Precio {lista}" for lista in listas_ordenadas]
    
    # Establecer los nombres de las columnas
    table.field_names = columnas_base + columnas_precios
    
    total_stock = 0
    total_disponible = 0
    
    # Procesar cada artículo
    for articulo in articulos_filtrados:
        fila, stock, disponible = crear_fila_articulo(articulo, listas_ordenadas)
        table.add_row(fila)
        total_stock += stock
        total_disponible += disponible
    
    # Configurar alineación de la tabla
    table.align = "l"
    table.align[COL_STOCK] = "r"
    table.align[COL_DISPONIBLE] = "r"
    
    # Alinear columnas de precios
    for lista in listas_ordenadas:
        table.align[f"Precio {lista}"] = "r"
    
    return table, total_stock, total_disponible

def crear_tabla_articulos_sin_stock(articulos_sin_stock):
    """
    Crea una tabla para mostrar los artículos sin stock.
    """
    table = PrettyTable()
    table.field_names = [
        COL_ARTICULO, COL_DESCRIPCION, COL_COLOR, COL_TALLE, COL_PRECIO
    ]
    
    # Llenar tabla
    for articulo in articulos_sin_stock:
        table.add_row([
            articulo.get("Articulo", ""),
            articulo.get("ArticuloDescripcion", "")[:35] + "..." if len(articulo.get("ArticuloDescripcion", "")) > 35 else articulo.get("ArticuloDescripcion", ""),
            articulo.get("ColorDescripcion", ""),
            articulo.get("TalleDescripcion", ""),
            f"${articulo.get('Precio', 0)}"
        ])
    
    # Configurar alineación de la tabla
    table.align = "l"
    table.align[COL_PRECIO] = "r"
    
    return table

def obtener_precios_disponibles(articulo):
    """
    Extrae los precios disponibles para un artículo.
    """
    resultado = ""
    precios_articulo = articulo.get("Precios", [])
    
    if precios_articulo and isinstance(precios_articulo, list):
        for precio_info in precios_articulo:
            lista_nombre = precio_info.get("Lista", "")
            precio_valor = precio_info.get("Precio", 0)
            if lista_nombre:
                resultado += f"- {lista_nombre}: ${precio_valor}\n"
    
    return resultado

def crear_resumen_articulo(total_stock: int, total_disponible: int, articulos_filtrados: list, 
                          listas_ordenadas: list, primer_articulo) -> str:
    """
    Crea el resumen con totales y precios disponibles.
    """
    resultado = "\n\n**📊 Resumen Total:**\n"
    resultado += f"- Stock total: {total_stock}\n"
    resultado += f"- Disponible total: {total_disponible}\n"
    resultado += f"- Combinaciones: {len(articulos_filtrados)}\n"
    
    # Mostrar todas las listas de precios disponibles dinámicamente
    if listas_ordenadas:
        resultado += "\n**💰 Listas de Precios Disponibles:**\n"
        resultado += obtener_precios_disponibles(primer_articulo)
    
    return resultado
