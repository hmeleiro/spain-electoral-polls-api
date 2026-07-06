# Pagination

Most list endpoints are paginated.

## Paginated Endpoints

- `GET /api/v1/elections`
- `GET /api/v1/pollsters`
- `GET /api/v1/parties`
- `GET /api/v1/polls`
- `GET /api/v1/results`
- `GET /api/v1/timeseries`

Not paginated:

- `GET /health`
- `GET /api/v1/polls/{poll_id}`

## Response Structure

```json
{
  "items": [],
  "limit": 100,
  "offset": 0,
  "total": 0
}
```

- `items`: rows in the current page.
- `limit`: requested page size.
- `offset`: zero-based starting row offset.
- `total`: total number of rows matching the filters before pagination.

## Limits

Default `limit`: `100`

Maximum `limit`: `1000`

Default `offset`: `0`

If `limit > 1000`, the API returns `422 Validation Error`. It does not clamp the value.

## How To Know Whether More Pages Exist

There are more pages when:

```text
offset + length(items) < total
```

The simpler check from the API contract is:

```text
offset + limit < total
```

For robust clients, prefer `offset + length(items) < total` because a page may return fewer rows than requested.

## Recommended collect_all Strategy

For `collect_all = TRUE`, request pages with `limit = 1000` unless the user supplied a smaller limit intentionally.

Pseudocode:

```text
offset = 0
limit = 1000
all_items = []

repeat:
  request page with limit and offset
  append page.items to all_items

  if page.total == 0: break
  if length(page.items) == 0: break
  if offset + length(page.items) >= page.total: break

  offset = offset + limit
```

## Edge Cases

### `total = 0`

Return an empty tibble with the expected columns and types. Do not error.

### `items` is empty

If `total = 0`, this is normal. If `total > 0` and `items` is empty, the offset is likely past the end. Return an empty tibble for that page. In `collect_all`, stop to avoid an infinite loop.

### API returns fewer rows than `limit`

This can happen on the last page. Append the rows and stop if `offset + length(items) >= total`.

### Error in an intermediate page

Stop and raise an R error that includes:

- endpoint
- query filters
- `limit`
- `offset`
- HTTP status
- parsed API error detail, if available

Suggested R message:

```r
cli::cli_abort(
  "Failed while collecting {.path {endpoint}} at offset {.val {offset}}: HTTP {status}."
)
```

Do not silently return partial data unless the package explicitly offers an advanced recovery mode.

## Suggested R Function Contract

For paginated wrappers:

```r
get_polls <- function(..., limit = 100, offset = 0, collect_all = FALSE) {
  # validate limit <= 1000
  # if collect_all, page until all items are collected
  # return tibble
}
```

For `collect_all = TRUE`, either ignore user `offset` and start from zero, or document that collection starts from the supplied offset. The simplest public behavior is to start at `offset = 0`.

