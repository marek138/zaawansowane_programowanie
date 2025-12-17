import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from sqlalchemy.orm import Session
from sqlalchemy import select

from users_db import engine, Base
from models import User

app = FastAPI()

Base.metadata.create_all(bind=engine)

SECRET_KEY = "CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_session():
    with Session(engine) as session:
        yield session


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def roles_to_list(roles_str: str) -> list[str]:
    roles_str = (roles_str or "").strip()
    return [r.strip() for r in roles_str.split(",") if r.strip()]


def roles_to_str(roles: list[str]) -> str:
    return ",".join(roles)


def create_access_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        roles = payload.get("roles", [])
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return {"username": username, "roles": roles}


def require_admin(current=Depends(get_current_user)):
    if "ROLE_ADMIN" not in current["roles"]:
        raise HTTPException(status_code=403, detail="Admin required")
    return current


# 1) /login
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.username == form_data.username))
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")

    token = create_access_token({
        "sub": user.username,
        "roles": roles_to_list(user.roles),
    })
    return {"access_token": token, "token_type": "bearer"}


# 4,6) POST /users (admin-only)
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    body: dict,
    session: Session = Depends(get_session),
    _admin=Depends(require_admin),
):
    username = body["username"]
    password = body["password"]
    roles = body.get("roles", ["ROLE_USER"])

    existing = session.scalar(select(User).where(User.username == username))
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=username,
        hashed_password=hash_password(password),
        roles=roles_to_str(roles),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "username": user.username, "roles": roles_to_list(user.roles)}


# 7) /user_details
@app.get("/user_details")
def user_details(current=Depends(get_current_user)):
    return current


# 5) “Zabezpiecz wszystkie endpointy” – tu masz przykład chronionego endpointu
@app.get("/protected")
def protected(_current=Depends(get_current_user)):
    return {"ok": True}


def create_initial_admin():
    with Session(engine) as session:
        admin = session.scalar(select(User).where(User.username == "admin"))
        if admin is None:
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                roles="ROLE_ADMIN"
            )
            session.add(admin)
            session.commit()

create_initial_admin()