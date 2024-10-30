from passlib.context import CryptContext


__pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash_password(password: str) -> str:
    return __pwd_context.hash(password)


async def verify_password(password: str, hashed_password: str) -> bool:
    return __pwd_context.verify(password, hashed_password)
