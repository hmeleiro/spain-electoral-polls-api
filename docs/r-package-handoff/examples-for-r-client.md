# Examples for R Client

Production base URL: `https://pollsdb.spainelectoralproject.com`

Local base URL: `http://localhost:8000`

The R calls below are suggested public wrappers for the future `spainpolls` package. They are not implemented in this repository.

## Example: healthcheck

### HTTP request

```bash
curl "http://localhost:8000/health"
```

Production:

```bash
curl "https://pollsdb.spainelectoralproject.com/health"
```

### Expected JSON response

```json
{
  "status": "ok",
  "service": "spain-electoral-polls-api",
  "database": "ok"
}
```

### Suggested R call

```r
check_api_health()
```

## Example: list elections

### HTTP request

```bash
curl "http://localhost:8000/api/v1/elections?limit=10"
```

### Expected JSON response

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

### Suggested R call

```r
get_elections(limit = 10)
```

## Example: list pollsters

### HTTP request

```bash
curl "http://localhost:8000/api/v1/pollsters?election_key=congreso_espana_2027"
```

### Expected JSON response

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

### Suggested R call

```r
get_pollsters(election_key = "congreso_espana_2027")
```

## Example: list parties

### HTTP request

```bash
curl "http://localhost:8000/api/v1/parties?election_key=congreso_espana_2027"
```

### Expected JSON response

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

### Suggested R call

```r
get_parties(election_key = "congreso_espana_2027")
```

## Example: get recent polls

### HTTP request

```bash
curl "http://localhost:8000/api/v1/polls?limit=10"
```

Production:

```bash
curl "https://pollsdb.spainelectoralproject.com/api/v1/polls?limit=10"
```

### Expected JSON response

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
  "limit": 10,
  "offset": 0,
  "total": 1
}
```

### Suggested R call

```r
get_polls(limit = 10)
```

## Example: get one poll by ID

### HTTP request

```bash
curl "http://localhost:8000/api/v1/polls/101"
```

### Expected JSON response

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

### Suggested R call

```r
get_poll(101)
```

## Example: get results in long format

### HTTP request

```bash
curl "http://localhost:8000/api/v1/results?limit=10"
```

### Expected JSON response

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
  "limit": 10,
  "offset": 0,
  "total": 1
}
```

### Suggested R call

```r
get_results(limit = 10)
```

## Example: get timeseries for a party

### HTTP request

```bash
curl "http://localhost:8000/api/v1/timeseries?party=psoe&date_field=auto&limit=10"
```

### Expected JSON response

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
  "limit": 10,
  "offset": 0,
  "total": 1
}
```

### Suggested R call

```r
get_timeseries(party = "psoe", date_field = "auto", limit = 10)
```

## Example: filter by pollster

### HTTP request

```bash
curl "http://localhost:8000/api/v1/polls?pollster=40db&limit=10"
```

### Expected JSON response

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
  "limit": 10,
  "offset": 0,
  "total": 1
}
```

### Suggested R call

```r
get_polls(pollster = "40db", limit = 10)
```

Prefer this when users type names. For programmatic code, prefer `pollster_key = "40db"`.

## Example: use pagination

### HTTP request

```bash
curl "http://localhost:8000/api/v1/results?limit=1000&offset=0"
curl "http://localhost:8000/api/v1/results?limit=1000&offset=1000"
```

### Expected JSON response

```json
{
  "items": [],
  "limit": 1000,
  "offset": 1000,
  "total": 1000
}
```

### Suggested R call

```r
get_results(limit = 1000, collect_all = TRUE)
```

## Example: include manual review

### HTTP request

```bash
curl "http://localhost:8000/api/v1/polls?include_manual_review=true&limit=10"
```

### Expected JSON response

```json
{
  "items": [
    {
      "id": 102,
      "election_key": "congreso_espana_2027",
      "election_name": "Congreso de los Diputados 2027",
      "territory_code": "ES",
      "pollster_key": "40db",
      "pollster_name": "40dB",
      "media": "El Pais",
      "fieldwork_start": "2026-06-08",
      "fieldwork_end": "2026-06-10",
      "publication_date": "2026-06-11",
      "sample_size": 900,
      "turnout": null,
      "lead": 1.1,
      "source_url": "https://example.com/manual",
      "source_title": "Manual poll",
      "identity_status": "manual_review",
      "first_seen_at": "2026-06-11T09:00:00",
      "is_active": true
    }
  ],
  "limit": 10,
  "offset": 0,
  "total": 2
}
```

### Suggested R call

```r
get_polls(include_manual_review = TRUE, limit = 10)
```

The R package should make this opt-in and label it clearly in documentation.

## Example: include inactive polls

### HTTP request

```bash
curl "http://localhost:8000/api/v1/polls?include_inactive=true&limit=10"
```

### Expected JSON response

```json
{
  "items": [
    {
      "id": 103,
      "election_key": "congreso_espana_2027",
      "election_name": "Congreso de los Diputados 2027",
      "territory_code": "ES",
      "pollster_key": "40db",
      "pollster_name": "40dB",
      "media": "La Sexta",
      "fieldwork_start": "2026-06-10",
      "fieldwork_end": "2026-06-12",
      "publication_date": "2026-06-13",
      "sample_size": 1000,
      "turnout": null,
      "lead": 2.5,
      "source_url": "https://example.com/inactive",
      "source_title": "Inactive poll",
      "identity_status": "exact",
      "first_seen_at": "2026-06-13T09:00:00",
      "is_active": false
    }
  ],
  "limit": 10,
  "offset": 0,
  "total": 2
}
```

### Suggested R call

```r
get_polls(include_inactive = TRUE, limit = 10)
```
