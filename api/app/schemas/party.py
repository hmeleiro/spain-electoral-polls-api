from app.schemas.common import APIModel


class PartyRead(APIModel):
    party_key: str
    party_name: str
    short_name: str
    territory_code: str
    color_hex: str | None = None
    display_order: int | None = None
    is_active: bool
    poll_count: int = 0
