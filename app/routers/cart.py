
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartResponse
from app.services.cart_service import add_to_cart, get_cart


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
def add_cart_item(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_to_cart(
        db=db,
        user_id=current_user.id,
        item_data=item_data,
    )


@router.get("/", response_model=CartResponse)
def get_mycart(db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),):

    return get_cart(
        db=db,
        user_id=current_user.id,
    )

    

