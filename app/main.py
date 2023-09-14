import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from .tools import is_valid_pwd, get_hash, encrypt_secret, decrypt_secret


app = FastAPI()
client = MongoClient(os.environ["CONN_MONGODB_URL"])
secret_db = client["one-secret-db"]
# secret_db.posts.delete_many({}) # drop all db data on start


class SecretInStruct(BaseModel):
    secret: str
    pwd: str


class SecretGetStruct(BaseModel):
    pwd: str


@app.post("/generate")
async def creare_secret_key(data: SecretInStruct) -> str:
    """
    Генератор секретов
    На вход принимает json с секрет-строкой, кодовой фразой и отдает secret_key
    """
    if not is_valid_pwd(data.pwd):
        return HTMLResponse(
            content="""Need body like '{"secret": "foo", "pwd": "bar"}'""",
            status_code=422  # Unprocessable Entity
        )

    # insert in db
    item = {"secret": encrypt_secret(data.secret, data.pwd), "pwd_hash": get_hash(data.pwd), "retry_count": 4}
    secret_key = secret_db.posts.insert_one(item).inserted_id

    return HTMLResponse(content=str(secret_key))


@app.post("/secrets/{secret_key}")
async def get_secret(secret_key: str, data: SecretGetStruct) -> str:
    """
    Возвращатель секретов
    На вход принимает json с кодовой фразой (паролем) и отдает secret
    Можно пару раз ввести неправильный пароль, но секрет вернет только один раз
    """
    try:
        item = secret_db.posts.find_one({"_id": ObjectId(secret_key)})
    except Exception:
        item = None
    if not item:
        return HTMLResponse(content=f"No secret by {secret_key}", status_code=404)  # Not Found

    if not is_valid_pwd(data.pwd):
        return HTMLResponse(
            content="""Need body like '{"pwd": "foo"}'""",
            status_code=422  # Unprocessable Entity
        )
    if item.get("pwd_hash", "__None__") != get_hash(data.pwd):
        if item.get("retry_count", 1) <= 1:
            secret_db.posts.delete_many({"_id": ObjectId(secret_key)})
        else:
            secret_db.posts.update_one({"_id": ObjectId(secret_key)}, {'$inc': {"retry_count": -1}})
        return HTMLResponse(content="""Invalid body "pwd" """, status_code=403)  # Forbidden

    secret_db.posts.delete_many({"_id": ObjectId(secret_key)})
    return HTMLResponse(content=decrypt_secret(item["secret"], data.pwd))
