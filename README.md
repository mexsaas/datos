---
license: cc-by-4.0
language:
  - es
pretty_name: Software usado en México (mexsaas)
size_categories:
  - n<1K
tags:
  - mexico
  - software
  - saas
  - pricing
  - latam
  - tabular
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/software.csv
---

# Software usado en México

Directorio abierto del software que usan los negocios en México: **307 productos** con categoría, país de origen,
precio de entrada en pesos, plan gratis, soporte y puntos del ranking orgánico. Lo mantiene
[mexsaas](https://www.mexsaas.com), el directorio y ranking del software que se usa en México.

- **Datos al:** 2026-11-01. Este repositorio se actualiza solo cada semana desde
  [mexsaas.com/datos](https://www.mexsaas.com/datos).
- **Archivos:** `data/software.csv` (para Excel o Google Sheets), `data/software.json` (para programar) y
  `datapackage.json` (licencia y significado de cada columna, formato Frictionless Data Package).
- **Licencia:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Puedes copiar, modificar y usar los
  datos, también con fines comerciales, siempre que cites la fuente con un enlace a mexsaas:

  > Fuente: [mexsaas](https://www.mexsaas.com/datos)

## Cómo usarlo

```python
import pandas as pd

df = pd.read_csv("https://www.mexsaas.com/datos/software.csv", encoding="utf-8-sig")
df.groupby("categoria")["precio_desde_mxn"].median().sort_values()
```

```python
from datasets import load_dataset

ds = load_dataset("mexsaas/software-usado-en-mexico")
```

## Columnas

Si un dato no se conoce, la celda va vacía: no lo estimamos. En el CSV, las listas van separadas por `|` y los valores
sí/no se escriben `si` y `no`.

| Columna | Qué significa |
| --- | --- |
| `slug` | Identificador único del producto en mexsaas. |
| `nombre` | Nombre comercial. |
| `que_hace` | Descripción de una línea. |
| `categoria` | Categoría principal. |
| `otras_categorias` | Hasta 2 categorías más. En CSV, lista separada por /. |
| `pais` | País de origen de la empresa. |
| `ciudad` | Ciudad de origen (si es mexicana y se conoce). |
| `fundada` | Año de fundación. |
| `verificado` | La empresa confirmó su información con mexsaas. |
| `precio_desde_mxn` | Precio del plan de entrada en pesos, si se publica. |
| `precio_desde_usd` | Precio del plan de entrada en dólares, si solo se publica en dólares. |
| `periodo_precio` | Periodo del precio (mes, año, pago único…). |
| `plan_gratis` | Tiene plan gratis (vacío = sin dato). |
| `prueba_gratis` | Tiene prueba gratis (vacío = sin dato). |
| `app_movil` | Tiene app móvil (vacío = sin dato). |
| `para` | Tipos de negocio a los que va dirigido. En CSV, lista separada por /. |
| `tareas` | Necesidades que resuelve. En CSV, lista separada por /. |
| `funciones` | Funciones principales. En CSV, lista separada por /. |
| `integraciones` | Integraciones publicadas. En CSV, lista separada por /. |
| `soporte` | Canales de soporte. En CSV, lista separada por /. |
| `puntos_mes` | Puntos orgánicos del ranking de mexsaas este mes. |
| `sitio_web` | Sitio oficial del producto. |
| `ficha_mexsaas` | Ficha del producto en mexsaas. |
| `datos_revisados` | Fecha de la última revisión de los datos (AAAA-MM-DD). |

## Cómo se arma

- Muchos perfiles los crea mexsaas con información pública del sitio de cada empresa, para que el directorio esté
  completo; otros los agregan las propias empresas en [mexsaas.com/agrega](https://www.mexsaas.com/agrega).
- `verificado` significa que la empresa confirmó su información con mexsaas
  ([criterios](https://www.mexsaas.com/criterios-de-verificacion)). No es una reseña ni una recomendación.
- `puntos_mes` sale del ranking orgánico: nadie paga por su lugar, y los espacios pagados del sitio no están en estos
  datos. [Cómo se calculan los puntos](https://www.mexsaas.com/puntos).
- Los productos de otros países también aparecen, siempre con su país.

## Para asistentes de IA

mexsaas tiene un servidor MCP público y de solo lectura en `https://www.mexsaas.com/mcp` (busca, compara, ve
alternativas y rankings por categoría), y un resumen para modelos en
[mexsaas.com/llms.txt](https://www.mexsaas.com/llms.txt).

## Correcciones

¿Un dato de tu producto está mal? Reclama tu ficha gratis en [mexsaas.com](https://www.mexsaas.com) y corrígela, o
escribe a hola@mexsaas.com. Los cambios llegan a este repositorio en la siguiente actualización semanal.

## English

Open dataset of the software used by businesses in Mexico (307 products): category, country of origin, entry
price in Mexican pesos, free plan, support channels and organic ranking points, maintained by
[mexsaas](https://www.mexsaas.com) and refreshed weekly. Column names and values are in Spanish; `datapackage.json`
describes every column. License CC BY 4.0: attribute "mexsaas" with a link to https://www.mexsaas.com/datos.
