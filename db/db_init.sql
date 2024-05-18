DROP DATABASE IF EXISTS cells_model_validation_db;
CREATE DATABASE cells_model_validation_db;

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE TABLE anp(id serial, 
    id_anp varchar(20), 
    nombre varchar(300) not null, 
    cat_manejo varchar(20),
    estados varchar(200),
    municipios varchar(500),
    region varchar(200),
    superficie float, 
    s_terres float, 
    s_marina float, 
    prim_dec date,
    ult_dof date,
    pcm1 date,
    sinap varchar(30),
    cov_ integer,
    cov_id integer,
    geom geometry not null,
    centroid geometry not null);

CREATE TABLE colouration(id serial, 
    id_cell integer not null,
    id_colour integer not null);

ALTER TABLE colouration ADD COLUMN created_at timestamp DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE "user"(id serial, 
    username varchar(100) not null,
    id_user_external bigint,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    "role" varchar(20) not null
);

CREATE TABLE user_anp_relations( id serial, 
    id_user bigint not null,
    id_anp bigint not null,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO user_anp_relations(id_user, id_anp) SELECT 1, id FROM anp LIMIT 20;

ALTER TABLE colouration ADD COLUMN id_user bigint not null;

ALTER TABLE "user" ADD COLUMN "password" varchar(100) not null; 

INSERT INTO "user"(username, "role", "password") VALUES ('promero@conabio.gob.mx', 'ADMIN', md5('Qwerty123'));

ALTER TABLE colouration ADD COLUMN id_anp bigint not null;

ALTER TABLE colouration ADD COLUMN updated_at timestamp DEFAULT CURRENT_TIMESTAMP;