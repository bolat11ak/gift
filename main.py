from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory="front", html=True), name="static")


@app.get("/")
def serve_home():
    return FileResponse("front/index.html")


DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "6082f8d84e86160ce78c1849a2f2bf65af448b0e03f53061055a7860eda2f9b8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    wish_lists = relationship("WishList", back_populates="owner")
    celebrations = relationship("Celebration", back_populates="owner")


class WishList(Base):
    __tablename__ = "wish_lists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="wish_lists")


class Celebration(Base):
    __tablename__ = "celebrations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    date = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="celebrations")


Base.metadata.create_all(bind=engine)


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str


class WishListCreate(BaseModel):
    name: str


class WishListResponse(BaseModel):
    id: int
    name: str


class CelebrationCreate(BaseModel):
    title: str
    date: str


class CelebrationResponse(BaseModel):
    id: int
    title: str
    date: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@app.post("/signup", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/wishlists", response_model=WishListResponse)
def create_wishlist(wishlist: WishListCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_wishlist = WishList(name=wishlist.name, owner=user)
    db.add(new_wishlist)
    db.commit()
    db.refresh(new_wishlist)
    return new_wishlist


@app.get("/wishlists", response_model=List[WishListResponse])
def get_wishlists(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(WishList).filter(WishList.user_id == user.id is True).all()


@app.post("/celebrations", response_model=CelebrationResponse)
def create_celebration(celebration: CelebrationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_celebration = Celebration(title=celebration.title, date=celebration.date, owner=user)
    db.add(new_celebration)
    db.commit()
    db.refresh(new_celebration)
    return new_celebration


@app.get("/celebrations", response_model=List[CelebrationResponse])
def get_celebrations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Celebration).filter(Celebration.user_id == user.id is True).all()

