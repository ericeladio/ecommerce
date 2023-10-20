from fastapi import FastAPI, Request, HTTPException, status, Depends
from tortoise.contrib.fastapi import register_tortoise
from models import *

# authentication
from authentication import *
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import *

# response classes
from fastapi.responses import HTMLResponse

# templates
from fastapi.templating import Jinja2Templates

# images Upload
from fastapi import File, UploadFile
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image


app = FastAPI()

oath2_schema = OAuth2PasswordBearer(tokenUrl="token")

# static files  setup config
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/token")
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oath2_schema)):
    try:
        payload = jwt.decode(token, config_credentials["SECRET"], algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await user


@app.post("/user/me")
async def user_login(user: user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(owner=user)
    return {
        "status": "ok",
        "data": {
            "user_name": user.user_name,
            "email": user.email,
            "verified": user.is_verified,
            "joined_date": user.join_date.strftime("%Y-%m-%d %H:%M:%S"),
        },
    }


# a signals
@post_save(User)
async def create_business(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    if created:
        business_obj = await Business.create(
            business_name=instance.user_name, owner=instance
        )
        await business_pydantic.from_tortoise_orm(business_obj)
        # send the email
        await send_email([instance.email], instance)


@app.post("/registration")
async def user(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)  # create Model
    new_user = await user_pydantic.from_tortoise_orm(user_obj)  # inser data orm
    return {
        "status": "success",
        "data": f"Hello{new_user.user_name}, thank you for registering, chek your email and click on the link to verify your account",
    }


templates = Jinja2Templates(directory="templates")


@app.get("/verification", response_class=HTMLResponse)
async def email_verification(resquest: Request, token: str):
    user = await very_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse(
            "verification.html", {"request": resquest, "username": user.user_name}
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/")
def index():
    return {"message": "Hello World"}


@app.post("/uploadfile/profile")
async def create_upload_file(
    file: UploadFile = File(...), user: user_pydantic = Depends(get_current_user)
):
    FILEPATH = "./static/images"
    file_name = file.filename
    extension = file_name.split(".")[1]

    if extension not in ["png", "jpg"]:
        return {"status": "eror", "detail": "invalid file extension"}

    token_name = secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()

    with open(generated_name, "wb") as file:
        file.write(file_content)

    img = Image.open(generated_name)
    img = img.resize((200, 200))
    img.save(generated_name)

    file.close()

    business = await Business.get(owner=user)
    owner = await business.owner

    if owner == user:
        business.logo = token_name
        await business.save()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    file_url = "localhost:8000" + generated_name[1:]
    return {"status": "ok", "filename": file_url}


@app.post("/uploadfile/product/{id}")
# check for product owner before making the changes.
async def create_upload_file(
    id: int,
    file: UploadFile = File(...),
    user: user_pydantic = Depends(get_current_user),
):
    FILEPATH = "./static/images/"
    filename = file.file_name
    extension = filename.split(".")[1]

    if extension not in ["png", "jpg"]:
        return {"status": "eror", "detail": "invalid file extension"}

    token_name = secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()

    with open(generated_name, "wb") as file:
        file.write(file_content)

    # pillow
    img = Image.open(generated_name)
    img = img.resize(size=(200, 200))
    img.save(generated_name)

    file.close()

    # get product details
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner

    # check if the user making the request is authenticated
    if owner == user:
        product.product_image = token_name
        await product.save()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    file_url = "localhost:8000" + generated_name[1:]
    return {"status": "ok", "filename": file_url}


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
