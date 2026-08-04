from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import User


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.username == username, User.is_active.is_(True)))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user
