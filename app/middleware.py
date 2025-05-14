#middleware.py
from fastapi import Request, HTTPException
from functools import wraps
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET")

def auth_needed(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        if request is None:
            raise RuntimeError("Request object not found in route arguments.")

        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Usuario não autenticado")

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return await func(*args, cookie=payload, **kwargs)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return wrapper
