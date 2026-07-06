# OpenAPI Notes

The API is implemented with FastAPI, so OpenAPI documentation is generated automatically.

## Local URLs

With the local server running on port 8000:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Production URLs

If production is deployed at the configured public domain:

- Swagger UI: `https://polls.spainelectoralproject.com/docs`
- ReDoc: `https://polls.spainelectoralproject.com/redoc`
- OpenAPI JSON: `https://polls.spainelectoralproject.com/openapi.json`

## Download OpenAPI JSON

From a running local server:

```bash
curl http://localhost:8000/openapi.json -o docs/r-package-handoff/openapi.json
```

From production:

```bash
curl https://polls.spainelectoralproject.com/openapi.json -o docs/r-package-handoff/openapi.json
```

A copy has also been generated in this folder as `openapi.json` by importing the FastAPI app and calling `app.openapi()`.

## Completeness

The OpenAPI contract is useful and mostly complete for:

- endpoint paths
- query parameter names
- path parameter names
- primitive types
- `limit` and `offset` validation bounds
- response models
- enum validation for `date_field`
- 422 validation error shape

## Known Limitations

- OpenAPI does not fully describe business defaults such as "manual review is excluded unless `include_manual_review=true`".
- OpenAPI does not explain that `party` is an alias for `party_key` and does not match `party_raw`, `party_name`, or `short_name`.
- OpenAPI does not describe sorting order.
- OpenAPI does not explain that public defaults use `api_polls_public` and `api_poll_results_public`.
- OpenAPI does not mark client-facing stability of fields.
- OpenAPI may not show every possible infrastructure error such as 503 or timeout.
- `identity_status` is typed as string, not an enum, even though known database values are `exact`, `probable_match`, `manual_review`, and `new_poll`.
- `GET /api/v1/polls/{poll_id}/results` is absent because it is not implemented.

## Warnings for R Package Agent

- Use OpenAPI to confirm route names and parameter types, but use these handoff docs for behavior and R typing.
- Do not generate wrappers for paths absent from OpenAPI.
- Do not assume fields outside schemas are stable.
- Do not expose internal fields even if a future OpenAPI version includes them accidentally.
- Treat `limit=1000` as the maximum page size.
- Parse FastAPI 422 errors into friendly R messages.
