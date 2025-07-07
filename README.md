# MCP Server Demo - Dragonfish API

Este proyecto es una demostración de un servidor MCP (Model Context Protocol) que integra con la API de Dragonfish para consultar y mostrar información sobre artículos, familias, stock, colores y talles, con la capacidad de especificar la base de datos por consulta.

## Características

- Integración con API de Dragonfish basada en Swagger
- Herramientas MCP para consultar:
  - Artículos
  - Artículos con información de familia
  - Stock de un artículo específico
  - Detalle de un artículo
  - Colores disponibles
  - Talles disponibles
  - Familias de artículos
  - Bases de datos disponibles
  - Stock total de todos los artículos
- Todas las herramientas soportan la especificación de base de datos
- Formateo de salida en tablas para Claude Desktop

## Opciones de Demostración

Este proyecto ofrece tres modos diferentes para probar las herramientas MCP:

1. **Servidor MCP para Claude Desktop**
   - Permite usar las herramientas directamente desde Claude Desktop
   - Requiere configuración de Claude Desktop

2. **Cliente de Línea de Comandos**
   - Interfaz sencilla para probar desde la terminal
   - No requiere configuración adicional

3. **Servidor Web**
   - Interfaz web para probar desde cualquier navegador o chat
   - Incluye documentación API automática con OpenAPI

## Requisitos

- Python 3.8 o superior
- Paquetes Python:
  - fastmcp
  - httpx
  - pandas
  - tabulate
  - prettytable
  - fastapi (para servidor web)
  - uvicorn (para servidor web)

## Inicio Rápido

### Usando PowerShell (Windows)

El script `Demo-MCP.ps1` permite ejecutar cualquiera de los modos de demostración:

```powershell
# Instalar dependencias e iniciar cliente CLI
.\Demo-MCP.ps1 -Mode cli -InstallDeps

# Iniciar servidor web
.\Demo-MCP.ps1 -Mode web

# Iniciar ambos (servidor web y cliente CLI)
.\Demo-MCP.ps1 -Mode all
```

### Manual (Cualquier Sistema Operativo)

1. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

2. Para usar con Claude Desktop:
   ```
   python server.py
   ```

3. Para cliente de línea de comandos:
   ```
   # En una terminal, iniciar el servidor MCP
   python server.py
   
   # En otra terminal, usar el cliente CLI
   python cli_demo.py
   ```

4. Para servidor web:
   ```
   # En una terminal, iniciar el servidor MCP
   python server.py
   
   # En otra terminal, iniciar el servidor web
   python web_demo.py
   ```

## Documentación Detallada

- [README_WEB_DEMO.md](README_WEB_DEMO.md) - Información detallada sobre el servidor web de demostración

## Ejemplos de Uso

### Claude Desktop

```python
listar_articulos(limite=10, base_datos="ECOMMECS")
listar_articulos_con_familia(limite=5, base_datos="ECOMMECS")
listar_stock_articulo(codigo_articulo="1001", base_datos="ECOMMECS")
obtener_detalle_articulo(codigo="1001", base_datos="ECOMMECS")
listar_colores()
listar_talles()
listar_familias()
listar_bases_datos()
listar_stock_todos_articulos(limite=10, base_datos="ECOMMECS")
```

### Cliente CLI

```bash
python cli_demo.py listar_articulos --limite 10 --base_datos ECOMMECS
python cli_demo.py listar_stock_articulo --codigo_articulo 1001 --base_datos ECOMMECS
python cli_demo.py obtener_detalle_articulo --codigo 1001 --base_datos ECOMMECS
python cli_demo.py listar_stock_todos_articulos --limite 10 --base_datos ECOMMECS
python cli_demo.py listar_bases_datos
```

### Servidor Web

Navega a `http://localhost:8080` para ver la interfaz web, o usa los endpoints directamente:

```
http://localhost:8080/api/listar_articulos?limite=10&base_datos=ECOMMECS
http://localhost:8080/api/listar_stock_articulo?codigo_articulo=1001&base_datos=ECOMMECS
http://localhost:8080/api/obtener_detalle_articulo?codigo=1001&base_datos=ECOMMECS
http://localhost:8080/api/listar_stock_todos_articulos?limite=10&base_datos=ECOMMECS
http://localhost:8080/api/listar_bases_datos
```

## Notas

- Este es un proyecto de demostración y no está destinado para uso en producción.
- El servidor web temporal no incluye autenticación ni otras medidas de seguridad.
- Las salidas están formateadas para ser legibles tanto en terminales como en interfaces de chat como Claude Desktop.
