from app.schemas.common import APIModel


class PartyRead(APIModel):
    party_key: str
    party_raw: str | None = None
    poll_count: int
