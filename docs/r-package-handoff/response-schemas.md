# Response Schemas

JSON fields use `snake_case`. Dates are strings in `YYYY-MM-DD`; datetimes are ISO-8601 strings. Numeric values serialized from database decimals are JSON numbers.

## Health response

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `status` | string | no | API process status. Currently `ok`. | character |
| `service` | string | no | Service identifier. | character |
| `database` | string | no | Database health: `ok` or `unavailable`. | character |

Example:

```json
{
  "status": "ok",
  "service": "spain-electoral-polls-api",
  "database": "ok"
}
```

## Paginated response

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `items` | array | no | Page rows. Element schema depends on endpoint. | list, then tibble |
| `limit` | integer | no | Requested page size. | integer |
| `offset` | integer | no | Requested offset. | integer |
| `total` | integer | no | Total matching rows before pagination. | integer |

Example:

```json
{
  "items": [],
  "limit": 100,
  "offset": 0,
  "total": 0
}
```

## Election

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `id` | integer | no | Database election id. Stable enough for joins within one API instance, but prefer `election_key`. | integer |
| `election_key` | string | no | Stable election key. | character |
| `election_type` | string | no | Election type. | character |
| `territory_code` | string | no | Territory code. | character |
| `election_name` | string | no | Display election name. | character |
| `election_date` | string/date | yes | Election date, if known. | Date |

Example:

```json
{
  "id": 1,
  "election_key": "congreso_espana_2027",
  "election_type": "general",
  "territory_code": "ES",
  "election_name": "Congreso de los Diputados 2027",
  "election_date": null
}
```

## Pollster

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `id` | integer | no | Database pollster id. Prefer `pollster_key` for filters. | integer |
| `pollster_key` | string | no | Stable pollster key. | character |
| `pollster_name` | string | no | Display name. | character |
| `poll_count` | integer | no | Number of matching polls used for this catalogue row. | integer |

Example:

```json
{
  "id": 10,
  "pollster_key": "40db",
  "pollster_name": "40dB",
  "poll_count": 18
}
```

## Party

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `party_key` | string | no | Stable party key. | character |
| `party_name` | string | no | Canonical party name. | character |
| `short_name` | string | no | Compact display label. | character |
| `territory_code` | string | no | Primary territory for the party. | character |
| `color_hex` | string | yes | Suggested visualization color. | character |
| `display_order` | integer | yes | Suggested ordering for legends/tables. | integer |
| `is_active` | boolean | no | Whether the party is active in the catalog. | logical |
| `poll_count` | integer | no | Number of distinct polls with this party key. | integer |

Example:

```json
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
```

## Poll summary

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `id` | integer | no | Poll id. | integer |
| `election_key` | string | no | Stable election key. | character |
| `election_name` | string | yes | Election display name. | character |
| `territory_code` | string | yes | Territory code. | character |
| `pollster_key` | string | no | Stable pollster key. | character |
| `pollster_name` | string | no | Pollster display name. | character |
| `media` | string | yes | Media outlet/source label. | character |
| `fieldwork_start` | string/date | yes | Fieldwork start date. | Date |
| `fieldwork_end` | string/date | yes | Fieldwork end date. | Date |
| `publication_date` | string/date | yes | Publication date. | Date |
| `sample_size` | integer | yes | Sample size. | integer |
| `turnout` | number | yes | Turnout percentage/estimate. | numeric |
| `lead` | number | yes | Lead value in percentage points. | numeric |
| `source_url` | string | yes | Public source URL. | character |
| `source_title` | string | yes | Public source title. | character |
| `identity_status` | string | no | Identity/matching status. | character |
| `first_seen_at` | string/datetime | yes | First time this poll was seen by the pipeline. | POSIXct or character |
| `is_active` | boolean | no | Whether poll is active. | logical |

Example:

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
  "is_active": true
}
```

## Poll detail

Same fields as `Poll summary`, plus:

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `results` | array of Poll result | no | Nested party results for this poll. May be empty. | tibble/list column |

Example:

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

## Poll result

Standalone poll result fields:

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `party_key` | string | no | Stable party key. | character |
| `party_raw` | string | yes | Raw/display party label. | character |
| `party_name` | string | yes | Canonical party name, falling back to `party_raw` for uncatalogued parties. | character |
| `short_name` | string | yes | Compact party label, falling back to `party_raw` for uncatalogued parties. | character |
| `color_hex` | string | yes | Suggested visualization color. | character |
| `display_order` | integer | yes | Suggested visualization order. | integer |
| `vote_share` | number | yes | Vote share percentage. | numeric |
| `seats_min` | integer | yes | Minimum seat estimate, if present. | integer |
| `seats_max` | integer | yes | Maximum seat estimate, if present. | integer |

Long-format `/api/v1/results` adds:

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `poll_id` | integer | no | Poll id. | integer |
| `date` | string/date | yes | `coalesce(fieldwork_end, publication_date)`. | Date |
| `election_key` | string | no | Stable election key. | character |
| `pollster_key` | string | no | Stable pollster key. | character |
| `pollster_name` | string | no | Pollster display name. | character |
| `media` | string | yes | Media label. | character |
| `fieldwork_end` | string/date | yes | Fieldwork end date. | Date |
| `publication_date` | string/date | yes | Publication date. | Date |
| `sample_size` | integer | yes | Sample size. | integer |

Example:

```json
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
```

## Timeseries item

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `date` | string/date | no | Selected date according to `date_field`. | Date |
| `poll_id` | integer | no | Poll id. | integer |
| `pollster_key` | string | no | Stable pollster key. | character |
| `pollster_name` | string | yes | Pollster display name. | character |
| `media` | string | yes | Media label. | character |
| `sample_size` | integer | yes | Sample size. | integer |
| `party_key` | string | no | Stable party key. | character |
| `party_raw` | string | yes | Raw/display party label. | character |
| `party_name` | string | yes | Canonical party name, falling back to `party_raw` for uncatalogued parties. | character |
| `short_name` | string | yes | Compact party label, falling back to `party_raw` for uncatalogued parties. | character |
| `color_hex` | string | yes | Suggested visualization color. | character |
| `display_order` | integer | yes | Suggested visualization order. | integer |
| `vote_share` | number | yes | Vote share percentage. | numeric |

Example:

```json
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
```

## Error response

FastAPI errors generally use a `detail` field.

| Field | Type | Nullable | Description | R target type |
|---|---|---|---|---|
| `detail` | string, array, or object | no | Error detail. Shape depends on error source. | list/character |

404 example:

```json
{
  "detail": "Poll not found"
}
```

422 example:

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["query", "limit"],
      "msg": "Input should be less than or equal to 1000",
      "input": "1001",
      "ctx": {"le": 1000}
    }
  ]
}
```

## Type Conversion Summary

Convert to `Date`:

- `election_date`
- `fieldwork_start`
- `fieldwork_end`
- `publication_date`
- `date`

Convert to `numeric`:

- `turnout`
- `lead`
- `vote_share`

Convert to `logical`:

- `is_active`
- Boolean input parameters such as `include_inactive`, `include_manual_review`, `active_only`

Nullable fields include:

- `election_date`
- `election_name`
- `territory_code`
- `media`
- `fieldwork_start`
- `fieldwork_end`
- `publication_date`
- `sample_size`
- `turnout`
- `lead`
- `source_url`
- `source_title`
- `first_seen_at`
- `party_raw`
- `party_name`
- `short_name`
- `color_hex`
- `display_order`
- `vote_share`
- `seats_min`
- `seats_max`

## Internal Fields

The current public API does not expose these internal fields, and the R package should ignore them if they appear in future responses:

- `row_hash`
- `poll_signature`
- `poll_key_strict`
- `raw_html`
- `raw_wikitext`
- `payload_json`
- `wiki_revision_id`
- `identity_confidence`
- `source_reference_ids`
- `source_metadata`
- `raw_value`
