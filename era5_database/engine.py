__version__='0.1.1'
__author__=['Ioannis Tsakmakis']
__date_created__='2025-01-27'
__last_updated__='2025-11-06'

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session
from aws_utils.aws_utils import SecretsManager
from dotenv import load_dotenv
from envrio_logger.logger import alchemy
import os

# Load variables from the .env file
load_dotenv()

# Access database configuration info
db_conf = SecretsManager().get_secret(secret_name=os.getenv('era5'))

# Creating sqlalchemy engine
try:
    engine = create_engine(url=f'{db_conf["DBAPI"]}://{db_conf["username"]}:{db_conf['password']}@{db_conf["host-ip"]}/{os.getenv('db_name1')}',
                        pool_size=30, max_overflow=5, pool_recycle=7200)
except Exception as e:
    alchemy.error(f"Error occurred during engine creation: {str(e)}")
    
SessionLocal = scoped_session(sessionmaker(bind=engine))

class Base(DeclarativeBase):
    pass
