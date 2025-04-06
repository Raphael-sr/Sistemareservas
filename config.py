import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'd3949d51431a594d06711d4bde5327b0'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "database.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
