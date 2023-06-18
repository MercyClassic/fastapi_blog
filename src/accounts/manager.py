from typing import Optional
import os
from dotenv import load_dotenv
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from src.accounts.models import User
from src.accounts.utils import get_user_db


load_dotenv()


SECRET = os.getenv('SECRET_TOKEN_FOR_EMAIL')


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        # here must be send email for verification


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)