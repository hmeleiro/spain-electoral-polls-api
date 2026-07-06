# Endpoints Reference

All implemented endpoints are public and unauthenticated in v1. They are read-only and use `GET`.

Production base URL: `https://polls.spainelectoralproject.com`

Local base URL: `http://localhost:8000`

## GET /health

### Purpose

Check that the API process is alive and whether the database healthcheck succeeds.

### Suggested R wrapper

`check_api_health()`

### Query parameters

None.

### Path parameters

None.

### Response shape

Simple object, not paginated.

### Example request

```bash
curl "http://localhost:8000/health"
```

### Example response

```json
{
  "status": "ok",
  "service": "spain-electoral-polls-api",
  "database": "ok"
}
```

If the process is alive but the database healthcheck fails, the implementation returns HTTP 200 with `"database": "unavailable"`.

### Notes for R client

Return a small one-row `tibble` or a named list. Do not use this endpoint as a guarantee that data endpoints will succeed; use it as a preflight check.

## GET /api/v1/elections

### Purpose

List elections known by the API.

### Suggested R wrapper

`get_elections()`

### Query parameters

- `territory_code`
- `election_type`
- `limit`
- `offset`

### Path parameters

None.

### Response shape

Paginated response with `items`, `limit`, `offset`, `total`. Each item is an `Election`.

### Example request

```bash
curl "http://localhost:8000/api/v1/elections?territory_code=ES&limit=10"
```

### Example response

```json
{
  "items": [
    {
      "id": 1,
      "election_key": "congreso_espana_2027",
      "election_type": "general",
      "territory_code": "ES",
      "election_name": "Congreso de los Diputados 2027",
      "election_date": null
    }
  ],
  "limit": 10,
  "offset": 0,
  "total": 1
}
```

### Notes for R client

Return a tibble with one row per election. Convert `election_date` to `Date`. Use `election_key` as the stable filter value in other functions.

## GET /api/v1/pollsters

### Purpose

List pollsters and the number of polls attached to each pollster.

### Suggested R wrapper

`get_pollsters()`

### Query parameters

- `election_key`
- `territory_code`
- `active_only`
- `limit`
- `offset`

### Path parameters

None.

### Response shape

Paginated response. Each item is a `Pollster`.

### Example request

```bash
curl "http://localhost:8000/api/v1/pollsters?election_key=congreso_espana_2027"
```

### Example response

```json
{
  "items": [
    {
      "id": 10,
      "pollster_key": "40db",
      "pollster_name": "40dB",
      "poll_count": 18
    }
  ],
  "limit": 100,
  "offset": 0,
  "total": 1
}
```

### Notes for R client

Return a tibble. `active_only` defaults to `true`; this counts only active, non-manual-review polls. Use `pollster_key` for exact filters. `pollster_name` is a label.

## GET /api/v1/parties

### Purpose

List the canonical party catalog, enriched with the number of public polls currently attached to each party when available.

### Suggested R wrapper

`get_parties()`

### Query parameters

- `election_key`
- `territory_code`
- `active_only`
- `limit`
- `offset`

### Path parameters

None.

### Response shape

Paginated response. Each item is a `Party`.

### Example request

```bash
curl "http://localhost:8000/api/v1/parties?election_key=congreso_espana_2027"
```

### Example response

```json
{
  "items": [
    {
      "party_key": "psoe",
      "party_name": "Partido Socialista Obrero Espanol",
      "short_name": "PSOE",
      "territory_code": "ES",
      "color_hex": "#e30613",
      "display_order": 10,
      "is_active": true,
      "poll_count": 42
    }
  ],
  "limit": 100,
  "offset": 0,
  "total": 1
}
```

### Notes for R client

Return a tibble. Use `party_key` as the stable identifier. `short_name` is the preferred compact display label; `color_hex` and `display_order` are suitable defaults for visualizations.

## GET /api/v1/polls

### Purpose

List polls with poll-level metadata.

### Suggested R wrapper

`get_polls()`

### Query parameters

- `election_key`
- `territory_code`
- `pollster_key`
- `pollster`
- `media`
- `fieldwork_start_from`
- `fieldwork_start_to`
- `fieldwork_end_from`
- `fieldwork_end_to`
- `publication_date_from`
- `publication_date_to`
- `identity_status`
- `include_manual_review`
- `include_inactive`
- `limit`
- `offset`

### Path parameters

None.

### Response shape

Paginated response. Each item is a `Poll summary`.

### Example request

```bash
curl "http://localhost:8000/api/v1/polls?election_key=congreso_espana_2027&limit=2"
```

### Example response

```json
{
  "items": [
    {
      "id": 101,
      "election_key": "congreso_espana_2027",
      "election_name": "Congreso de los Diputados 2027",
      "territory_code": "ES",
      "pollster_key": "40db",
      "pollster_name": "40dB",
      "media": "El Pais",
      "fieldwork_start": "2026-06-01",
      "fieldwork_end": "2026-06-05",
      "publication_date": "2026-06-07",
      "sample_size": 1200,
      "turnout": null,
      "lead": 3.2,
      "source_url": "https://example.com/active",
      "source_title": "Active poll",
      "identity_status": "exact",
      "first_seen_at": "2026-06-07T10:15:00",
      "is_active": true
    }
  ],
  "limit": 2,
  "offset": 0,
  "total": 1
}
```

### Notes for R client

This endpoint is paginated. The R client should support `limit`, `offset` and `collect_all`.

Return one row per poll. Convert `fieldwork_start`, `fieldwork_end`, and `publication_date` to `Date`; convert `first_seen_at` to `POSIXct` or keep as character in the first implementation; convert `turnout` and `lead` to numeric; convert `is_active` to logical.

Do not surface internal fields if added later. `identity_status` is public metadata, but package examples should default to public-clean data by leaving `include_manual_review=FALSE`.

## GET /api/v1/polls/{poll_id}

### Purpose

Fetch one poll by numeric id, including nested poll results.

### Suggested R wrapper

`get_poll(poll_id)` or `get_poll_detail(poll_id)`

### Query parameters

- `include_manual_review`
- `include_inactive`

### Path parameters

- `poll_id`: integer poll id.

### Response shape

Simple object, not paginated. Same fields as `Poll summary`, plus `results`.

### Example request

```bash
curl "http://localhost:8000/api/v1/polls/101"
```

### Example response

```json
{
  "id": 101,
  "election_key": "congreso_espana_2027",
  "election_name": "Congreso de los Diputados 2027",
  "territory_code": "ES",
  "pollster_key": "40db",
  "pollster_name": "40dB",
  "media": "El Pais",
  "fieldwork_start": "2026-06-01",
  "fieldwork_end": "2026-06-05",
  "publication_date": "2026-06-07",
  "sample_size": 1200,
  "turnout": null,
  "lead": 3.2,
  "source_url": "https://example.com/active",
  "source_title": "Active poll",
  "identity_status": "exact",
  "first_seen_at": "2026-06-07T10:15:00",
  "is_active": true,
  "results": [
    {
      "party_key": "pp",
      "party_raw": "PP",
      "party_name": "Partido Popular",
      "short_name": "PP",
      "color_hex": "#1d84ce",
      "display_order": 20,
      "vote_share": 28.0,
      "seats_min": null,
      "seats_max": null
    },
    {
      "party_key": "psoe",
      "party_raw": "PSOE",
      "party_name": "Partido Socialista Obrero Espanol",
      "short_name": "PSOE",
      "color_hex": "#e30613",
      "display_order": 10,
      "vote_share": 31.2,
      "seats_min": null,
      "seats_max": null
    }
  ]
}
```

### Notes for R client

The API returns a nested JSON object. The R package can either return a list with `poll` and `results` tibbles, or expose two helpers: one for poll metadata and one for nested results. Convert date and numeric fields as above.

If the poll exists but is inactive or in manual review, it is hidden by default and returns 404 unless the relevant `include_*` query flag is set.

## GET /api/v1/results

### Purpose

Return poll results in long format: one row per poll and party.

### Suggested R wrapper

`get_results()`

### Query parameters

- `election_key`
- `territory_code`
- `pollster_key`
- `pollster`
- `media`
- `party_key`
- `party`
- `fieldwork_end_from`
- `fieldwork_end_to`
- `publication_date_from`
- `publication_date_to`
- `include_manual_review`
- `include_inactive`
- `limit`
- `offset`

### Path parameters

None.

### Response shape

Paginated response. Each item is a `Poll result` in long format.

### Example request

```bash
curl "http://localhost:8000/api/v1/results?party=psoe&limit=2"
```

### Example response

```json
{
  "items": [
    {
      "party_key": "psoe",
      "party_raw": "PSOE",
      "party_name": "Partido Socialista Obrero Espanol",
      "short_name": "PSOE",
      "color_hex": "#e30613",
      "display_order": 10,
      "vote_share": 31.2,
      "seats_min": null,
      "seats_max": null,
      "poll_id": 101,
      "date": "2026-06-05",
      "election_key": "congreso_espana_2027",
      "pollster_key": "40db",
      "pollster_name": "40dB",
      "media": "El Pais",
      "fieldwork_end": "2026-06-05",
      "publication_date": "2026-06-07",
      "sample_size": 1200
    }
  ],
  "limit": 2,
  "offset": 0,
  "total": 1
}
```

### Notes for R client

This is the preferred endpoint for analytical tables in R. Return one row per party result. Convert `date`, `fieldwork_end`, and `publication_date` to `Date`; `vote_share` to numeric; seats and sample size to integer.

The `date` field is `coalesce(fieldwork_end, publication_date)` in the current implementation.

## GET /api/v1/timeseries

### Purpose

Return party vote-share points over time for charts and time-series analysis.

### Suggested R wrapper

`get_timeseries()`

### Query parameters

- `election_key`
- `territory_code`
- `pollster_key`
- `pollster`
- `media`
- `party_key`
- `party`
- `date_from`
- `date_to`
- `date_field`
- `include_manual_review`
- `include_inactive`
- `limit`
- `offset`

### Path parameters

None.

### Response shape

Paginated response. Each item is a `Timeseries item`.

### Example request

```bash
curl "http://localhost:8000/api/v1/timeseries?party=psoe&date_field=auto&limit=2"
```

### Example response

```json
{
  "items": [
    {
      "date": "2026-06-05",
      "poll_id": 101,
      "pollster_key": "40db",
      "pollster_name": "40dB",
      "media": "El Pais",
      "sample_size": 1200,
      "party_key": "psoe",
      "party_raw": "PSOE",
      "party_name": "Partido Socialista Obrero Espanol",
      "short_name": "PSOE",
      "color_hex": "#e30613",
      "display_order": 10,
      "vote_share": 31.2
    }
  ],
  "limit": 2,
  "offset": 0,
  "total": 1
}
```

### Notes for R client

Return one row per point. Convert `date` to `Date` and `vote_share` to numeric.

`date_field` allowed values are `auto`, `fieldwork_end`, and `publication_date`. In `auto`, the API uses `coalesce(fieldwork_end, publication_date)`.

## Pending Endpoint: GET /api/v1/polls/{poll_id}/results

This endpoint was mentioned in planning material but is not implemented in the current API. The R package should not call it.

Use one of these instead:

- `GET /api/v1/polls/{poll_id}` and unnest the `results` field.
- `GET /api/v1/results` and filter by available poll metadata. There is currently no `poll_id` query parameter on `/api/v1/results`.
