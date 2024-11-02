from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)


Base = declarative_base()


class UserAccounts(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    mails = relationship("UserMails", back_populates="accounts")


class UserLikes(Base):
    __tablename__ = "user_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_mails.id'))
    other_user_id = Column(Integer, ForeignKey('user_mails.id'))
    liked_at = Column(DateTime, default=func.now())

    user_mail = relationship("UserMails", foreign_keys=[user_id], back_populates="likes_user_id")
    other_user_mail = relationship("UserMails", foreign_keys=[other_user_id], back_populates="likes_other_user_id")


class UserMails(Base):
    __tablename__ = 'user_mails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_accounts.id'))
    email = Column(String, unique=True)
    gender = Column(String)

    names = relationship("UserNames", back_populates="mails", uselist=False)
    avatars = relationship("UserAvatars", back_populates="mails", uselist=False)
    accounts = relationship("UserAccounts", back_populates="mails")
    likes_user_id = relationship("UserLikes", foreign_keys=[UserLikes.user_id], back_populates="user_mail")
    likes_other_user_id = relationship("UserLikes", foreign_keys=[UserLikes.other_user_id], back_populates="other_user_mail")    

class UserNames(Base):
    __tablename__ = 'user_names'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_mails.user_id'))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    mails = relationship("UserMails", back_populates="names")



class UserAvatars(Base):
    __tablename__ = 'user_avatars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_mails.user_id'))
    avatar_way = Column(String, nullable=False)

    mails = relationship("UserMails", back_populates="avatars")


