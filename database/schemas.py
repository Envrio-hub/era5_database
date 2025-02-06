__version__='0.1.2'
__author__=['Ioannis Tsakmakis']
__date_created__='2025-01-30'
__last_updated__='2025-02-0'

from pydantic import BaseModel
from databases_companion.enum_variables import AccountType

# Base Models
class UsersBase(BaseModel):
    aws_user_name: str
    email: str
    account_type: AccountType
    subscription_expires_in: float

class VariablesBase(BaseModel):
    
    abbrev: str
    long_name: str
    standar_name: str
    units: str

class InfluxMappingBase(BaseModel):
    
    measurement: str
    latitude: float
    longitude: float
    start_timestamp: float
    end_timestamp: float

# Create Models

class UsersCreate(UsersBase):
    pass

class VariablesCreate(VariablesBase):
    pass

class InfluxMappingCreate(InfluxMappingBase):
    pass
