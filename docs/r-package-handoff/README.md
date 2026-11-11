# Spainpolls R Package Handoff

Esta carpeta documenta la API publica de Spain Electoral Polls para que otro agente pueda implementar un paquete de R llamado `spainpolls`.

El objetivo no es explicar el codigo interno de FastAPI ni el ETL. El objetivo es describir el contrato HTTP/JSON que debe consumir un cliente R con `httr2`, y como transformar las respuestas en `tibble`s limpios.

Documentacion relacionada ya existente:

- `api/README.md`: guia operativa general de la API.
- `docs/api-handoff/`: documentacion de traspaso previa para construir la API desde el esquema y reglas de negocio.

Esta carpeta resume y actualiza ese material contra la implementacion actual.

## Orden recomendado de lectura

1. `api-overview.md`
2. `endpoints-reference.md`
3. `query-parameters.md`
4. `response-schemas.md`
5. `pagination.md`
6. `error-handling.md`
7. `examples-for-r-client.md`
8. `openapi-notes.md`

## Ficheros

- `api-overview.md`: resumen de la API, version, base URL, autenticacion, limites y convenciones.
- `endpoints-reference.md`: referencia endpoint por endpoint con wrappers R sugeridos.
- `query-parameters.md`: tabla central de parametros de consulta.
- `response-schemas.md`: schemas JSON, campos estables y conversiones recomendadas a R.
- `pagination.md`: contrato de paginacion y estrategia `collect_all`.
- `error-handling.md`: errores HTTP, validacion y recomendaciones para `cli::cli_abort()`.
- `examples-for-r-client.md`: ejemplos HTTP, JSON y llamadas R sugeridas.
- `openapi-notes.md`: como usar `/docs`, `/redoc` y `/openapi.json`.
- `openapi.json`: copia generada del contrato OpenAPI actual, si esta presente.

## Endpoints publicos disponibles

- `GET /health`
- `GET /api/v1/elections`
- `GET /api/v1/pollsters`
- `GET /api/v1/parties`
- `GET /api/v1/polls`
- `GET /api/v1/polls/{poll_id}`
- `GET /api/v1/results`
- `GET /api/v1/timeseries`

Todos los endpoints implementados son publicos, de solo lectura, y devuelven JSON. No hay autenticacion en v1.

## Endpoints que no deberia usar el paquete R inicial

- No hay endpoints administrativos implementados en v1. `ENABLE_ADMIN_ENDPOINTS` existe en configuracion, pero no activa rutas en la implementacion actual.
- `GET /api/v1/polls/{poll_id}/results` no esta implementado. Los resultados de una encuesta concreta se obtienen dentro de `GET /api/v1/polls/{poll_id}` en el campo `results`, o en formato long con `GET /api/v1/results`.
- El paquete R inicial no debe depender de campos internos como `row_hash`, `poll_signature`, `raw_html`, `raw_wikitext`, `payload_json`, `wiki_revision_id` o `identity_confidence`. La API publica actual no los expone.

## Documentacion OpenAPI

En local, con el servidor arrancado:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

En produccion, si el dominio esta activo:

- Swagger UI: `https://pollsdb.spainelectoralproject.com/docs`
- ReDoc: `https://pollsdb.spainelectoralproject.com/redoc`
- OpenAPI JSON: `https://pollsdb.spainelectoralproject.com/openapi.json`

Tambien se ha generado una copia estatica en `docs/r-package-handoff/openapi.json`.

## Validacion realizada

El 2026-07-02 se comprobo la implementacion local contra estos comandos:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/elections
curl "http://localhost:8000/api/v1/polls?limit=1"
curl "http://localhost:8000/api/v1/results?limit=1"
curl "http://localhost:8000/api/v1/timeseries?limit=1"
```

Todos respondieron con JSON y los endpoints coincidieron con la forma documentada. Tambien se genero `openapi.json` desde la app FastAPI actual.

Se ejecuto `pytest` en `api/`; los 13 tests publicos se saltaron porque la base PostgreSQL de test no estaba disponible para esa suite. La validacion HTTP local anterior si encontro una API y base de datos disponibles en `localhost:8000`.
