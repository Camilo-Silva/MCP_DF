# server.py
from mcp.server.fastmcp import FastMCP
import httpx
import json
from prettytable import PrettyTable
import pandas as pd
from tabulate import tabulate
from typing import Optional, List, Dict, Any
import copy

# Create an MCP server
mcp = FastMCP("Demo")

# Configuración global para la API de Dragonfish
API_BASE_URL = "http://192.168.0.3:8009/api.Dragonfish"
API_HEADERS = {
    "accept": "application/json",
    "IdCliente": "TOKENAFUDEMO",
    "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvIjoiQURNSU4iLCJwYXNzd29yZCI6IjA2NDMwNWNmNDgwNTgxMTA1NjVkNDFiMjE1NDNiYzkyYWI0YjBjZGI4ODNlMTY1YjhiNDVmZDlmN2FlMTZlM2YiLCJleHAiOiIxODQ2MzQwMzQzIn0.IROROsh-IByUuGtFHWrFMcLGQZJxTrXmNCIydwywxvY"
}

# Función para obtener los headers de la API con la base de datos especificada
def get_headers_with_db(base_datos: str = "ECOMMECS") -> Dict[str, str]:
    """
    Obtiene los headers para la API con la base de datos especificada.
    
    Args:
        base_datos: Nombre de la base de datos a usar (por defecto ECOMMECS)
        
    Returns:
        Headers con la base de datos incluida
    """
    # Crear una copia de los headers para no modificar los globales
    headers = copy.deepcopy(API_HEADERS)
    headers["BaseDeDatos"] = base_datos
    return headers

@mcp.tool()
def listar_bases_datos() -> str:
    """
    Lista todas las bases de datos disponibles en el sistema.
    
    Returns:
        Una tabla formateada con las bases de datos disponibles
    """
    try:
        # Hacer la petición para obtener las bases de datos
        url = f"{API_BASE_URL}/BaseDeDatos/"
        response = httpx.get(url, headers=API_HEADERS)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = ["Código", "Descripción", "Activa"]
        
        # Obtener resultados
        bases_datos = data.get("Resultados", [])
        
        # Llenar tabla
        for bd in bases_datos:
            table.add_row([
                bd.get("Codigo", ""),
                bd.get("Descripcion", ""),
                "Sí" if bd.get("Activa", False) else "No"
            ])
        
        # Configurar la tabla
        table.align = "l"
        
        total = len(bases_datos)
        
        return f"Total de bases de datos: {total}\n\n{table.get_string()}"
    except Exception as e:
        return f"Error al obtener las bases de datos: {str(e)}"

# Add an addition tool
@mcp.tool()
def sum(a: int, b: int) -> int:
    """Suma dos numeros enteros"""
    return a + b

@mcp.tool()
def analizar_archivo(ruta: str) -> str:
    """Analiza un archivo y devuelve su contenido"""
    try:
        with open(ruta, 'r') as file:
            contenido = file.read()
        return f"Contenido del archivo {ruta}:\n{contenido}"
    except FileNotFoundError:
        return f"Archivo {ruta} no encontrado."
    except Exception as e:
        return f"Error al leer el archivo {ruta}: {str(e)}"

@mcp.tool()
def buscar_repos(query: str) -> str:
    """Busca repositorios en GitHub"""
    url = f"https://api.github.com/search/repositories?q={query}"
    try:
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()
        return f"Repositorios encontrados: {data['total_count']}"
    except httpx.RequestError as e:
        return f"Error de conexión: {str(e)}"
    except httpx.HTTPStatusError as e:
        return f"Error HTTP: {str(e)}"

@mcp.tool()
def listar_articulos(limite: Optional[int] = None, base_datos: str = "ECOMMECS") -> str:
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
        response = httpx.get(url, headers=headers)
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
def listar_articulos_con_familia(limite: Optional[int] = None, base_datos: str = "ECOMMECS") -> str:
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
        response = httpx.get(url, headers=headers)
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
        response = httpx.get(url, headers=headers)
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
        resultado = f"## Información del artículo: {codigo}\n\n"
        resultado += f"**Descripción**: {articulo_encontrado.get('Descripcion', '')}\n"
        resultado += f"**Familia**: {articulo_encontrado.get('Familia', '')}\n"
        resultado += f"**Tipo de artículo**: {articulo_encontrado.get('TipodeArticulo', '')}\n"
        resultado += f"**Línea**: {articulo_encontrado.get('Linea', '')}\n"
        resultado += f"**Categoría**: {articulo_encontrado.get('CategoriaDeArticulo', '')}\n"
        resultado += f"**Proveedor**: {articulo_encontrado.get('Proveedor', '')}\n"
        resultado += f"**Importado**: {'Sí' if articulo_encontrado.get('Importado') else 'No'}\n"
        
        # Agregar información adicional si existe
        if articulo_encontrado.get("DescripcionAdicional"):
            resultado += f"**Descripción adicional**: {articulo_encontrado.get('DescripcionAdicional')}\n"
        
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
def listar_stock_articulo(codigo_articulo: str, base_datos: str = "ECOMMECS") -> str:
    """
    Lista el stock disponible de un artículo específico con sus combinaciones de color y talle.
    
    Args:
        codigo_articulo: Código del artículo a consultar
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con el stock disponible
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        # Primero obtenemos información del artículo
        url = f"{API_BASE_URL}/StockArticulo/{codigo_articulo}/"
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if not data or "Resultados" not in data or not data["Resultados"]:
            return f"No se encontró stock para el artículo {codigo_articulo}"
        
        # Crear tabla
        table = PrettyTable()
        table.field_names = ["Artículo", "Descripción", "Color", "Talle", "Stock"]
        
        # Obtener resultados
        stock_items = data.get("Resultados", [])
        
        # Llenar tabla
        for item in stock_items:
            table.add_row([
                item.get("Articulo", ""),
                item.get("ArticuloDetalle", ""),
                item.get("ColorDetalle", ""),
                item.get("Talle", ""),
                item.get("Stock", 0)
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.align["Stock"] = "r"  # Alinear stock a la derecha
        
        total = len(stock_items)
        
        return f"Stock para el artículo {codigo_articulo} - Total combinaciones: {total}\n\n{table.get_string()}"
        
    except Exception as e:
        return f"Error al obtener el stock del artículo: {str(e)}"

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
        response = httpx.get(url, headers=headers)
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
        response = httpx.get(url, headers=headers)
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
        response = httpx.get(url, headers=headers)
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

if __name__ == "__main__":
    mcp.run()