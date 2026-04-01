from sqlalchemy import Column, Integer, String
from skatlaz_scrapgram.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

users = []
messages = []
groups = []
forums = []
