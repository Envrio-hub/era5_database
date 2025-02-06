__version__='0.1.3'
__authors__=['Ioannis Tsakmakis']
__date_created__='2025-01-30'
__last_updated__='2025-02-06'

from database import models, schemas, engine
from sqlalchemy.orm import Session
from sqlalchemy import  select, and_
from databases_companion.decorators import DatabaseDecorators, DTypeValidator

db_decorator = DatabaseDecorators(SessionLocal=engine.SessionLocal, Session=Session)
dtype_validator = DTypeValidator()

class User:

    @staticmethod
    @db_decorator.session_handler_add_delete_update
    def add(user: schemas.UsersCreate, db: Session = None):
        new_user = models.Users(aws_user_name=user.aws_user_name, email=user.email, account_type=user.account_type, subscription_expires_in=user.subscription_expires_in)
        db.add(new_user)

    @staticmethod
    @dtype_validator.validate_str('aws_user_name')
    @db_decorator.session_handler_query
    def get_by_name(name: str, db: Session = None):
        return db.execute(select(models.Users).filter_by(aws_user_name=name)).one_or_none()

    @staticmethod
    @dtype_validator.validate_int('user_id')
    @db_decorator.session_handler_query
    def get_by_id(user_id: int, db: Session = None):
        return db.execute(select(models.Users).filter_by(user_id=user_id)).one_or_none()

    @staticmethod
    @dtype_validator.validate_str('email')
    @db_decorator.session_handler_query
    def get_by_email(email: str, db: Session = None):
        return db.execute(select(models.Users).filter_by(email=email)).one_or_none()

    @staticmethod
    @dtype_validator.validate_str('aws_user_name')
    @db_decorator.session_handler_add_delete_update
    def delete_by_name(name: str, db: Session = None):
            result = db.execute(select(models.Users).filter_by(aws_user_name=name)).one_or_none()
            if result is not None:
                db.delete(result.Users)
            else:
                return {"message": "Not Found", "errors": ["The provided name does not exist in the users table"]}, 404

class Variables:

    @staticmethod
    @db_decorator.session_handler_add_delete_update
    def add(parameter: schemas.VariablesCreate, db: Session = None):
        new_parameter = models.Variables(abbrev=parameter.abbrev, long_name=parameter.long_name, standar_name=parameter.standar_name, units=parameter.units)
        db.add(new_parameter)

    @staticmethod
    @db_decorator.session_handler_query
    def get_all(db: Session = None):
        result = db.execute(select(models.Variables))
        return result.scalars().all()

    @staticmethod
    @dtype_validator.validate_str('abbrev')
    @db_decorator.session_handler_query
    def get_by_abbrev(abbrev: str, db: Session = None):
        return db.execute(select(models.Variables).filter_by(abbrev = abbrev)).one_or_none()

    @staticmethod
    @dtype_validator.validate_int('variable_id')
    @db_decorator.session_handler_query
    def get_by_variable_id(variable_id: int, db: Session = None):
        return db.execute(select(models.Variables).filter_by(variable_id = variable_id)).one_or_none()

    @staticmethod
    @dtype_validator.validate_str('long_name')
    @db_decorator.session_handler_query
    def get_by_long_name(long_name: str, db: Session = None):
        return db.execute(select(models.Variables).filter_by(long_name = long_name)).one_or_none()
    
    @staticmethod
    @dtype_validator.validate_str('abbrev')
    @db_decorator.session_handler_query
    def get_unit_by_abbrev(abbrev: str, db: Session):
        result = db.execute(select(models.Variables).where(models.Variables.abbrev == abbrev))
        variable = result.scalars().first()
        return variable.units if variable else None

    @db_decorator.session_handler_add_delete_update
    def delete_by_abbrev(abbrev: str, db: Session = None):
            result = db.execute(select(models.Variables).filter_by(abbrev=abbrev)).one_or_none()
            if result is not None:
                db.delete(result.Variables)
            else:
                return {"message": "Not Found", "errors": ["The provided abbrev does not exist in the Variables table"]}, 404

class InfluxMapping:

    @staticmethod
    @db_decorator.session_handler_add_delete_update
    def add(entry: schemas.InfluxMappingCreate, db: Session = None):
        new_entry = models.InfluxMapping(measurement = entry.measurement, longitude = entry.longitude, latitude = entry.latitude)
        db.add(new_entry)

    @staticmethod
    @db_decorator.session_handler_query
    def get_all(db: Session = None):
        result = db.execute(select(models.InfluxMapping))
        return result.scalars().all()

    @staticmethod
    @dtype_validator.validate_decimal('lat_min', 'lat_max', 'long_min', 'long_max')
    @db_decorator.session_handler_query
    def get_by_lat_and_long_range(lat_min: float, lat_max: float, long_min: float, long_max: float, db: Session = None):
        return db.execute(select(models.InfluxMapping).where(and_(models.InfluxMapping.longitude >= long_min, models.InfluxMapping.longitude <= long_max,
                                                                  models.InfluxMapping.latitude >= lat_min, models.InfluxMapping.latitude <= lat_max))).all()

    @staticmethod
    @dtype_validator.validate_decimal('latitude', 'longitude')
    @db_decorator.session_handler_query
    def get_by_lat_and_long(latitude: float,longitude: float, db: Session = None):
        return db.execute(select(models.InfluxMapping).where(and_(models.InfluxMapping.longitude == longitude, models.InfluxMapping.latitude == latitude))).all()
    
    @staticmethod
    @dtype_validator.validate_list('measurement')
    @db_decorator.session_handler_query
    def get_by_measurement(measurement: list, db: Session = None):
        return db.execute(select(models.InfluxMapping).where(models.InfluxMapping.measurement.in_(measurement))).scalars().all()

    @staticmethod
    @dtype_validator.validate_decimal('latitude', 'longitude')
    @dtype_validator.validate_str('measurement')
    @db_decorator.session_handler_query
    def get_by_lat_and_long_and_measurement(latitude: float,longitude: float,measurement: str, db: Session = None):
        return db.execute(select(models.InfluxMapping).where(and_(models.InfluxMapping.longitude == longitude, models.InfluxMapping.latitude == latitude, models.InfluxMapping.measurement == measurement))).one_or_none()
