from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Text,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)


Base = declarative_base()


class UserAccounts(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    mails = relationship("UserMails", back_populates="accounts")


class UserAccountsLog(Base):
    __tablename__ = "user_accounts_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_accounts.id'), nullable=False)
    action = Column(String, nullable=False)
    changed_column = Column(String, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    action_timestamp = Column(DateTime, default=func.now())


class UserMails(Base):
    __tablename__ = 'user_mails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_accounts.id'))
    email = Column(String, unique=True)
    gender = Column(String)

    names = relationship("UserNames", back_populates="mails", uselist=False)
    avatars = relationship("UserAvatars", back_populates="mails", uselist=False)
    accounts = relationship("UserAccounts", back_populates="mails")
    


class UserMailsLog(Base):
    __tablename__ = "user_mails_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_mails.user_id'), nullable=False)

    action = Column(String, nullable=False)
    changed_column = Column(String, nullable=True) 
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    action_timestamp = Column(DateTime, default=func.now())


class UserNames(Base):
    __tablename__ = 'user_names'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_mails.user_id'))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    mails = relationship("UserMails", back_populates="names")


class UserNamesLog(Base):
    __tablename__ = "user_names_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_names.user_id'), nullable=False)
    action = Column(String, nullable=False)
    changed_column = Column(String, nullable=True)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    action_timestamp = Column(DateTime, default=func.now())


class UserAvatars(Base):
    __tablename__ = 'user_avatars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_mails.user_id'))
    avatar_way = Column(String, nullable=False)

    mails = relationship("UserMails", back_populates="avatars")


class UserAvatarsLog(Base):
    __tablename__ = "user_avatars_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_avatars.user_id'), nullable=False)
    action = Column(String, nullable=False) 
    changed_column = Column(String, nullable=True)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    action_timestamp = Column(DateTime, default=func.now())
