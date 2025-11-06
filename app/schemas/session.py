from datetime import datetime
from pydantic import BaseModel


class SessionOut(BaseModel):
    id: int
    ip: str | None
    user_agent: str | None
    created_at: datetime
    last_seen_at: datetime
    is_current: bool

    class Config:
        orm_mode = True
