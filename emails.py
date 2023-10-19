import jwt
from fastapi import (
    BackgroundTasks,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
    status,
)
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List

from dotenv import dotenv_values
from models import User

config_credentials = dotenv_values(".env")

conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials["EMAIL"],
    MAIL_PASSWORD=config_credentials["PASS"],
    MAIL_FROM=config_credentials["EMAIL"],
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


class EmailSchema(BaseModel):
    email: List[EmailStr]


async def send_email(email: List, instance: User):
    token_data = {"id": instance.id, "username": instance.user_name}

    token = jwt.encode(token_data, config_credentials["SECRET"], algorithm="HS256")

    template = f"""
        <!DOCTYPE html>
        <html>
            <head>
            <body>
                <div style = "display: flex; align-items: center; justify-content: center; flex-direction: column;">
                    <h3>Account Verification</h3>
                    <br>
                    <p>Thank you for registering with us, please click on the link below to verify your account</p>
                    <a style="margin-top:1rem; padding: 1rem; border-radius: 0.5rem;
                    background-color: #0275d8; text-decoration: none; font-size: 1rem; color: white;"
                    href="http://localhost:8000/verification/?token={token}">
                        Verify your email
                    </a>
                    <p> please kindly  ignore this email if you did not register </p>
                </div>
            </body>
            </head>
        </html>
    """

    message = MessageSchema(
        subject="Account Verification",
        recipients=email,
        body=template,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message=message)
