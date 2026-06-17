# era5_database

A Python library for managing the ERA5 climate dataset database. It provides an ORM layer over a MySQL database with spatial support (PostGIS-style geometry via GeoAlchemy2) and integrates with InfluxDB for time-series data.

**Version:** 0.1.8  
**Authors:** Ioannis Tsakmakis, Nikolaos Kokkos  
**License:** Apache 2.0

---

## Requirements

- Python >= 3.12
- MySQL with spatial extension enabled
- InfluxDB instance

---

## Installation

```bash
pip install git+https://github.com/Envrio-hub/era5_database.git
```

Or clone and install locally:

```bash
git clone https://github.com/Envrio-hub/era5_database.git
cd era5_database
pip install .
```

### Dependencies

| Package | Version |
|---|---|
| sqlalchemy | >= 2.0.37 |
| mysql-connector-python | >= 9.2.0 |
| pydantic | >= 2.10.6 |
| GeoAlchemy2 | >= 0.17.1 |
| influxdb-client | >= 1.48.0 |
| databases_companion | Envrio-hub/databases_companion@main |
| aws_utils | Envrio-hub/aws_utils@main |

---

## Database Schema

### `grid`
Stores the spatial grid cells from the ERA5 dataset.

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-incremented |
| `name` | String | Optional label |
| `latitude` | Numeric(10,6) | Latitude in decimal degrees |
| `longitude` | Numeric(10,6) | Longitude in decimal degrees |
| `mean_elevation` | Integer | Optional mean elevation (m) |
| `geom` | Geometry(POINT, 4326) | Spatial index column |

### `variables`
Stores ERA5 meteorological variable definitions.

| Column | Type | Description |
|---|---|---|
| `variables_id` | Integer PK | Auto-incremented |
| `abbrev` | String(60) | Short name (e.g. `t2m`, `tp`) |
| `long_name` | String(100) | Descriptive name |
| `standard_name` | String(100) | CF convention name |
| `units` | String(100) | Units string |
| `variable_source_type` | Enum | Measurement category |
| `cell_methods` | String(255) | Optional CF cell methods |

### `influx_mapping`
Maps (variable, location) pairs to InfluxDB measurements.

| Column | Type | Description |
|---|---|---|
| `influx_id` | Integer PK | Auto-incremented |
| `measurement` | String (FK → variables.abbrev) | ERA5 variable abbreviation |
| `latitude` | Numeric(10,6) | Grid cell latitude |
| `longitude` | Numeric(10,6) | Grid cell longitude |
| `start_timestamp` | Float | Unix timestamp of first record |
| `end_timestamp` | Float | Unix timestamp of last record |

Unique constraint on `(measurement, latitude, longitude)`.

---

## Usage

### Create the database tables

```python
from era5_database.models import Base
from era5_database.engine import engine

Base.metadata.create_all(engine)
```

### Add a grid cell

```python
from era5_database import crud, schemas
from decimal import Decimal

cell = schemas.GridCreate(
    name="cell_01",
    latitude=Decimal("41.750"),
    longitude=Decimal("21.500")
)
crud.Grid.add(cell=cell)
```

### Populate grid from a CSV file

```python
import pandas as pd
from decimal import Decimal
from era5_database import crud, schemas

cols = pd.read_csv('data/t2m.csv', sep=',', index_col='valid_time').columns

for col in cols:
    lat, lon = col.split('_')
    cell = schemas.GridCreate(
        name="",
        latitude=Decimal(lat).quantize(Decimal('0.001')),
        longitude=Decimal(lon).quantize(Decimal('0.001'))
    )
    crud.Grid.add(cell=cell)
```

### Register ERA5 variables

```python
import json
from era5_database import crud, schemas

with open('era5_variables_mapping.json') as f:
    variables = json.load(f)

for key, meta in variables.items():
    if not crud.Variables.get_by_abbrev(abbrev=key):
        variable = schemas.VariablesCreate(
            abbrev=key,
            long_name=meta['long_name'],
            standar_name=meta['standar_name'],
            units=meta['units']
        )
        crud.Variables.add(parameter=variable)
```

### Add an InfluxDB mapping entry

```python
from era5_database import crud, schemas

entry = schemas.InfluxMappingCreate(
    measurement='t2m',
    longitude=21.50,
    latitude=41.75,
    start_timestamp=1700000000.0,
    end_timestamp=1700086400.0
)
crud.InfluxMapping.add(entry=entry)
```

### Find the nearest grid cell to a point

```python
from era5_database import crud

nearest = crud.Grid.find_nearest(lon_query=21.5, lat_query=41.75)
```

---

## Database Migrations (Alembic)

Generate a new migration after changing `models.py`:

```bash
alembic revision --autogenerate -m "describe your change"
```

Apply all pending migrations:

```bash
alembic upgrade head
```

Rollback one migration:

```bash
alembic downgrade -1
```
