# pylint: disable=too-few-public-methods

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Parameters
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')

    # JWT Secret
    JWT_SECRET = os.getenv('JWT_SECRET')

    # Harbor Registry Parameters
    HARBOR_HOST = os.getenv("HARBOR_HOST")
    HARBOR_USER = os.getenv("HARBOR_USER")
    HARBOR_PASSWORD = os.getenv("HARBOR_PASSWORD")
    HARBOR_PROJECT = os.getenv("HARBOR_PROJECT")

    # LDAP Parameters
    LDAP_HOST = os.getenv("LDAP_HOST")
    LDAP_ENABLE_TLS = os.getenv("LDAP_ENABLE_TLS").lower() == 'yes'
    LDAP_CA_PATH = os.getenv("LDAP_CA_PATH")
    LDAP_USER_BASE_DN = os.getenv("LDAP_USER_BASE_DN")
    LDAP_ADMIN_GROUP_DN = os.getenv("LDAP_ADMIN_GROUP_DN")

    # Flask
    LOG_PATH = None # None -> stdout
    LOGGING_LEVEL = "info"
    DEBUG = False

class DevelopmentConfig(Config):
    LOG_PATH = "./judge.log"
    LOGGING_LEVEL = "debug"
    DEBUG = True
