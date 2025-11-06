from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session as OrmSession
from app.models.session import Session as SessionModel

SESSION_TTL_DAYS = 30


def cleanup_old_sessions(db: OrmSession) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=SESSION_TTL_DAYS)
    (
        db.query(SessionModel)
        .filter(SessionModel.last_seen_at < cutoff)
        .delete(synchronize_session=False)
    )
    db.commit()
