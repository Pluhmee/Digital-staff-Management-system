# Configuration file for Flask and database
import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    # SECRET_KEY = '1234567890'
    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'staff.db')}"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False# SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/staff.db'
    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.mailersend.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER='MS_AItpcz@test-nrw7gym1wp2g2k8e.mlsender.net'
    MAIL_USERNAME = 'MS_AItpcz@test-nrw7gym1wp2g2k8e.mlsender.net'
    MAIL_PASSWORD = 'mssp.VZk6p6X.pxkjn413nv0gz781.HyOHr06'
