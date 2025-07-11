import httpx
from prettytable import PrettyTable
from server import mcp
from utils.api_helpers import get_headers_with_db, API_BASE_URL

@mcp.tool()
def listar_articulos(limite: int | None = None, base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los artículos con su código y descripción.
    
    Args:
        limite: Número máximo de artículos a mostrar (opcio        # Leyenda de campos actualizada
        resultado += "\n\n📋 **LEYENDA DE CAMPOS EXPANDIDA:**\n"
        resultado += "🔸 **Básicos**: Código, Descripción, DescAdicional\n"
        resultado += "🔸 **Tipificaciones**: Familia + DescFamilia, Tipo + DescTipo, Línea + DescLínea, Grupo + DescGrupo, Categoría + DescCategoría, Material + DescMaterial, Clasificación + DescClasificación\n"
        resultado += "🔸 **Generales**: Proveedor + DescProveedor, UM + DescUM, Temporada + DescTemporada, Año, Importado, Peso, Marca\n"
        resultado += "🔸 **Configuraciones**: Comportamiento, TipoAgrup, NoDevol, RestDesc, ReqCC, NoEcomm, SoloPromo\n"
        resultado += "🔸 **Fiscales**: CondIVAVent, %IVAVent, CondIVAComp, %IVAComp, %ImpInt, Nomenclador, PercIVA\n"
        resultado += "🔸 **Condicionales**: PaletaCol, CurvaTall, NoComercial, RestArt, ImprDespach\n"
        resultado += "🔸 **E-commerce**: DescEcomm, DescHTML, Largo, Ancho, Alto, Imagen\n"
        resultado += "\n💡 **Nota**: Ahora incluye descripciones detalladas para Tipificaciones y Generales\n"     base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
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
def obtener_detalle_articulo(codigo: str, base_datos: str = "ECOMMECS") -> str:
    """
    Obtiene información detallada de un artículo específico por su código.
    Incluye todas las tipificaciones con sus descripciones completas.
    
    Args:
        codigo: Código del artículo a buscar
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Información detallada del artículo en formato legible con todas las tipificaciones
    """
    try:
        # Obtener headers con la base de datos especificada
        headers = get_headers_with_db(base_datos)
            
        # Obtener el artículo específico
        url = f"{API_BASE_URL}/Articulo/"
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
            return f"❌ No se encontró ningún artículo con el código **{codigo}** en la base de datos **{base_datos}**"
        
        # Función helper para obtener descripción de tipificaciones
        def obtener_descripcion_tipificacion(endpoint: str, codigo_tipif: str) -> str:
            if not codigo_tipif:
                return "No asignado"
            try:
                desc_url = f"{API_BASE_URL}/{endpoint}/"
                desc_response = httpx.get(desc_url, headers=headers, params={"limit": 1000})
                desc_response.raise_for_status()
                desc_data = desc_response.json()
                
                # Definir el campo a usar según el endpoint
                campo_descripcion = "Nombre" if endpoint == "Proveedor" else "Descripcion"
                
                for item in desc_data.get("Resultados", []):
                    if item.get("Codigo") == codigo_tipif:
                        return item.get(campo_descripcion, "Sin descripción")
                return "Código no encontrado"
            except:
                return "Error al obtener descripción"
        
        # Crear representación detallada del artículo
        resultado = f"# 📋 Detalle Completo del Artículo: **{codigo}**\n"
        resultado += f"**Base de datos:** {base_datos}\n\n"
        
        # ═══ INFORMACIÓN BÁSICA ═══
        resultado += "## 🏷️ **INFORMACIÓN BÁSICA**\n"
        resultado += f"**Código:** {articulo_encontrado.get('Codigo', '')}\n"
        resultado += f"**Descripción:** {articulo_encontrado.get('Descripcion', 'Sin descripción')}\n"
        if articulo_encontrado.get("DescripcionAdicional"):
            resultado += f"**Descripción adicional:** {articulo_encontrado.get('DescripcionAdicional')}\n"
        
        # ═══ TIPIFICACIONES COMPLETAS ═══
        resultado += f"\n## 🏗️ **TIPIFICACIONES**\n"
        
        # Familia
        familia_cod = articulo_encontrado.get('Familia', '')
        familia_desc = obtener_descripcion_tipificacion("Familia", familia_cod)
        resultado += f"**� Familia:** {familia_cod} - {familia_desc}\n"
        
        # Tipo de Artículo
        tipo_cod = articulo_encontrado.get('TipodeArticulo', '')
        tipo_desc = obtener_descripcion_tipificacion("Tipodearticulo", tipo_cod)
        resultado += f"**📦 Tipo de Artículo:** {tipo_cod} - {tipo_desc}\n"
        
        # Línea
        linea_cod = articulo_encontrado.get('Linea', '')
        linea_desc = obtener_descripcion_tipificacion("Linea", linea_cod)
        resultado += f"**🏪 Línea:** {linea_cod} - {linea_desc}\n"
        
        # Grupo
        grupo_cod = articulo_encontrado.get('Grupo', '')
        grupo_desc = obtener_descripcion_tipificacion("Grupo", grupo_cod)
        resultado += f"**📂 Grupo:** {grupo_cod} - {grupo_desc}\n"
        
        # Categoría de Artículo
        categoria_cod = articulo_encontrado.get('CategoriaDeArticulo', '')
        categoria_desc = obtener_descripcion_tipificacion("Categoriadearticulo", categoria_cod)
        resultado += f"**🏷️ Categoría:** {categoria_cod} - {categoria_desc}\n"
        
        # Material
        material_cod = articulo_encontrado.get('Material', '')
        material_desc = obtener_descripcion_tipificacion("Material", material_cod)
        resultado += f"**🧱 Material:** {material_cod} - {material_desc}\n"
        
        # Clasificación
        clasificacion_cod = articulo_encontrado.get('Clasificacion', '')
        clasificacion_desc = obtener_descripcion_tipificacion("Clasificacionarticulo", clasificacion_cod)
        resultado += f"**🔖 Clasificación:** {clasificacion_cod} - {clasificacion_desc}\n"
        
        # ═══ INFORMACIÓN COMERCIAL ═══
        resultado += f"\n## � **INFORMACIÓN COMERCIAL**\n"
        
        # Proveedor
        proveedor_cod = articulo_encontrado.get('Proveedor', '')
        proveedor_desc = obtener_descripcion_tipificacion("Proveedor", proveedor_cod)
        resultado += f"**� Proveedor:** {proveedor_cod} - {proveedor_desc}\n"
        
        # Unidad de Medida
        um_cod = articulo_encontrado.get('UnidadDeMedida', '')
        um_desc = obtener_descripcion_tipificacion("Unidaddemedida", um_cod)
        resultado += f"**📏 Unidad de Medida:** {um_cod} - {um_desc}\n"
        
        # Temporada
        temporada_cod = articulo_encontrado.get('Temporada', '')
        temporada_desc = obtener_descripcion_tipificacion("Temporada", temporada_cod)
        resultado += f"**🌤️ Temporada:** {temporada_cod} - {temporada_desc}\n"
        
        # Paleta de Colores
        paleta_cod = articulo_encontrado.get('Paletadecolores', '')
        paleta_desc = obtener_descripcion_tipificacion("Paletadecolores", paleta_cod)
        resultado += f"**🎨 Paleta de Colores:** {paleta_cod} - {paleta_desc}\n"
        
        # Curva de Talles
        curva_cod = articulo_encontrado.get('Curvadetalles', '')
        curva_desc = obtener_descripcion_tipificacion("Curvadetalles", curva_cod)
        resultado += f"**📐 Curva de Talles:** {curva_cod} - {curva_desc}\n"
        
        # ═══ INFORMACIÓN ADICIONAL ═══
        resultado += f"\n## ℹ️ **INFORMACIÓN ADICIONAL**\n"
        resultado += f"**🌍 Importado:** {'Sí' if articulo_encontrado.get('Importado') else 'No'}\n"
        resultado += f"**📅 Año:** {articulo_encontrado.get('Ano', 'No especificado')}\n"
        resultado += f"**⚖️ Peso:** {articulo_encontrado.get('Peso', 'No especificado')}\n"
        resultado += f"**🏷️ Marca:** {articulo_encontrado.get('Marca', 'No especificada')}\n"
        
        # ═══ CONFIGURACIONES ═══
        resultado += f"\n## ⚙️ **CONFIGURACIONES**\n"
        resultado += f"**🔄 Comportamiento:** {articulo_encontrado.get('Comportamiento', 'No especificado')}\n"
        resultado += f"**📋 No Permite Devoluciones:** {'Sí' if articulo_encontrado.get('NoPermiteDevoluciones') else 'No'}\n"
        resultado += f"**💸 Restringir Descuentos:** {'Sí' if articulo_encontrado.get('RestringirDescuentos') else 'No'}\n"
        resultado += f"**� No Publicar en E-commerce:** {'Sí' if articulo_encontrado.get('NoPublicarEnEcommerce') else 'No'}\n"
        resultado += f"**🎁 Solo Promo y Kit:** {'Sí' if articulo_encontrado.get('SoloPromoYKit') else 'No'}\n"
        
        # ═══ INFORMACIÓN FISCAL ═══
        resultado += f"\n## 💰 **INFORMACIÓN FISCAL**\n"
        resultado += f"**📊 Condición IVA Ventas:** {articulo_encontrado.get('CondicionIvaVentas', 'No especificada')}\n"
        resultado += f"**📈 % IVA Ventas:** {articulo_encontrado.get('PorcentajeIvaVentas', 0)}%\n"
        resultado += f"**� Condición IVA Compras:** {articulo_encontrado.get('CondicionIvaCompras', 'No especificada')}\n"
        resultado += f"**📊 % IVA Compras:** {articulo_encontrado.get('PorcentajeIvaCompras', 0)}%\n"
        resultado += f"**🏛️ Nomenclador:** {articulo_encontrado.get('Nomenclador', 'No especificado')}\n"
        
        # ═══ E-COMMERCE ═══
        if any([articulo_encontrado.get('DescEcommerce'), articulo_encontrado.get('Largo'), 
                articulo_encontrado.get('Ancho'), articulo_encontrado.get('Alto'), 
                articulo_encontrado.get('Imagen')]):
            resultado += f"\n## 🛒 **E-COMMERCE**\n"
            if articulo_encontrado.get('DescEcommerce'):
                resultado += f"**� Descripción E-commerce:** {articulo_encontrado.get('DescEcommerce')}\n"
            if articulo_encontrado.get('Largo'):
                resultado += f"**📏 Dimensiones:** {articulo_encontrado.get('Largo', 0)} x {articulo_encontrado.get('Ancho', 0)} x {articulo_encontrado.get('Alto', 0)}\n"
            if articulo_encontrado.get('Imagen'):
                resultado += f"**�️ Imagen:** {articulo_encontrado.get('Imagen')}\n"
        
        # ═══ COMPONENTES (SI ES KIT) ═══
        if articulo_encontrado.get("ParticipantesDetalle") and len(articulo_encontrado.get("ParticipantesDetalle")) > 0:
            resultado += f"\n## 📦 **COMPONENTES DEL KIT**\n"
            
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
        return f"❌ Error al obtener el detalle del artículo: {str(e)}"

@mcp.tool()
def listar_articulos_completos(limite: int | None = None, base_datos: str = "ECOMMECS") -> str:
    """
    Lista todos los artículos con todos los campos disponibles de la API de Dragonfish según swagger.json.
    Incluye campos básicos, tipificaciones, datos fiscales, e-commerce y información adicional.
    Consulta endpoints específicos para obtener las descripciones reales de tipificaciones.
    
    Args:
        limite: Número máximo de artículos a mostrar (opcional)
        base_datos: Base de datos a consultar (por defecto ECOMMECS)
    
    Returns:
        Una tabla formateada con todos los campos de los artículos disponibles en la API
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
        
        # Obtener resultados
        articulos = data.get("Resultados", [])
        if limite:
            articulos = articulos[:limite]
        
        # Función helper para obtener descripción de endpoint específico
        def obtener_descripcion(endpoint: str, codigo: str) -> str:
            try:
                if not codigo:
                    return ""
                desc_url = f"{API_BASE_URL}/{endpoint}/"
                desc_response = httpx.get(desc_url, headers=headers, params={"limit": 1000})
                desc_response.raise_for_status()
                desc_data = desc_response.json()
                
                # Definir el campo a usar según el endpoint
                campo_descripcion = "Nombre" if endpoint == "Proveedor" else "Descripcion"
                
                for item in desc_data.get("Resultados", []):
                    if item.get("Codigo") == codigo:
                        descripcion = item.get(campo_descripcion, "")
                        return descripcion[:40] + "..." if len(descripcion) > 40 else descripcion
                return ""
            except:
                return ""
        
        # Crear tabla completa con todos los campos como columnas
        table = PrettyTable()
        table.field_names = [
            "Código", "Descripción", "DescAdicional", 
            "Familia", "DescFamilia", "Tipo", "DescTipo", "Línea", "DescLínea", 
            "Grupo", "DescGrupo", "Categoría", "DescCategoría", "Material", "DescMaterial", 
            "Clasificación", "DescClasificación", "Proveedor", "DescProveedor", 
            "UM", "DescUM", "Temporada", "DescTemporada", "Año", "Importado", "Peso", "Marca",
            "Comportamiento", "TipoAgrup", "NoDevol", "RestDesc", "ReqCC", "NoEcomm", "SoloPromo", 
            "CondIVAVent", "%IVAVent", "CondIVAComp", "%IVAComp", "%ImpInt", "Nomenclador", "PercIVA", 
            "PaletaCol", "DescPaletaCol", "CurvaTall", "DescCurvaTall", "NoComercial", "RestArt", "ImprDespach", 
            "DescEcomm", "DescHTML", "Largo", "Ancho", "Alto", "Imagen"
        ]
        
        # Llenar tabla con todos los campos
        for articulo in articulos:
            table.add_row([
                # Básicos
                articulo.get("Codigo", ""),
                articulo.get("Descripcion", "")[:30] + "..." if len(articulo.get("Descripcion", "")) > 30 else articulo.get("Descripcion", ""),
                articulo.get("DescripcionAdicional", "")[:20] + "..." if len(articulo.get("DescripcionAdicional", "")) > 20 else articulo.get("DescripcionAdicional", ""),
                
                # Tipificaciones
                articulo.get("Familia", ""),
                obtener_descripcion("Familia", articulo.get("Familia", "")),
                articulo.get("TipodeArticulo", ""),
                obtener_descripcion("Tipodearticulo", articulo.get("TipodeArticulo", "")),
                articulo.get("Linea", ""),
                obtener_descripcion("Linea", articulo.get("Linea", "")),
                articulo.get("Grupo", ""),
                obtener_descripcion("Grupo", articulo.get("Grupo", "")),
                articulo.get("CategoriaDeArticulo", ""),
                obtener_descripcion("Categoriadearticulo", articulo.get("CategoriaDeArticulo", "")),
                articulo.get("Material", ""),
                obtener_descripcion("Material", articulo.get("Material", "")),
                articulo.get("Clasificacion", ""),
                obtener_descripcion("Clasificacionarticulo", articulo.get("Clasificacion", "")),
                
                # Generales
                articulo.get("Proveedor", ""),
                obtener_descripcion("Proveedor", articulo.get("Proveedor", "")),
                articulo.get("UnidadDeMedida", ""),
                obtener_descripcion("Unidaddemedida", articulo.get("UnidadDeMedida", "")),
                articulo.get("Temporada", ""),
                obtener_descripcion("Temporada", articulo.get("Temporada", "")),
                str(articulo.get("Ano", "")) if articulo.get("Ano") else "",
                "Sí" if articulo.get("Importado") else "No",
                str(articulo.get("Peso", "")) if articulo.get("Peso") else "",
                articulo.get("Marca", ""),
                
                # Configuraciones
                str(articulo.get("Comportamiento", "")),
                str(articulo.get("TipoAgrupamientoPublicaciones", "")),
                "Sí" if articulo.get("NoPermiteDevoluciones") else "No",
                "Sí" if articulo.get("RestringirDescuentos") else "No",
                str(articulo.get("RequiereCCosto", "")),
                "Sí" if articulo.get("NoPublicarEnEcommerce") else "No",
                "Sí" if articulo.get("SoloPromoYKit") else "No",
                
                # Fiscales
                str(articulo.get("CondicionIvaVentas", "")),
                f"{articulo.get('PorcentajeIvaVentas', 0)}%" if articulo.get('PorcentajeIvaVentas') else "",
                str(articulo.get("CondicionIvaCompras", "")),
                f"{articulo.get('PorcentajeIvaCompras', 0)}%" if articulo.get('PorcentajeIvaCompras') else "",
                f"{articulo.get('PorcentajeImpuestoInterno', 0)}%" if articulo.get('PorcentajeImpuestoInterno') else "",
                articulo.get("Nomenclador", ""),
                str(articulo.get("PercepcionIvaRG5329", "")),
                
                # Condicionales
                articulo.get("Paletadecolores", ""),
                obtener_descripcion("Paletadecolores", articulo.get("Paletadecolores", "")),
                articulo.get("Curvadetalles", ""),
                obtener_descripcion("Curvadetalles", articulo.get("Curvadetalles", "")),
                str(articulo.get("NoComercializable", "")),
                str(articulo.get("RestringirArticulo", "")),
                "Sí" if articulo.get("ImprimeDespacho") else "No",
                
                # E-commerce
                articulo.get("DescEcommerce", "")[:15] + "..." if len(articulo.get("DescEcommerce", "")) > 15 else articulo.get("DescEcommerce", ""),
                articulo.get("DescEcommerceHTML", "")[:10] + "..." if len(articulo.get("DescEcommerceHTML", "")) > 10 else articulo.get("DescEcommerceHTML", ""),
                str(articulo.get("Largo", "")) if articulo.get("Largo") else "",
                str(articulo.get("Ancho", "")) if articulo.get("Ancho") else "",
                str(articulo.get("Alto", "")) if articulo.get("Alto") else "",
                articulo.get("Imagen", "")[:25] + "..." if len(articulo.get("Imagen", "")) > 25 else articulo.get("Imagen", "")
            ])
        
        # Configurar la tabla
        table.align = "l"
        table.max_width["Descripción"] = 30
        table.max_width["DescAdicional"] = 20
        table.max_width["DescFamilia"] = 15
        table.max_width["DescTipo"] = 15
        table.max_width["DescLínea"] = 15
        table.max_width["DescGrupo"] = 15
        table.max_width["DescCategoría"] = 15
        table.max_width["DescMaterial"] = 15
        table.max_width["DescClasificación"] = 15
        table.max_width["DescProveedor"] = 15
        table.max_width["DescUM"] = 15
        table.max_width["DescTemporada"] = 15
        table.max_width["DescPaletaCol"] = 15
        table.max_width["DescCurvaTall"] = 15
        table.max_width["DescEcomm"] = 15
        table.max_width["DescHTML"] = 10
        table.max_width["Imagen"] = 25
        
        total = data.get("TotalRegistros", 0)
        mostrados = len(articulos)
        
        resultado = f"📋 **Tabla Completa de Artículos - BD: {base_datos}**\n\n"
        resultado += f"Total de artículos: {total}, Mostrando: {mostrados}\n"
        resultado += f"📊 Mostrando {len(table.field_names)} campos por artículo\n\n"
        resultado += table.get_string()
        
        # Leyenda de campos
        resultado += "\n\n� **LEYENDA DE CAMPOS:**\n"
        resultado += "🔸 **Básicos**: Código, Descripción, DescAdicional\n"
        resultado += "� **Tipificaciones**: Familia, Tipo, Línea, Grupo, Categoría, Material, Clasificación\n"
        resultado += "🔸 **Generales**: Proveedor, UM, Temporada, Año, Importado, Peso, Marca\n"
        resultado += "� **Configuraciones**: Comportamiento, TipoAgrup, NoDevol, RestDesc, ReqCC, NoEcomm, SoloPromo\n"
        resultado += "� **Fiscales**: CondIVAVent, %IVAVent, CondIVAComp, %IVAComp, %ImpInt, Nomenclador, PercIVA\n"
        resultado += "� **Condicionales**: PaletaCol, CurvaTall, NoComercial, RestArt, ImprDespach\n"
        resultado += "� **E-commerce**: DescEcomm, DescHTML, Largo, Ancho, Alto, Imagen\n"
        
        return resultado
        
    except Exception as e:
        return f"Error al obtener los artículos completos: {str(e)}"
