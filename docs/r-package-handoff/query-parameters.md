# Query Parameters

Dates use `YYYY-MM-DD`. In R, accept `Date` or character values coercible to `Date`, then send character strings in ISO date format.

Booleans should be sent as `true` or `false`.

| Parameter | Type | Used by endpoints | Default | Allowed values | Description | R type |
|---|---:|---|---|---|---|---|
| `territory_code` | string | `/api/v1/elections`, `/api/v1/pollsters`, `/api/v1/parties`, `/api/v1/polls`, `/api/v1/results`, `/api/v1/timeseries` | none | Known territory codes, for example `ES` | Exact territory filter from elections. | character |
| `election_type` | string | `/api/v1/elections` | none | Values in database, for example `general` | Exact election type filter. | character |
| `election_key` | string | `/api/v1/pollsters`, `/api/v1/parties`, `/api/v1/polls`, `/api/v1/results`, `/api/v1/timeseries` | none | Known election keys, for example `congreso_espana_2027` | Stable election identifier. | character |
| `pollster_key` | string | `/api/v1/polls`, `/api/v1/results`, `/api/v1/timeseries` | none | Known pollster keys, for example `40db` | Exact pollster key filter, case-insensitive. | character |
| `pollster` | string | `/api/v1/polls`, `/api/v1/results`, `/api/v1/timeseries` | none | Pollster key or exact pollster name | Case-insensitive exact match against `pollster_key` or `pollster_name`. | character |
| `media` | string | `/api/v1/polls`, `/api/v1/results`, `/api/v1/timeseries` | none | Any substring | Case-insensitive substring match against `polls.media`. | character |
| `party_key` | string | `/api/v1/results`, `/api/v1/timeseries` | none | Known party keys, for example `psoe` | Exact party key filter, case-insensitive. | character |
| `party` | string | `/api/v1/results`, `/api/v1/timeseries` | none | Known party keys, for example `psoe` | Alias for `party_key`; matches only canonical party keys, not `party_raw`, `party_name`, or `short_name`. | character |
| `fieldwork_start_from` | date string | `/api/v1/polls` | none | `YYYY-MM-DD` | Include polls with `fieldwork_start >= value`. | Date or character |
| `fieldwork_start_to` | date string | `/api/v1/polls` | none | `YYYY-MM-DD` | Include polls with `fieldwork_start <= value`. | Date or character |
| `fieldwork_end_from` | date string | `/api/v1/polls`, `/api/v1/results` | none | `YYYY-MM-DD` | Include polls with `fieldwork_end >= value`. | Date or character |
| `fieldwork_end_to` | date string | `/api/v1/polls`, `/api/v1/results` | none | `YYYY-MM-DD` | Include polls with `fieldwork_end <= value`. | Date or character |
| `publication_date_from` | date string | `/api/v1/polls`, `/api/v1/results` | none | `YYYY-MM-DD` | Include polls with `publication_date >= value`. | Date or character |
| `publication_date_to` | date string | `/api/v1/polls`, `/api/v1/results` | none | `YYYY-MM-DD` | Include polls with `publication_date <= value`. | Date or character |
| `date_from` | date string | `/api/v1/timeseries` | none | `YYYY-MM-DD` | Include timeseries points with selected `date >= value`. | Date or character |
| `date_to` | date string | `/api/v1/timeseries` | none | `YYYY-MM-DD` | Include timeseries points with selected `date <= value`. | Date or character |
| `date_field` | string enum | `/api/v1/timeseries` | `auto` | `auto`, `fieldwork_end`, `publication_date` | Chooses the date used by timeseries. `auto` uses `coalesce(fieldwork_end, publication_date)`. | character |
| `identity_status` | string | `/api/v1/polls` | none | `exact`, `probable_match`, `manual_review`, `new_poll` | Exact identity status filter. If supplied, it overrides the default exclusion of `manual_review`. Not validated as an enum by FastAPI. | character |
| `include_manual_review` | boolean | `/api/v1/polls`, `/api/v1/polls/{poll_id}`, `/api/v1/results`, `/api/v1/timeseries` | `false` | `true`, `false` | Include polls with `identity_status = "manual_review"`. | logical |
| `include_inactive` | boolean | `/api/v1/polls`, `/api/v1/polls/{poll_id}`, `/api/v1/results`, `/api/v1/timeseries` | `false` | `true`, `false` | Include polls where `is_active = false`. | logical |
| `active_only` | boolean | `/api/v1/pollsters`, `/api/v1/parties` | `true` | `true`, `false` | For pollsters, counts only active non-manual-review polls. For parties, filters `parties.is_active`. | logical |
| `limit` | integer | All paginated endpoints | `100` | `1` to `1000` | Number of rows returned in this page. If above 1000, the API returns 422. | integer |
| `offset` | integer | All paginated endpoints | `0` | `>= 0` | Zero-based row offset for pagination. | integer |

## Limit Behavior

Default: `100`

Maximum: `1000`

If the client sends `limit=1001`, FastAPI returns HTTP `422` with a validation error. The API does not silently clamp the value.

## Parameter Notes for R

- Prefer keys (`election_key`, `pollster_key`, `party_key`) over names.
- Use `/api/v1/parties` to obtain `short_name`, `color_hex`, and `display_order` for plotting defaults.
- Convert `Date` inputs with `format(x, "%Y-%m-%d")`.
- Omit parameters with `NULL`; do not send `param=NULL`.
- Send booleans as JSON/query booleans through `httr2::req_url_query(include_inactive = TRUE)`; `httr2` serializes these appropriately.
- Consider validating `date_field` client-side before request.
- Consider validating `limit <= 1000` client-side for clearer R errors.
