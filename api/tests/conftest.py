import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/spainelectoralpollsdb_test",
)

from app.core.cache import clear_response_cache  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_response_cache():
    clear_response_cache()
    yield
    clear_response_cache()


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    try:
        with engine.connect():
            pass
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL test database is not available: {exc}")
    yield engine
    engine.dispose()


def _run_sql_file(engine, path: Path) -> None:
    raw_connection = engine.raw_connection()
    try:
        cursor = raw_connection.cursor()
        cursor.execute(path.read_text(encoding="utf-8"))
        raw_connection.commit()
    finally:
        raw_connection.close()


@pytest.fixture(autouse=True)
def reset_database(request):
    if request.node.get_closest_marker("no_db"):
        return

    test_engine = request.getfixturevalue("test_engine")
    root = Path(__file__).resolve().parents[2]
    sql_dir = root / "sql"

    with test_engine.begin() as conn:
        conn.execute(
            text(
                """
                drop table if exists poll_results cascade;
                drop table if exists poll_review_actions cascade;
                drop table if exists poll_match_candidates cascade;
                drop table if exists polls cascade;
                drop table if exists parties cascade;
                drop table if exists pollsters cascade;
                drop table if exists scraper_runs cascade;
                drop table if exists poll_identity_events cascade;
                drop table if exists poll_versions cascade;
                drop table if exists wiki_page_revisions cascade;
                drop table if exists wiki_pages cascade;
                drop table if exists elections cascade;
                """
            )
        )

    _run_sql_file(test_engine, sql_dir / "001_schema.sql")
    _run_sql_file(test_engine, sql_dir / "002_indexes.sql")
    _run_sql_file(test_engine, sql_dir / "004_manual_review_workflow.sql")

    with test_engine.begin() as conn:
        pollster_id = conn.execute(
            text(
                """
                insert into pollsters (pollster_name, pollster_key)
                values ('40dB', '40db')
                returning id
                """
            )
        ).scalar_one()
        election_id = conn.execute(
            text("select id from elections where election_key = 'congreso_espana_2027'")
        ).scalar_one()

        active_poll_id = conn.execute(
            text(
                """
                insert into polls (
                    poll_key_strict, poll_signature, election_id, pollster_id, media,
                    fieldwork_start, fieldwork_end, publication_date, sample_size,
                    turnout, lead, wiki_page, wiki_revision_id, source_url, source_title,
                    row_hash, identity_status, identity_confidence, is_active
                )
                values (
                    'poll_active', 'sig_active', :election_id, :pollster_id, 'El Pais',
                    '2026-06-01', '2026-06-05', '2026-06-07', 1200,
                    null, 3.2, 'next_spanish_general_election', 123456,
                    'https://example.com/active', 'Active poll',
                    'hash_active', 'exact', 1.0, true
                )
                returning id
                """
            ),
            {"election_id": election_id, "pollster_id": pollster_id},
        ).scalar_one()

        manual_poll_id = conn.execute(
            text(
                """
                insert into polls (
                    poll_key_strict, poll_signature, election_id, pollster_id, media,
                    fieldwork_start, fieldwork_end, publication_date, sample_size,
                    turnout, lead, wiki_page, wiki_revision_id, source_url, source_title,
                    row_hash, identity_status, identity_confidence, is_active
                )
                values (
                    'poll_manual', 'sig_manual', :election_id, :pollster_id, 'El Pais',
                    '2026-06-08', '2026-06-10', '2026-06-11', 900,
                    null, 1.1, 'next_spanish_general_election', 123457,
                    'https://example.com/manual', 'Manual poll',
                    'hash_manual', 'manual_review', 0.5, true
                )
                returning id
                """
            ),
            {"election_id": election_id, "pollster_id": pollster_id},
        ).scalar_one()

        inactive_poll_id = conn.execute(
            text(
                """
                insert into polls (
                    poll_key_strict, poll_signature, election_id, pollster_id, media,
                    fieldwork_start, fieldwork_end, publication_date, sample_size,
                    turnout, lead, wiki_page, wiki_revision_id, source_url, source_title,
                    row_hash, identity_status, identity_confidence, is_active
                )
                values (
                    'poll_inactive', 'sig_inactive', :election_id, :pollster_id, 'La Sexta',
                    '2026-06-10', '2026-06-12', '2026-06-13', 1000,
                    null, 2.5, 'next_spanish_general_election', 123458,
                    'https://example.com/inactive', 'Inactive poll',
                    'hash_inactive', 'exact', 1.0, false
                )
                returning id
                """
            ),
            {"election_id": election_id, "pollster_id": pollster_id},
        ).scalar_one()

        for poll_id, psoe_share, pp_share in [
            (active_poll_id, 31.2, 28.0),
            (manual_poll_id, 30.1, 29.0),
            (inactive_poll_id, 29.5, 31.0),
        ]:
            conn.execute(
                text(
                    """
                    insert into poll_results (
                        poll_id, party_key, party_raw, vote_share, seats_min, seats_max, raw_value
                    )
                    values
                      (:poll_id, 'psoe', 'PSOE', :psoe_share, null, null, :psoe_raw),
                      (:poll_id, 'pp', 'PP', :pp_share, null, null, :pp_raw)
                    """
                ),
                {
                    "poll_id": poll_id,
                    "psoe_share": psoe_share,
                    "pp_share": pp_share,
                    "psoe_raw": str(psoe_share),
                    "pp_raw": str(pp_share),
                },
            )

        conn.execute(
            text(
                """
                insert into poll_results (poll_id, party_key, party_raw, vote_share, seats_min, seats_max, raw_value)
                values (:poll_id, 'new_party', 'New Party', 2.4, null, null, '2.4')
                """
            ),
            {"poll_id": active_poll_id},
        )

        conn.execute(
            text(
                """
                insert into poll_match_candidates (
                    poll_id,
                    candidate_poll_id,
                    wiki_revision_id,
                    rank,
                    confidence,
                    reasons,
                    candidate_snapshot
                )
                values (
                    :poll_id,
                    :candidate_poll_id,
                    123457,
                    1,
                    0.82,
                    jsonb_build_array('same_election', 'same_pollster', 'same_media', 'similar_vote_results'),
                    jsonb_build_object(
                        'candidate_poll_id', :candidate_poll_id,
                        'pollster_key', '40db',
                        'pollster_name', '40dB',
                        'media', 'El Pais',
                        'fieldwork_start', '2026-06-01',
                        'fieldwork_end', '2026-06-05',
                        'publication_date', '2026-06-07',
                        'sample_size', 1200,
                        'source_url', 'https://example.com/active',
                        'source_title', 'Active poll',
                        'identity_status', 'exact',
                        'vote_share_sum', 59.2,
                        'results', jsonb_build_array(
                            jsonb_build_object(
                                'party_key', 'psoe',
                                'party_raw', 'PSOE',
                                'short_name', 'PSOE',
                                'vote_share', 31.2,
                                'raw_value', '31.2'
                            ),
                            jsonb_build_object(
                                'party_key', 'pp',
                                'party_raw', 'PP',
                                'short_name', 'PP',
                                'vote_share', 28.0,
                                'raw_value', '28.0'
                            )
                        )
                    )
                )
                """
            ),
            {"poll_id": manual_poll_id, "candidate_poll_id": active_poll_id},
        )


@pytest.fixture
def fastapi_app():
    return app
