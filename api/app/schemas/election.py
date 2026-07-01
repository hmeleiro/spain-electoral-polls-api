from datetime import date

from app.schemas.common import APIModel


class ElectionRead(APIModel):
    id: int
    election_key: str
    election_type: str
    territory_code: str
    election_name: str
    election_date: date | None = None
