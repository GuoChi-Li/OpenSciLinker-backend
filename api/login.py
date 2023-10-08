from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database.dataSchema import get_db, User
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

router = APIRouter()

# Initialize password context with bcrypt scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


########## Pydantic Models ##########
class RegisterOutput(BaseModel):
    message: str
    username: str = None
    email: str = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class CheckUserExistenceRequest(BaseModel):
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    email: str = None
    username: str = None
    isSuccess: int = 0


########## Utility Functions ##########
def get_user_by_email(db: Session, email: str) -> User:
    """Fetch a user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create and save a new user."""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    try:
        db.add(db_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"error": "Username or email already exists!"}
    db.refresh(db_user)
    return db_user


def verify_password(plain_password: str, correct_hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, correct_hashed_password)


def get_user_by_username(db: Session, username: str) -> User:
    """Fetch a user by username."""
    return db.query(User).filter(User.username == username).first()


########## API Endpoints ##########
@router.get("/")
def read_root() -> dict:
    """Provide a welcome message."""
    return {"message": "Welcome to the API!"}


@router.post("/register", response_model=RegisterOutput)
def register(user: UserCreate, db: Session = Depends(get_db)) -> RegisterOutput:
    """Register a new user."""
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        return RegisterOutput(message="Email already registered")

    user_obj = create_user(db, user)
    return RegisterOutput(
        message="Registration successful",
        username=user_obj.username,
        email=user_obj.email,
    )


@router.get("/test")
def test_route() -> dict:
    """Endpoint for testing purposes."""
    return {"message": "This is a test route!"}


@router.post("/check_user_existence")
def check_user_existence(
    request_data: CheckUserExistenceRequest, db: Session = Depends(get_db)
) -> dict:
    """Check if a user exists by email."""
    user = get_user_by_email(db, email=request_data.email)
    if user:
        return {
            "message": "User exists",
            "User ID": user.email,
            "Username": user.username,
        }
    else:
        return {"message": "User does not exist"}


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Login a user."""
    user = get_user_by_email(db, email=request.email)

    if not user or not verify_password(request.password, user.password):
        return LoginResponse(message="Invalid username or password", isSuccess=0)

    return LoginResponse(
        message="Login successful",
        email=user.email,
        username=user.username,
        isSuccess=1,
    )
