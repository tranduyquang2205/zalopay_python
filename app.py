import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import sys
import traceback
from api_response import APIResponse

app = FastAPI()

from zalopay import Zalopay


@app.get("/")
def read_root():
    return {"Hello": "World"}

class LoginDetails(BaseModel):
    username: str
    password: str
    cookies: str
    proxy_list: list

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
    try:
        zalopay = Zalopay(input.username,input.password,input.cookies,input.proxy_list)
        balance = zalopay.get_balance()
        return APIResponse.json_format(balance)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)  
    
class Transactions(BaseModel):
    username: str
    password: str
    cookies: str
    limit: int
    proxy_list: list
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
    try:
        zalopay = Zalopay(input.username,input.password,input.cookies,input.proxy_list)
        history = zalopay.get_transactions(input.limit)
        return APIResponse.json_format(history)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)  

class Transfer_Item(BaseModel):
    account_number: str
    amount: int
    description: str
    bank_code: str
class Transfer(BaseModel):
    username: str
    password: str
    cookies: str
    proxy_list: list
    transfer_item: Transfer_Item
@app.post('/transfer_money', tags=["transfer_money"])
def get_transactions_api(input: Transfer):
    try:
        zalopay = Zalopay(input.username,input.password,input.cookies,input.proxy_list)
        history = zalopay.transfer_money_bank(input.transfer_item)
        return APIResponse.json_format(history)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)  


if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)


