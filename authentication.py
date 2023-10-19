from fastapi.exceptions import HTTPException
from fastapi import status
from passlib.context import CryptContext
from dotenv import dotenv_values
import jwt
from models import User

config_credentials = dotenv_values(".env")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str):
    return pwd_context.hash(password)


async def very_token(token: str):
    try:
        payload = jwt.decode(token, config_credentials["SECRET"], algorithms=["HS256"])
        user = await User.get(id=payload["id"])

    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(user_name: str, password: str):
    user = await User.get(user_name=user_name)

    if user and verify_password(password, user.password):
        return user
    return False


async def token_generator(user_name: str, password: str):
    user = await authenticate_user(user_name, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"id": user.id, "user_name": user.user_name}

    token = jwt.encode(token_data, config_credentials["SECRET"], algorithm="HS256")

    return token
