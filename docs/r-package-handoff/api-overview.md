# API Overview

## Summary

Name: Spain Electoral Polls API

Objective: expose read-only polling data from the Spain Electoral Polls database as JSON for dashboards, external programmatic use, and the future R package `spainpolls`.

Base URL: `https://pollsdb.spainelectoralproject.com`

Local base URL: `http://localhost:8000`

API prefix: `/api/v1`

Format: JSON

Authentication: none for public endpoints

Current API version: `0.1.0`

Current status: public read-only API implemented with FastAPI. Admin endpoints are postponed.

## Intended Use

- Dashboard: fetch lists of elections, pollsters, parties, polls, results and timeseries.
- External programmatic queries: stable JSON over HTTP using `GET` only.
- R package: wrap public endpoints in `get_*()` functions, parse JSON, and return typed `tibble`s.

## Public Surface

Implemented routes:

- `GET /health`
- `GET /api/v1/elections`
- `GET /api/v1/pollsters`
- `GET /api/v1/parties`
- `GET /api/v1/polls`
- `GET /api/v1/polls/{poll_id}`
- `GET /api/v1/results`
- `GET /api/v1/timeseries`

Not implemented:

- `GET /api/v1/polls/{poll_id}/results`
- Admin/scraper/audit endpoints

## Limits

- Paginated endpoints default to `limit=100`.
- Maximum `limit` is `1000`.
- `offset` defaults to `0`.
- If `limit > 1000`, FastAPI returns `422 Validation Error`.
- All implemented routes are `GET`.
- CORS allows `GET` methods.

## Default Public Filters

For poll-based data, the API excludes by default:

- inactive polls: `is_active = false`
- polls in manual review: `identity_status = "manual_review"`

The client may opt in:

- `include_inactive=true`
- `include_manual_review=true`

For `/api/v1/polls`, `identity_status` can also be supplied. If it is supplied, it filters to that exact status and overrides the default manual-review exclusion.

For default public reads, the API uses database views:

- `/api/v1/polls` reads from `api_polls_public`.
- `/api/v1/results` and `/api/v1/timeseries` read from `api_poll_results_public`.

Those views already apply the public filters. Requests that explicitly include inactive or manual-review polls use base tables instead.

## Naming Conventions

- JSON fields use `snake_case`.
- Dates are serialized as strings in `YYYY-MM-DD`.
- Datetimes are ISO-8601 strings, for example `2026-06-07T12:34:56`.
- Percent-like values such as `vote_share`, `turnout` and `lead` are JSON numbers.
- Keys ending in `_key` are stable identifiers intended for client filters, for example `election_key`, `pollster_key`, `party_key`.
- Display names ending in `_name`, `_raw`, or `short_name` are useful for labels but should not be used as primary keys.

## Stable Fields for External Clients

Stable enough for the R package initial public interface:

- IDs and keys: `id`, `poll_id`, `election_key`, `pollster_key`, `party_key`, `territory_code`
- Display fields: `election_name`, `pollster_name`, `party_raw`, `party_name`, `short_name`, `media`
- Visualization fields: `color_hex`, `display_order`
- Dates: `election_date`, `fieldwork_start`, `fieldwork_end`, `publication_date`, `date`
- Measures: `sample_size`, `turnout`, `lead`, `vote_share`, `seats_min`, `seats_max`, `poll_count`
- Public state fields: `identity_status`, `is_active`, `first_seen_at`

Fields not exposed or not stable for R package users:

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

If any of these appear in a future public response, the R package should ignore them by default and not document them as stable user-facing columns.
