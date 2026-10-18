
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    UserUpdate,
    UserProfileUpdate
)
from app.core.security import hash_password, verify_password
from app.core.jwt_utils import create_access_token
from app.core.dependencies import get_current_user, require_admin


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    new_user = User(
        name=user_data.name,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user




@router.post("/login", response_model=Token)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if (
        user is None
        or not verify_password(
            user_data.password,
            user.hashed_password if user else ""
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    access_token = create_access_token(user_id=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }



@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user




@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    if "email" in update_data:
        existing_user = db.scalar(
            select(User).where(
                User.email == update_data["email"],
                User.id != user_id,
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        update_data["email"] = str(update_data["email"])

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user




@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    update_data = profile_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    if "email" in update_data:
        existing_user = db.scalar(
            select(User).where(
                User.email == update_data["email"],
                User.id != current_user.id,
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        update_data["email"] = str(update_data["email"])

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user




@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.is_active = False

    db.commit()

    return None





