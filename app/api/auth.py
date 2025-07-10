from fastapi import APIRouter, Depends, HTTPException, status, Security, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.api_key import APIKeyHeader
from app.core.jwt_utils import create_access_token, decode_access_token
from app.models.user import User, UserCreate, UserLogin, UserRead
from app.core.database_session import get_db
from app.core.config import config

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

api_key_header = APIKeyHeader(name=config.api_key_name, auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user = db.query(User).filter(User.username == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def get_api_key(request: Request, api_key: str = Security(api_key_header)):
    if api_key and api_key == config.api_key:
        return api_key
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

def get_current_user_or_apikey(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    api_key: str = Security(api_key_header)
):
    if config.auth_method == "jwt":
        return get_current_user(token, db)
    elif config.auth_method == "api_key":
        if api_key and api_key == config.api_key:
            return {"api_key": api_key}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    else:
        raise HTTPException(status_code=500, detail="Invalid auth method config")

@router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = User(username=user_in.username, email=user_in.email)
    user.set_password(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user_or_apikey)):
    return current_user 