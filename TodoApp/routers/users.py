from fastapi import APIRouter, Path, Depends
from models import Users
from fastapi import HTTPException
from starlette import status
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    password: str = Field(min_length=3, max_length=50)
    new_password: str = Field(min_length=3, max_length=50)


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail=f"User with id {user.get("id")} not found")
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    return {"message": "Password changed successfully"}

@router.put("/change-phone-number", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail=f"User with id {user.get("id")} not found")
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
    return {"message": "Phone number changed successfully"}

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Users).filter(Users.id == user.get("id")).first()




