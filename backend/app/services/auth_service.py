from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.core.security import hash_password, verify_password
from app.models import User


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.username == username, User.is_active.is_(True)))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def change_password(db: Session, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise BusinessError(400, "旧密码不正确")
    user.password_hash = hash_password(new_password)
    db.commit()
