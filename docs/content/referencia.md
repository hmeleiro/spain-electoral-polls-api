---
title: "Referencia de la API"
description: "Endpoints, filtros, paginación y modelos de respuesta de la versión 1."
---

<div class="api-facts">
  <div><span>Base URL</span><strong>https://polls.spainelectoralproject.com</strong></div>
  <div><span>Versión</span><strong>/api/v1</strong></div>
  <div><span>Formato</span><strong>application/json</strong></div>
</div>

La API es pública, de solo lectura y no requiere autenticación. La documentación interactiva generada desde el esquema OpenAPI también está disponible en [Swagger UI](https://polls.spainelectoralproject.com/docs).

## Endpoints

<div class="endpoint-list">
  <div class="endpoint-row"><b>GET</b><code>/health</code><span>Estado del servicio y de la base de datos.</span></div>
  <div class="endpoint-row"><b>GET</b><code>/api/v1/elections</code><span>Catálogo de elecciones.</span></div>
  <div class="endpoint-row"><b>GET</b><code>/api/v1/pollsters</code><span>Catálogo de encuestadoras.</span></div>
  <div class="endpoint-row"><b>GET</b><code>/api/v1/parties</code><span>Catálogo normalizado de partidos.</span></div>
  <div class="endpoint-row"><b>GET</b><code>/api/v1/polls</code><span>Listado de encuestas y sus metadatos.</span></div>
  <div class="endpoint-row"><b>GET</b><code>/api/v1/polls/{poll_id}</code><span>Detalle de una encuesta con todos sus resultados.</span></div>
  <div class="endpoint-row"><b>GET</b><code>/api/v1/results</code><span>Resultados de encuestas en formato largo.</span></div>
  <div class="endpoint-row"><b>GET</b><code>/api/v1/timeseries</code><span>Observaciones fechadas preparadas para series temporales.</span></div>
</div>

## Paginación

Todos los endpoints de listado usan `limit` y `offset`. `limit` admite valores entre 1 y 1.000 y su valor predeterminado es 100. La respuesta mantiene siempre la misma envoltura:

```json
{
  "items": [],
  "limit": 100,
  "offset": 0,
  "total": 0
}
```

Para recorrer una colección, incrementa `offset` en el valor de `limit` hasta que `offset + limit` sea igual o superior a `total`.

## Catálogos {#catalogos}

### Elecciones

`GET /api/v1/elections`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `territory_code` | string | Código de territorio exacto. |
| `election_type` | string | Tipo de elección exacto. |
| `limit` | integer | Registros por página, de 1 a 1.000. |
| `offset` | integer | Registros que se omiten desde el inicio. |

Cada elemento contiene `id`, `election_key`, `election_type`, `territory_code`, `election_name` y `election_date`.

### Encuestadoras

`GET /api/v1/pollsters`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `election_key` | string, repetible | Limita el catálogo a una o varias elecciones. |
| `territory_code` | string | Limita por territorio. |
| `active_only` | boolean | Solo encuestadoras con actividad pública; por defecto `true`. |
| `limit`, `offset` | integer | Paginación. |

Devuelve la clave y nombre normalizados de cada encuestadora junto a `poll_count`.

### Partidos

`GET /api/v1/parties`

Admite `election_key` repetible, `territory_code`, `active_only`, `limit` y `offset`. Incluye `party_key`, nombre, sigla, color, orden de visualización y número de encuestas públicas.

## Encuestas {#encuestas}

### Listado

`GET /api/v1/polls`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `election_key` | string, repetible | Una o varias elecciones. |
| `territory_code` | string | Territorio exacto. |
| `pollster_key` | string, repetible | Clave normalizada de encuestadora. |
| `pollster` | string, repetible | Clave o nombre de encuestadora. |
| `media` | string, repetible | Coincidencia parcial con el medio. |
| `fieldwork_start_from`, `fieldwork_start_to` | date | Rango de inicio de trabajo de campo. |
| `fieldwork_end_from`, `fieldwork_end_to` | date | Rango de fin de trabajo de campo. |
| `publication_date_from`, `publication_date_to` | date | Rango de publicación. |
| `identity_status` | string | Estado de identificación exacto. |
| `include_manual_review` | boolean | Incluye registros pendientes de revisión manual. |
| `include_inactive` | boolean | Incluye registros inactivos. |
| `limit`, `offset` | integer | Paginación. |

Por defecto se excluyen encuestas inactivas y pendientes de revisión manual. Las fechas usan el formato ISO `AAAA-MM-DD`.

### Detalle

`GET /api/v1/polls/{poll_id}`

Devuelve los metadatos de la encuesta y un array `results` con partido, voto estimado y horquilla de escaños. Responde `404` cuando el identificador no existe o el registro no es público.

## Resultados {#resultados}

`GET /api/v1/results`

El formato largo devuelve una fila por combinación encuesta–partido. Es útil para análisis tabular y exportaciones.

| Grupo | Parámetros disponibles |
|---|---|
| Contexto | `election_key`, `territory_code` |
| Encuestadora | `pollster_key`, `pollster`, `media` |
| Partido | `party_key`, `party` |
| Fechas | `fieldwork_end_from`, `fieldwork_end_to`, `publication_date_from`, `publication_date_to` |
| Publicación | `include_manual_review`, `include_inactive` |
| Paginación | `limit`, `offset` |

Los parámetros `election_key`, `pollster_key`, `pollster`, `media`, `party_key` y `party` pueden repetirse para consultar varios valores.

## Series temporales {#series-temporales}

`GET /api/v1/timeseries`

Comparte los filtros de elección, territorio, encuestadora, medio y partido. Añade:

| Parámetro | Valores | Descripción |
|---|---|---|
| `date_from` | date | Fecha mínima, inclusive. |
| `date_to` | date | Fecha máxima, inclusive. |
| `date_field` | `auto`, `fieldwork_end`, `publication_date` | Campo usado como fecha. |

`date_field=auto`, el valor predeterminado, usa el fin del trabajo de campo y recurre a la fecha de publicación cuando falta. Cada punto incluye fecha, encuesta, encuestadora, partido, voto estimado, escaños y metadatos de presentación.

## Errores

Los parámetros inválidos producen un `422` con el detalle estructurado de FastAPI. Un recurso no encontrado produce un `404`:

```json
{
  "detail": "Poll not found"
}
```

Una colección sin coincidencias no es un error: devuelve `200`, `total: 0` e `items: []`.

> Para integraciones automáticas, consulta también el contrato canónico en `/openapi.json`. Esta web resume el comportamiento; OpenAPI refleja siempre la versión desplegada.
