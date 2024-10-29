from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)


Base = declarative_base()


class UserAccounts(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    mail = relationship("UserMails", back_populates="accounts")


class UserMails(Base):
    __tablename__ = 'user_mails'

    id = Column(Integer, ForeignKey('user_accounts.id'), primary_key=True)
    email = Column(String, unique=True)
    gender = Column(String)
    name = relationship("UserNames", back_populates="mail", uselist=False)
    avatar = relationship("UserAvatars", back_populates="mail", uselist=False)
    account = relationship("UserAccounts", back_populates="mails")


class UserNames(Base):
    __tablename__ = 'user_names'

    id = Column(Integer, ForeignKey('user_mails.id'), primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    participant = relationship("UserMails", back_populates="name")


class UserAvatars(Base):
    __tablename__ = 'user_avatars'

    id = Column(Integer, ForeignKey('user_mails.id'), primary_key=True)
    avatar_way = Column(String, nullable=False)

    participant = relationship("UserMails", back_populates="avatar")


