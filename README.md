# cells-models-validation

This repository contains the three layers for deploying the 1km grid models validation application.

## Dependencias

- PostgreSQL >= 13 + PostGIS
- Python >= 3.11

Las dependencias especificas de Python se pueden instalar con pip con 

```
    $> pip install -r requirements.txt
```

## Preparación de la DB

1. Crear base de datos, desde el motor de base de datos

```
    $> CREATE DATABASE cells_model_validation_db;
```

2. Conectarse a la base de datos

```
    $> \c cells_model_validation_db;
```

3. Crear las extensiones para información geográfica

```
    $> CREATE EXTENSION IF NOT EXISTS postgis;
    $> CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

4. Correr el script para insertar las ANPs `process_anps.py` desde linea de comandos

```
    $> cd api/
    $> python process_anps.py
    $> cd ..
```

5. Correr el script de escructura de base de datos `db_init.sql`,  desde linea de comandos

```
    $> psql -U postgres -d cells_model_validation_db < db/db_init.sql
```

## Conexión del API con la DB

Se espera tener un archivo de variables de ambiente `.env`, con las siguientes variables

```
POSTGRES_DB=cells_model_validation_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

Cuando este proyecto se corre sin contenedor de docker el archivo `.env` se debe meter
en el directorio `api/`.

## Conexión del front con el API

En la función de inicialización del archivo `front/login.html` se tienen las lineas

```
//var baseUrlApi = 'http://127.0.0.1:555';
//var baseUrlApi = 'http://api:5000';
//var baseUrlApi = 'https://cosmos-validacion-integridad-sipecam.conabio.gob.mx/api/';
```

Se debe descomentar la primera, es decir, debe quedar así 

```
var baseUrlApi = 'http://127.0.0.1:555';
//var baseUrlApi = 'http://api:5000';
//var baseUrlApi = 'https://cosmos-validacion-integridad-sipecam.conabio.gob.mx/api/';
```

Se debe hacer de la misma manera en la función de inicialización para el `front/script.js`.

## Desplegar en modo desarrollo

* Correr el API

```
    $> cd api/
    $> flask --app api run --host=0.0.0.0
```

* Montar un servidor de desarrollo para el front

```
    $> cd front/
    $> python -m http.server
```