from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from settings import settings


auth_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenAuthenticator:
    async def create_access_token(
        self,
        data: dict,
        expires_delta: timedelta = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ENCRYPTION
        )

    async def get_current_user(
        self,
        token: str = Depends(OAuth2PasswordBearer)
    ):
        id = None
        username = None
        email = None
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима аутентификация",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ENCRYPTION]
            )

            id: str = payload.get("id")
            username: str = payload.get("username")
            email: str = payload.get("email")
            if id is None or username is None or email is None:
                raise credentials_exception

        except JWTError:
            raise credentials_exception
        return id, username, email
