from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import Field, field_serializer

from app.schemas.common import DecimalJSONModel

ReviewStatus = Literal["pending", "needs_fix", "reviewed", "rejected"]
ReviewAction = Literal["approved_new_poll", "approved_match", "rejected", "needs_fix", "comment"]


class ReviewAnomaly(DecimalJSONModel):
    severity: Literal["error", "warning", "info"]
    code: str
    message: str


class ReviewQueueItem(DecimalJSONModel):
    poll_id: int
    election_key: str
    territory_code: str
    pollster_key: str | None = None
    pollster_name: str
    media: str | None = None
    fieldwork_start: date | None = None
    fieldwork_end: date | None = None
    publication_date: date | None = None
    sample_size: int | None = None
    source_url: str | None = None
    source_title: str | None = None
    wiki_page: str | None = None
    identity_status: str
    identity_confidence: Decimal | None = None
    is_active: bool
    result_count: int
    vote_share_sum: Decimal | None = None
    anomaly_count: int
    error_count: int
    warning_count: int
    anomalies: list[ReviewAnomaly]
    latest_identity_event_type: str | None = None
    latest_identity_event_reasons: list[str] | None = None
    latest_review_action: ReviewAction | None = None
    latest_reviewer: str | None = None
    latest_review_at: datetime | None = None
    review_status: ReviewStatus
    review_priority: int

    @field_serializer("identity_confidence", "vote_share_sum")
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        return self._decimal_to_float(value)

    @field_serializer("latest_review_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return None if value is None else value.isoformat()


class ReviewResult(DecimalJSONModel):
    poll_id: int | None = None
    party_key: str
    party_raw: str | None = None
    party_name: str | None = None
    short_name: str
    color_hex: str | None = None
    display_order: int | None = None
    is_unknown_party: bool
    vote_share: Decimal | None = None
    seats_min: int | None = None
    seats_max: int | None = None
    raw_value: str | None = None
    recent_average_vote_share: Decimal | None = None
    delta_from_recent_average: Decimal | None = None

    @field_serializer("vote_share", "recent_average_vote_share", "delta_from_recent_average")
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        return self._decimal_to_float(value)


class ReviewMatchCandidateResult(DecimalJSONModel):
    party_key: str
    party_raw: str | None = None
    short_name: str | None = None
    vote_share: Decimal | None = None
    seats_min: int | None = None
    seats_max: int | None = None
    raw_value: str | None = None

    @field_serializer("vote_share")
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        return self._decimal_to_float(value)


class ReviewMatchCandidate(DecimalJSONModel):
    candidate_poll_id: int
    rank: int
    confidence: Decimal | None = None
    reasons: list[str]
    pollster_key: str | None = None
    pollster_name: str | None = None
    media: str | None = None
    fieldwork_start: date | None = None
    fieldwork_end: date | None = None
    publication_date: date | None = None
    sample_size: int | None = None
    source_url: str | None = None
    source_title: str | None = None
    identity_status: str | None = None
    vote_share_sum: Decimal | None = None
    results: list[ReviewMatchCandidateResult] = Field(default_factory=list)

    @field_serializer("confidence", "vote_share_sum")
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        return self._decimal_to_float(value)


class ReviewDetail(ReviewQueueItem):
    election_type: str | None = None
    election_name: str | None = None
    wiki_page_title: str | None = None
    wiki_page_url: str | None = None
    wiki_revision_id: int | None = None
    turnout: Decimal | None = None
    lead: Decimal | None = None
    source_reference_ids: list[Any] = Field(default_factory=list)
    source_metadata: dict[str, Any] = Field(default_factory=dict)
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    updated_at: datetime | None = None
    results: list[ReviewResult]
    match_candidates: list[ReviewMatchCandidate] = Field(default_factory=list)
    latest_identity_event_confidence: Decimal | None = None
    latest_identity_event_at: datetime | None = None
    latest_payload_json: dict[str, Any] | None = None
    latest_payload_at: datetime | None = None
    latest_review_notes: str | None = None

    @field_serializer("turnout", "lead", "latest_identity_event_confidence")
    def serialize_detail_decimal(self, value: Decimal | None) -> float | None:
        return self._decimal_to_float(value)

    @field_serializer(
        "first_seen_at",
        "last_seen_at",
        "updated_at",
        "latest_identity_event_at",
        "latest_payload_at",
    )
    def serialize_detail_datetime(self, value: datetime | None) -> str | None:
        return None if value is None else value.isoformat()


class ReviewActionPayload(DecimalJSONModel):
    action: ReviewAction
    reviewer: str | None = None
    notes: str | None = None
    corrected_payload: dict[str, Any] = Field(default_factory=dict)


class ReviewActionResponse(DecimalJSONModel):
    poll_id: int
    review_action_id: int
    action: ReviewAction
