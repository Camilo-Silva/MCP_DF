# Servidor MCP para API Dragonfish

Este proyecto implementa un servidor MCP (Model Context Protocol) que se integra con la API de Dragonfish. Permite realizar consultas sobre artículos, stock, precios, y más, directamente desde un entorno compatible con MCP como Claude.

## Características Principales

- **Integración con Dragonfish**: Utiliza un archivo `swagger.json` para interactuar con la API de Dragonfish de forma estructurada.
- **Herramientas MCP**: Provee un conjunto de herramientas para consultar información de la API:
  - Listado de artículos con descripciones.
  - Listado de artículos con detalles de familia y tipo.
  - Consulta de stock y precios para un artículo específico.
  - Obtención de detalles completos de un artículo.
  - Listado de colores, talles y familias disponibles.
  - Consulta de artículos sin stock.
  - Consulta general de stock y precios con filtros.
  - Exportación de resultados a formato Excel.
- **Selección de Base de Datos**: La mayoría de las herramientas permiten especificar la base de datos (`ECOMMECS`, `TANGO`, etc.) en cada consulta.
- **Salida Formateada**: Las respuestas se presentan en tablas bien formateadas para una fácil lectura en consolas o clientes de chat.

## Requisitos Previos

- Python 3.8 o superior.
- Git.

## Configuración del Entorno

1.  **Clonar el Repositorio**:
    ```bash
    git clone <URL-del-repositorio>
    cd mcp-server-demo
    ```

2.  **Crear un Entorno Virtual** (recomendado):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .\.venv\Scripts\activate
    ```

3.  **Instalar Dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar Variables de Entorno**:
    Crea un archivo llamado `.env` en la raíz del proyecto. Este archivo **no** será subido a Git gracias al `.gitignore`. Añade las siguientes variables con tus credenciales:

    ```ini
    # URL base de la API de Dragonfish
    API_BASE_URL=http://tu-servidor-dragonfish/api.Dragonfish

    # Credenciales de la API
    ID_CLIENTE=TU_ID_CLIENTE
    JW_TOKEN=TU_TOKEN_JWT
    ```

## Uso

Para iniciar el servidor MCP, ejecuta el siguiente comando desde la raíz del proyecto:

```bash
python main.py
```

El servidor comenzará a escuchar peticiones MCP. Ahora puedes conectarlo a tu cliente compatible (como Claude Desktop) y empezar a usar las herramientas.

## Referencia de Herramientas (Funciones)

Aquí hay una lista de las funciones disponibles a través de MCP:

- `listar_articulos(limite, base_datos)`
- `listar_articulos_con_familia(limite, base_datos)`
- `consultar_stock_articulo_especifico(codigo_articulo, base_datos)`
- `obtener_detalle_articulo(codigo, base_datos)`
- `listar_colores(base_datos)`
- `listar_talles(base_datos)`
- `listar_familias(base_datos)`
- `consultar_articulos_sin_stock(limite, base_datos)`
- `consultar_stock_y_precios(limite, query, lista, preciocero, stockcero, exacto, base_datos)`
- `exportar_datos_a_excel(data, nombre_archivo, nombre_hoja, incluir_resumen, columnas_numericas)`

### Ejemplo de Invocación

```python
# Ejemplo de cómo se invocaría una herramienta desde un cliente MCP
consultar_stock_articulo_especifico(codigo_articulo="XYZ123", base_datos="ECOMMECS")
```
