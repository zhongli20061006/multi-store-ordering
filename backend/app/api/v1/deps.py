from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.security import decode_access_token
from app.models import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise BusinessError(401, "未登录")
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise BusinessError(401, "登录已失效，请重新登录")
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise BusinessError(401, "账号不可用")
    return user


def get_user_store_ids(user: User) -> set[int]:
    return {link.store_id for link in user.store_links}


def ensure_store_access(user: User, store_id: int) -> None:
    if store_id not in get_user_store_ids(user):
        raise BusinessError(403, "无权操作该门店")
