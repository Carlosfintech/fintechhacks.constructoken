"""Hop Sauna

SPDX-FileCopyrightText: Copyright (C) Whythawk and Hop Sauna Authors ask@whythawk.com
SPDX-License-Identifier: AGPL-3.0-or-later

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http:#www.gnu.org/licenses/>.

"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.orm import Session

from app.core.config import settings
from app import crud, models, schemas
from app.api import deps

router = APIRouter(lifespan=deps.get_lifespan)


@router.post("/order/{id}", response_model=schemas.Msg)
@router.post("/order/{id}/{volume}", response_model=schemas.Msg)
def place_product_order(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    id: str,
    volume: int = 1,
    buyer_wallet: str = Body(...),
    creator: Annotated[models.Actor | None, Depends(deps.get_optional_creator)],
) -> Any:
    """
    Place a product order for a given volume of an item.
    """
    if not isinstance(volume, int) or volume < 1:
        raise HTTPException(
            status_code=400,
            detail="Inapropriate order.",
        )
    print("-------------------------------place_product_order------------------------------------")
    print(id, volume, buyer_wallet, creator)
    product = {
        "id": "01K24SCPT4JG59FYRVE5RXPX7J",
        "name": "Barb Rouge - Standard",
        "description": "1 kg, vaccuum-sealed for freshness.",
        "value": "2500",
        "assetCode": "EUR",
        "assetScale": 2,
    }
    print("-------------------------------place_product_order------------------------------------")
    # 1. SET UP THE ORDER
    seller_wallet = settings.TEST_SELLER_WALLET
    seller_key = settings.TEST_SELLER_KEY
    seller = schemas.SellerOpenPaymentAccount(
        **{
            "walletAddressUrl": seller_wallet,
            "privateKey": seller_key,
            "keyId": settings.TEST_SELLER_KEY_ID,
        }
    )
    order = crud.OpenPaymentsProcessor(
        seller=seller,
        buyer=buyer_wallet,
        redirect_uri=settings.DEFAULT_REDIRECT_AFTER_AUTH,
    )
    amount = str(int(product["value"]) * volume)
    # 2. SELLER INCOMING PAYMENT PROCESS
    incoming_payment_response = order.request_incoming_payment(amount=amount)
    print("-------------------------------incoming_payment_response------------------------------------")
    print(incoming_payment_response)
    print("-------------------------------incoming_payment_response------------------------------------")
    # 3. BUYER QUOTE REQUEST PROCESS
    quote_request_response = order.request_quote(incoming_payment_id=incoming_payment_response.id)
    print("-------------------------------quote_request_response------------------------------------")
    print(quote_request_response)
    print("-------------------------------quote_request_response------------------------------------")
    # This could be returned to the buyer for review, but we'll skip this for now...
    # 4. REQUEST BUYER INTERACTIVE GRANT FOR PURCHASE
    purchase_endpoint = order.get_purchase_endpoint(amount=amount)
    print("-------------------------------purchase_endpoint------------------------------------")
    print(purchase_endpoint)
    print("-------------------------------purchase_endpoint------------------------------------")
    return {"msg": str(purchase_endpoint)}


@router.post("/fulfil/{key}", status_code=status.HTTP_202_ACCEPTED)
def fulfil_product_order(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    key: str,
    hash: str,
    interact_ref: str,
    creator: Annotated[models.Actor | None, Depends(deps.get_optional_creator)],
) -> Any:
    """
    Fulfil the product order and associate the purchase to the buyer.
    """
    print("-------------------------------fulfil_product_order------------------------------------")
    print("key", key)
    print("hash", hash)
    print("interact_ref", interact_ref)
    print("-------------------------------fulfil_product_order------------------------------------")
    # 1. GET THE REQUIRED ORDER REFERENCE FROM THE KEY
    seller_wallet = settings.TEST_SELLER_WALLET
    seller_key = settings.TEST_SELLER_KEY
    buyer_wallet = settings.TEST_BUYER_WALLET
    seller = schemas.SellerOpenPaymentAccount(
        **{
            "walletAddressUrl": seller_wallet,
            "privateKey": seller_key,
            "keyId": settings.TEST_SELLER_KEY_ID,
        }
    )
    payment = crud.OpenPaymentsProcessor(seller=seller, buyer=buyer_wallet)

    # # 5. COMPLETE OUTGOING PAYMENT
    # # This depends on the app ... can divide up payments between collaborators, take platform fees, etc.
    # incoming_payment_response = payment.complete_payment(interact_ref=interact_ref, received_hash=hash, pending_payment)
    # print("-------------------------------incoming_payment_response------------------------------------")
    # print(incoming_payment_response)
    # print("-------------------------------incoming_payment_response------------------------------------")
