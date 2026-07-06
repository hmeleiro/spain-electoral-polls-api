# Error Handling

The API uses FastAPI defaults plus one explicit 404 for missing or hidden poll detail. Most JSON errors contain a top-level `detail` field.

The R package should always call `httr2::resp_check_status()` or equivalent, then parse JSON error bodies when possible to produce friendly `cli::cli_abort()` messages.

## 400 Bad Request

### When it happens

No implemented route explicitly raises 400 today. It may be returned by infrastructure, future API validation, malformed requests at a proxy, or non-FastAPI layers.

### Example response

```json
{
  "detail": "Bad request"
}
```

### Recommended R error message

```r
cli::cli_abort("The API rejected the request as malformed: {detail}")
```

## 404 Not Found

### When it happens

- `GET /api/v1/polls/{poll_id}` cannot find the poll.
- The poll exists but is hidden by default because it is inactive or in manual review.
- Endpoint path does not exist, for example `/api/v1/polls/101/results`.

### Example response

```json
{
  "detail": "Poll not found"
}
```

For an unknown endpoint, FastAPI usually returns:

```json
{
  "detail": "Not Found"
}
```

### Recommended R error message

For poll detail:

```r
cli::cli_abort("Poll with id {.val {poll_id}} was not found.")
```

If the call did not include `include_inactive` or `include_manual_review`, optionally add:

```r
cli::cli_abort(
  "Poll with id {.val {poll_id}} was not found. It may be inactive or in manual review."
)
```

## 422 Validation Error

### When it happens

FastAPI could not validate query or path parameters. Common examples:

- `limit=1001`
- `limit=0`
- `offset=-1`
- invalid date format, for example `fieldwork_end_from=2026/06/05`
- invalid `date_field`, for example `date_field=end`
- non-integer `poll_id`

### Example response

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

### Recommended R error message

```r
cli::cli_abort("Invalid API parameter {.arg {param}}: {message}")
```

The client should validate `limit`, `offset`, `date_field`, and date inputs before sending the request when practical.

## 500 Internal Server Error

### When it happens

Unhandled server errors, database query errors, serialization problems, or unexpected implementation issues.

### Example response

FastAPI may return a plain text or JSON body depending on configuration:

```json
{
  "detail": "Internal Server Error"
}
```

### Recommended R error message

```r
cli::cli_abort(
  "The Spain Electoral Polls API returned an internal error. Try again later."
)
```

Include endpoint and status in the condition metadata for debugging.

## 503 Service Unavailable

### When it happens

No implemented route explicitly raises 503 today. It may be returned by a reverse proxy, hosting platform, load balancer, deployment restart, or database-dependent infrastructure.

Note: `/health` currently returns HTTP 200 even when the database check fails, with `"database": "unavailable"`.

### Example response

```json
{
  "detail": "Service unavailable"
}
```

### Recommended R error message

```r
cli::cli_abort("The Spain Electoral Polls API is temporarily unavailable.")
```

## Timeout

### When it happens

The API or network does not respond within the client timeout.

### Recommended R behavior

Use an explicit timeout, for example 30 seconds:

```r
request(base_url) |>
  req_timeout(30)
```

Recommended message:

```r
cli::cli_abort("Request to Spain Electoral Polls API timed out after {timeout} seconds.")
```

## API Not Available

### When it happens

DNS failure, refused connection, TLS failure, local server not running, or production outage.

### Recommended R behavior

Catch `httr2` request errors and rethrow with the base URL:

```r
cli::cli_abort("Could not connect to Spain Electoral Polls API at {.url {base_url}}.")
```

## Unexpected JSON

### When it happens

- Response body is not JSON.
- Paginated endpoint lacks `items`, `limit`, `offset`, or `total`.
- Field type differs from expected schema.
- HTML error page returned by proxy.

### Recommended R behavior

Treat as an API contract error:

```r
cli::cli_abort("Unexpected response format from Spain Electoral Polls API.")
```

Include a truncated body preview in debug metadata, not in the default user message.

## Invalid Parameters

The R client should catch obvious invalid parameters before HTTP:

- `limit` must be between 1 and 1000.
- `offset` must be `>= 0`.
- `date_field` must be one of `auto`, `fieldwork_end`, `publication_date`.
- Date inputs must be coercible to `Date`.
- Boolean inputs must be scalar logical values.

