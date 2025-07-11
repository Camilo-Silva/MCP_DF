import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL

# Constantes para mensajes reutilizables
NO_ASIGNADO = "No asignado"
SIN_DESCRIPCION = "Sin descripción"
CODIGO_NO_ENCONTRADO = "Código no encontrado"
ERROR_OBTENER_DESCRIPCION = "Error al obtener descripción"

def obtener_descripcion_articulo(codigo_articulo: str, headers: dict) -> str:
    """
    Helper para obtener la descripción de un artículo específico.
    
    Args:
        codigo_articulo: Código del artículo
        headers: Headers con autenticación y base de datos
    
    Returns:
        Descripción del artículo o mensaje si no se encuentra
    """
    if not codigo_articulo:
        return NO_ASIGNADO
    
    try:
        url = f"{API_BASE_URL}/Articulo/"
        response = httpx.get(url, headers=headers, params={"limit": 1000})
        response.raise_for_status()
        data = response.json()
        
        for articulo in data.get("Resultados", []):
            if articulo.get("Codigo") == codigo_articulo:
                descripcion = articulo.get("Descripcion", SIN_DESCRIPCION)
                return descripcion[:40] + "..." if len(descripcion) > 40 else descripcion
        
        return CODIGO_NO_ENCONTRADO
    except Exception:
        return ERROR_OBTENER_DESCRIPCION

def obtener_descripcion_color(codigo_color: str, headers: dict) -> str:
    """
    Helper para obtener la descripción de un color específico.
    
    Args:
        codigo_color: Código del color
        headers: Headers con autenticación y base de datos
    
    Returns:
        Descripción del color o mensaje si no se encuentra
    """
    if not codigo_color:
        return NO_ASIGNADO
    
    try:
        url = f"{API_BASE_URL}/Color/"
        response = httpx.get(url, headers=headers, params={"limit": 1000})
        response.raise_for_status()
        data = response.json()
        
        for color in data.get("Resultados", []):
            if color.get("Codigo") == codigo_color:
                descripcion = color.get("Descripcion", SIN_DESCRIPCION)
                return descripcion[:20] + "..." if len(descripcion) > 20 else descripcion
        
        return CODIGO_NO_ENCONTRADO
    except Exception:
        return ERROR_OBTENER_DESCRIPCION

def obtener_descripcion_talle(codigo_talle: str, headers: dict) -> str:
    """
    Helper para obtener la descripción de un talle específico.
    
    Args:
        codigo_talle: Código del talle
        headers: Headers con autenticación y base de datos
    
    Returns:
        Descripción del talle o mensaje si no se encuentra
    """
    if not codigo_talle:
        return NO_ASIGNADO
    
    try:
        url = f"{API_BASE_URL}/Talle/"
        response = httpx.get(url, headers=headers, params={"limit": 1000})
        response.raise_for_status()
        data = response.json()
        
        for talle in data.get("Resultados", []):
            if talle.get("Codigo") == codigo_talle:
                descripcion = talle.get("Descripcion", SIN_DESCRIPCION)
                return descripcion[:15] + "..." if len(descripcion) > 15 else descripcion
        
        return CODIGO_NO_ENCONTRADO
    except Exception:
        return ERROR_OBTENER_DESCRIPCION

@mcp.tool()
def listar_equivalencias(limite: int | None = None, base_datos: str = "ECOMMECS") -> str:
    """
    Lista todas las equivalencias disponibles en el sistema con sus combinaciones de artículo, color y talle.
    Incluye las descripciones completas de cada elemento para mejor comprensión.
    
    Args:
        limite: Número máximo de equivalencias a mostrar (opcional)
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con las equivalencias y sus descripciones
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/Equivalencia/"
        # Si se especifica un límite, lo usamos; si no, obtenemos todas las equivalencias
        params = {"limit": limite if limite else 1000}
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Crear tabla con todos los campos relevantes
        table = PrettyTable()
        table.field_names = [
            "Código", "Artículo", "DescArt", "Color", "DescColor", 
            "Talle", "DescTalle", "Cantidad", "GTIN", "Observación"
        ]
        
        # Obtener resultados
        equivalencias = data.get("Resultados", [])
        if limite:
            equivalencias = equivalencias[:limite]
        
        # Llenar tabla con todas las equivalencias
        for equivalencia in equivalencias:
            # Obtener códigos
            codigo_art = equivalencia.get("Articulo", "")
            codigo_color = equivalencia.get("Color", "")
            codigo_talle = equivalencia.get("Talle", "")
            
            # Obtener descripciones usando los helpers
            desc_articulo = obtener_descripcion_articulo(codigo_art, headers)
            desc_color = obtener_descripcion_color(codigo_color, headers)
            desc_talle = obtener_descripcion_talle(codigo_talle, headers)
            
            # Formatear observación
            observacion = equivalencia.get("Observacion", "")
            if observacion and len(observacion) > 20:
                observacion = observacion[:20] + "..."
            
            table.add_row([
                equivalencia.get("Codigo", ""),
                codigo_art,
                desc_articulo,
                codigo_color,
                desc_color,
                codigo_talle,
                desc_talle,
                f"{equivalencia.get('Cantidad', 0):.2f}" if equivalencia.get('Cantidad') else "0.00",
                "Sí" if equivalencia.get("EsGTIN") else "No",
                observacion
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.max_width["DescArt"] = 25
        table.max_width["DescColor"] = 15
        table.max_width["DescTalle"] = 12
        table.max_width["Observación"] = 20
        
        total = data.get("TotalRegistros", 0)
        mostrados = len(equivalencias)
        
        resultado = f"📋 **Equivalencias - BD: {base_datos}**\n"
        resultado += "💡 Combinaciones de artículos con códigos equivalentes\n\n"
        resultado += f"Total de equivalencias: {total}, Mostrando: {mostrados}\n\n"
        resultado += table.get_string()
        
        # Leyenda de campos
        resultado += "\n\n📋 **LEYENDA DE CAMPOS:**\n"
        resultado += "🔸 **Código**: Código único de la equivalencia\n"
        resultado += "🔸 **Artículo**: Código del artículo + descripción completa\n"
        resultado += "🔸 **Color**: Código del color + descripción\n"
        resultado += "🔸 **Talle**: Código del talle + descripción\n"
        resultado += "🔸 **Cantidad**: Cantidad asociada a la equivalencia\n"
        resultado += "🔸 **GTIN**: Si cumple con código RG2904/10\n"
        resultado += "🔸 **Observación**: Notas adicionales sobre la equivalencia\n"
        resultado += "\n💡 **Nota**: Las equivalencias definen códigos alternativos para combinaciones específicas de artículo-color-talle\n"
        
        return resultado
        
    except Exception as e:
        return f"❌ Error al obtener las equivalencias: {str(e)}"

@mcp.tool()
def obtener_equivalencia_especifica(codigo: str, base_datos: str = "ECOMMECS") -> str:
    """
    Obtiene información detallada de una equivalencia específica por su código.
    
    Args:
        codigo: Código de la equivalencia a buscar
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Información detallada de la equivalencia en formato legible
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        url = f"{API_BASE_URL}/Equivalencia/"
        params = {"limit": 1000}
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Buscar la equivalencia por código
        equivalencia_encontrada = None
        for equivalencia in data.get("Resultados", []):
            if equivalencia.get("Codigo") == codigo:
                equivalencia_encontrada = equivalencia
                break
        
        if not equivalencia_encontrada:
            return f"❌ No se encontró ninguna equivalencia con el código **{codigo}** en la base de datos **{base_datos}**"
        
        # Obtener descripciones detalladas
        codigo_art = equivalencia_encontrada.get("Articulo", "")
        codigo_color = equivalencia_encontrada.get("Color", "")
        codigo_talle = equivalencia_encontrada.get("Talle", "")
        
        desc_articulo = obtener_descripcion_articulo(codigo_art, headers)
        desc_color = obtener_descripcion_color(codigo_color, headers)
        desc_talle = obtener_descripcion_talle(codigo_talle, headers)
        
        # Crear representación detallada
        resultado = f"# 📋 Detalle de Equivalencia: **{codigo}**\n"
        resultado += f"**Base de datos:** {base_datos}\n\n"
        
        # ═══ INFORMACIÓN BÁSICA ═══
        resultado += "## 🏷️ **INFORMACIÓN BÁSICA**\n"
        resultado += f"**Código de Equivalencia:** {equivalencia_encontrada.get('Codigo', '')}\n"
        resultado += f"**Tipo de Agrupamiento:** {equivalencia_encontrada.get('TipoAgrupamientoPublicaciones', 'No especificado')}\n"
        
        # ═══ COMBINACIÓN ═══
        resultado += "\n## 🔗 **COMBINACIÓN**\n"
        resultado += f"**📦 Artículo:** {codigo_art} - {desc_articulo}\n"
        resultado += f"**🎨 Color:** {codigo_color} - {desc_color}\n"
        resultado += f"**📐 Talle:** {codigo_talle} - {desc_talle}\n"
        
        # ═══ DETALLES ADICIONALES ═══
        resultado += "\n## ℹ️ **DETALLES ADICIONALES**\n"
        resultado += f"**📊 Cantidad:** {equivalencia_encontrada.get('Cantidad', 0):.2f}\n"
        resultado += f"**🏷️ Es GTIN:** {'Sí' if equivalencia_encontrada.get('EsGTIN') else 'No'} (Código RG2904/10)\n"
        
        if equivalencia_encontrada.get("Observacion"):
            resultado += f"**📝 Observaciones:** {equivalencia_encontrada.get('Observacion')}\n"
        
        # ═══ AGRUPAMIENTO DE PUBLICACIONES ═══
        if equivalencia_encontrada.get("Agrupublidetalle"):
            resultado += "\n## 📑 **AGRUPAMIENTO DE PUBLICACIONES**\n"
            agrup_table = PrettyTable()
            agrup_table.field_names = ["Detalle"]
            
            for detalle in equivalencia_encontrada.get("Agrupublidetalle", []):
                agrup_table.add_row([str(detalle)])
            
            agrup_table.align = "l"
            resultado += agrup_table.get_string()
        
        return resultado
        
    except Exception as e:
        return f"❌ Error al obtener el detalle de la equivalencia: {str(e)}"
