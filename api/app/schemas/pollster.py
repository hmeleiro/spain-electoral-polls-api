from app.schemas.common import APIModel


class PollsterRead(APIModel):
    id: int
    pollster_key: str
    pollster_name: str
    poll_count: int
