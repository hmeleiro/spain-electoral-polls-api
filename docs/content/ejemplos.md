---
title: "Ejemplos de uso"
description: "Recetas para consultar y paginar datos desde curl, Python y R."
---

Todos los ejemplos usan la API de producción. No hace falta enviar credenciales ni headers especiales.

## curl

Lista las diez encuestas más recientes de una elección:

```bash
curl "https://polls.spainelectoralproject.com/api/v1/polls?election_key=congreso_espana_2027&limit=10"
```

Consulta estimaciones de varios partidos repitiendo el parámetro:

```bash
curl "https://polls.spainelectoralproject.com/api/v1/results?party=psoe&party=pp&limit=100"
```

Comprueba el estado del servicio:

```bash
curl "https://polls.spainelectoralproject.com/health"
```

## Python

```python
import requests

url = "https://polls.spainelectoralproject.com/api/v1/timeseries"
params = {
    "election_key": "congreso_espana_2027",
    "party": ["psoe", "pp", "vox", "sumar"],
    "date_from": "2026-01-01",
    "date_field": "auto",
    "limit": 1000,
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()
payload = response.json()

print(f"{payload['total']} observaciones")
for point in payload["items"][:5]:
    print(point["date"], point["short_name"], point["vote_share"])
```

### Recorrer todas las páginas

```python
import requests

url = "https://polls.spainelectoralproject.com/api/v1/results"
limit = 1000
offset = 0
rows = []

while True:
    response = requests.get(
        url,
        params={"party": "psoe", "limit": limit, "offset": offset},
        timeout=30,
    )
    response.raise_for_status()
    page = response.json()
    rows.extend(page["items"])
    offset += page["limit"]
    if offset >= page["total"]:
        break

print(f"Descargadas {len(rows)} filas")
```

## R

Con `httr2`:

```r
library(httr2)

resp <- request(
  "https://polls.spainelectoralproject.com/api/v1/results"
) |>
  req_url_query(
    election_key = "congreso_espana_2027",
    party = "psoe",
    limit = 100
  ) |>
  req_perform() |>
  resp_body_json(simplifyVector = TRUE)

resultados <- resp$items
head(resultados)
```

Para repetir un parámetro con `httr2`, usa `.multi = "explode"`:

```r
resp <- request(
  "https://polls.spainelectoralproject.com/api/v1/results"
) |>
  req_url_query(
    party = c("psoe", "pp", "vox"),
    limit = 1000,
    .multi = "explode"
  ) |>
  req_perform() |>
  resp_body_json(simplifyVector = TRUE)
```

## JavaScript

La API puede consultarse directamente desde un navegador cuando el origen está permitido por CORS:

```js
const url = new URL(
  "https://polls.spainelectoralproject.com/api/v1/parties"
);
url.searchParams.set("election_key", "congreso_espana_2027");
url.searchParams.set("limit", "100");

const response = await fetch(url);
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const { items, total } = await response.json();

console.log(total, items);
```

## Citar la fuente original

Cuando presentes una encuesta concreta, usa `source_url` y `source_title` del recurso `/polls` para enlazar la publicación de origen. `fieldwork_start`, `fieldwork_end` y `sample_size` aportan el contexto metodológico mínimo para interpretar la estimación.
