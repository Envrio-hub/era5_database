__version__='1.3.0'
__author__=['Ioannis Tsakmakis']
__date_created__='2023-11-16'
__last_updated__='2026-05-03'

from influxdb_client import InfluxDBClient, Bucket, BucketRetentionRules
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta
from typing import Annotated, List, Literal
from pydantic import Field
from aws_utils.aws_utils import SecretsManager
from dotenv import load_dotenv
from era5_database.engine import SessionLocal
from databases_companion.decorators import DatabaseDecorators
from envrio_logger.logger import influxdb
from sqlalchemy.orm import Session
from decimal import Decimal
import os
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

# Disable the MissingPivotFunction warning
warnings.simplefilter("ignore", MissingPivotFunction)

# Load variables from the .env file
load_dotenv()

# Instantiate decorators
db_decorators = DatabaseDecorators(SessionLocal=SessionLocal, Session=Session)

# Create enum classes for data validation
StatisticType = Literal['mean', 'max', 'min']

class InfluxConnector():

    def __init__(self, bucket_name: str):
        influx_conf = SecretsManager().get_secret(secret_name=os.getenv('db_timeseries'))
        self.client = InfluxDBClient(url=influx_conf['url'], token=influx_conf['token'], org=influx_conf['org'])
        if not self.client.ping():
            influxdb.error("Connection to InfluxDB failed.")
            raise ConnectionError("Connection to InfluxDB failed.")
        self.bucket_name = bucket_name
        self.org = influx_conf['org']

class DataManagement(InfluxConnector):

    @db_decorators.influxdb_error_handler
    def write_point(self, measurement:str, sensor_id:int, unit:str, data:dict):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        records =[]
        for i in range(0,len(data['date_time'])):
            point = {
                'measurement': measurement,
                'tags': {'sensor_id': sensor_id},
                'fields': {unit: round(float(data['values'][i]),2) if data['values'][i] is not None else data['values'][i]},
                'time': data['date_time'][i].strftime('%Y-%m-%dT%H:%M:%S')
                }
            records.append(point)
        write_api.write(bucket=self.bucket_name, org=self.org, record=records)
        influxdb.info(f"message: Data successfully persisted to the bucket: {self.bucket_name}, measurement: {measurement}")        

    @db_decorators.influxdb_error_handler
    def delete_rows(self, measurement:str, tag:str, start:datetime, stop:datetime = None):
        if stop is None:
            stop = datetime.now()
        delete_api = self.client.delete_api()
        delete_api.delete(start, stop, predicate = f'_measurement = "{measurement}" and sensor_id = "{tag}"', bucket = self.bucket_name, org = self.org)
        influxdb.info(f"message: Data successfully deleted from the bucket: {self.bucket_name}, measurement: {measurement}, sensor_id: {tag}, from: {start} to: {stop}")

    @db_decorators.influxdb_error_handler
    def query_data_raw(self, measurement: str, sensor_id: int, unit: str,
                       start: Annotated[Decimal, Field(max_digits=15, decimal_places=3)] = None,
                       stop: Annotated[Decimal, Field(max_digits=15, decimal_places=3)] = None):
        if start is None:
            start = Decimal(str(round((datetime.now() - timedelta(days=1)).timestamp(), 3)))
        if stop is None:
            stop = Decimal(str(round(datetime.now().timestamp(), 3)))

        query_api = self.client.query_api()
        data_frame = query_api.query_data_frame(f'''from(bucket:"{self.bucket_name}") 
                                                    |> range(start: {datetime.fromtimestamp(float(start)).strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {datetime.fromtimestamp(float(stop)).strftime("%Y-%m-%dT%H:%M:%SZ")}) 
                                                    |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["sensor_id"] == "{sensor_id}")
                                                    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                                                    |> keep(columns: ["_time","sensor_id", "{unit}"])''')
        influxdb.info(f"message: Data from bucket: {self.bucket_name}, measurement: {measurement}, sensor_id: {sensor_id} between: {start} and {stop} retrived successfully")
        return data_frame
    
    @db_decorators.influxdb_error_handler
    def query_data_raw_lists(self,measurements: List, sensor_ids: List,
                       start: Annotated[Decimal, Field(max_digits=15, decimal_places=3)] =  None,
                       stop: Annotated[Decimal, Field(max_digits=15, decimal_places=3)] = None):
        if start is None:
            start = Decimal(str(round((datetime.now() - timedelta(days=1)).timestamp(), 3)))
        if stop is None:
            stop = Decimal(str(round(datetime.now().timestamp(), 3)))

        query_api = self.client.query_api()
        m_conditions = " or ".join([f'r["_measurement"] == "{m}"' for m in measurements])
        s_conditions = " or ".join([f'r["sensor_id"] == "{sid}"' for sid in sensor_ids])
        data_frame = query_api.query_data_frame(f'''from(bucket:"{self.bucket_name}")
                                                    |> range(start: {datetime.fromtimestamp(float(start)).strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {datetime.fromtimestamp(float(stop)).strftime("%Y-%m-%dT%H:%M:%SZ")}) 
                                                    |> filter(fn: (r) => ({m_conditions}) and ({s_conditions}))
                                                    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")''')
        influxdb.info(f"message: Data from bucket: {self.bucket_name}, measurement: {measurements}, sensor_id: {sensor_ids} between: {start} and {stop} retrived successfully")
        return data_frame
    
    @db_decorators.influxdb_error_handler
    def query_data_hourly(self,measurement: str,sensor_id: int,unit: str, start: datetime, stop: datetime = None):
        if stop is None:
            stop = datetime.now()
        query_api = self.client.query_api()
        data_frame = query_api.query_data_frame(f'''from(bucket:"{self.bucket_name}") 
                                                    |> range(start: {start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {stop.strftime("%Y-%m-%dT%H:%M:%SZ")}) 
                                                    |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["sensor_id"] == "{str(sensor_id)}" and r["_field"] == "{unit}")
                                                    |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
                                                    ''')
        influxdb.info(f"message: Data from bucket: {self.bucket_name}, measurement: {measurement}, sensor_id: {sensor_id} between: {start} and {stop} retrived successfully")
        return data_frame
    
    @db_decorators.influxdb_error_handler
    def query_data_statistic(self,measurement: str,sensor_id: int,unit: str, statistic: StatisticType,
                             start: datetime, stop: datetime = None):
        if stop is None:
            stop = datetime.now()
        query_api = self.client.query_api()
        data_frame = query_api.query_data_frame(f'''from(bucket:"{self.bucket_name}") 
                                                |> range(start: {start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {stop.strftime("%Y-%m-%dT%H:%M:%SZ")}) 
                                                |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["sensor_id"] == "{str(sensor_id)}" and r["_field"] == "{unit}")
                                                |> {statistic}()
                                                ''')
        influxdb.info(f"message: Data from bucket: {self.bucket_name}, measurement: {measurement}, sensor_id: {sensor_id} between: {start} and {stop} retrived successfully")
        return data_frame

    @db_decorators.influxdb_error_handler
    def query_data_stats(self,measurement: str,sensor_id: int,unit: str,start: datetime, stop: datetime = None):
        if stop is None:
            stop = datetime.now()
        query_api = self.client.query_api()
        data_frame = query_api.query_data_frame(f'''data = from(bucket:"{self.bucket_name}") 
                                                |> range(start: {start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {stop.strftime("%Y-%m-%dT%H:%M:%SZ")}) 
                                                |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["sensor_id"] == "{str(sensor_id)}" and r["_field"] == "{unit}")
                                                
                                                mean_val = data |> mean() |> map(fn: (r) => ({{r with stat: "mean"}}))
                                                max_val  = data |> max()  |> map(fn: (r) => ({{r with stat: "max"}}))
                                                min_val  = data |> min()  |> map(fn: (r) => ({{r with stat: "min"}}))
                                                
                                                union(tables: [mean_val, max_val, min_val])
                                                ''')
        influxdb.info(f"message: Data from bucket: {self.bucket_name}, measurement: {measurement}, sensor_id: {sensor_id} between: {start} and {stop} retrived successfully")
        return data_frame

class BucketConfiguration(InfluxConnector):
    
    @db_decorators.influxdb_error_handler
    def list_buckets(self):
        buckets_api = self.client.buckets_api()
        buckets = buckets_api.find_buckets().buckets
        print("\n".join([f" ---\n ID: {bucket.id}\n Name: {bucket.name}\n Retention: {bucket.retention_rules}"
                for bucket in buckets]))
        return buckets
    
    @db_decorators.influxdb_error_handler
    def update_bucket(self, type='expire', data_duration=0, shard_group_duration=630720000, description='Update to a 20 years shard group duration'):
        buckets_api = self.client.buckets_api()
        bucket_info = buckets_api.find_bucket_by_name(self.bucket_name)
        bucket_id = str(bucket_info.id)
        org_id = str(bucket_info.org_id)
        bucket_update = Bucket(
                                description = description,
                                id = bucket_id,
                                name = self.bucket_name,
                                org_id = org_id,
                                retention_rules = [BucketRetentionRules(every_seconds = data_duration,
                                                                        shard_group_duration_seconds = shard_group_duration,
                                                                        type = type)])
        buckets_api.update_bucket(bucket = bucket_update)
        influxdb.info(f"message: bucket: {self.bucket_name} updated succefully - {buckets_api.find_bucket_by_name(self.bucket_name)}")
        
        print(buckets_api.find_bucket_by_name(self.bucket_name))
