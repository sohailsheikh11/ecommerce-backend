
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate


def add_to_cart(
    db: Session,
    user_id: int,
    item_data: CartItemCreate,
) -> Cart:
    try:
        # 1. Check whether the product exists.
        product = db.get(Product, item_data.product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        # 2. Find the customer's cart.
        statement = select(Cart).where(Cart.user_id == user_id)
        cart = db.scalars(statement).first()

        # 3. Create a cart if this customer doesn't have one.
        if cart is None:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.flush()

        # 4. Check whether this product is already in the cart.
        item_statement = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product.id,
        )

        cart_item = db.scalars(item_statement).first()

        # 5. Add a new item or increase its quantity.
        if cart_item is None:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=item_data.quantity,
            )
            db.add(cart_item)
        else:
            new_quantity = cart_item.quantity + item_data.quantity

            if new_quantity > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cart quantity cannot exceed 100.",
                )

            cart_item.quantity = new_quantity

        # 6. Save the changes.
        db.commit()
        db.refresh(cart)

        # Load the items so they can be returned in the response.
        _ = cart.items

        return cart

    except Exception:
        db.rollback()
        raise



def get_cart(db: Session, user_id: int) -> Cart:
    statement =  (
        select(Cart)
        .where(Cart.user_id == user_id)
    )

    cart = db.scalars(statement).first()

    if cart is None:
        cart = Cart(user_id = user_id)
        db.add(cart)
        db.commit()
        db.refresh()



    _ = cart.items

    return cart
