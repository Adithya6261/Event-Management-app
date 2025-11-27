from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import Token, UserCreate, UserRead
from app.services import auth_service

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user_dependency(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    return auth_service.get_current_user(db=db, token=token)


@auth_router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_create: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    return auth_service.create_user(db=db, user_create=user_create)


@auth_router.post("/login", response_model=Token, response_model_exclude_none=True)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = auth_service.authenticate_user(db=db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token_for_user(user)
    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/me", response_model=UserRead)
def read_current_user(user=Depends(get_current_user_dependency)) -> UserRead:
    return user
