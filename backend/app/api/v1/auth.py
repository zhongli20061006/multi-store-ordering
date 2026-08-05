from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.core.security import create_access_token
from app.schemas.auth import ChangePasswordRequest, LoginRequest, TokenResponse, UserOut
from app.services.auth_service import authenticate, change_password
from app.api.v1.deps import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, payload.username, payload.password)
    if user is None:
        raise BusinessError(401, "用户名或密码错误")
    return ok(TokenResponse(access_token=create_access_token(user.id)).model_dump())


@router.get("/me")
def me(user=Depends(get_current_user)):
    return ok(UserOut.model_validate(user).model_dump())


@router.post("/change-password")
def change_password_endpoint(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    change_password(db, user, payload.old_password, payload.new_password)
    return ok({"changed": True})
