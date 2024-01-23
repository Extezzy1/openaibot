import json
from hashlib import sha256
from typing import Union
from fastapi import FastAPI, Request
import utils
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from db_ import db
import hashlib

app = FastAPI()

origins = ["*"]

# app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/payment/{bot_id}")
async def payment(bot_id: int, request: Request):
    notification_secret = "I9sOFqDV/VZxMjPeeeHRZKFx"
    keys = {"notification_type": "", "operation_id": "", "amount": "", "currency": "", "datetime": "", "sender": "",
            "codepro": "", "label": ""}

    response = await request.body()
    print(response)
    response_split = response.decode("utf-8").split("&")
    bill_id = None
    for item in response_split:
        if keys.get(item.split("=")[0], False):
            keys[item.split("=")[0]] = item.split("=")[1]
        if item.split("=")[0] == "label":
            bill_id = item.split("=")[1]
    print(keys)
    sha = hashlib.sha1(f"{keys['notification_type']}{keys['operation_id']}{keys['amount']}{keys['currency']}{keys['datetime']}{keys['sender']}{keys['codepro']}{notification_secret}{keys['label']}".encode("utf-8")).hexdigest()
    print(sha)
    if bill_id is None:
        return {"message": "bill id is None"}

    db.update_payment_done(bill_id, bot_id)
    # db.update_payment_done(bill_id)
    return {"message": "success"}
