from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.fastapi import register_tortoise
from models import *

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Hello World"}


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)