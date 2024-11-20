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

ALTER TABLE colouration ADD COLUMN id_user bigint not null;

ALTER TABLE "user" ADD COLUMN "password" varchar(100) not null; 

INSERT INTO "user"(username, "role", "password") VALUES ('promero@conabio.gob.mx', 'ADMIN', md5('Qwerty123'));

ALTER TABLE colouration ADD COLUMN id_anp bigint not null;

ALTER TABLE colouration ADD COLUMN updated_at timestamp DEFAULT CURRENT_TIMESTAMP;

INSERT INTO "user"(username, "role", "password") VALUES ('mariana.munguia@conabio.gob.mx', 'ADMIN', md5('c5Lk9QN3'));


INSERT INTO user_anp_relations(id_user, id_anp) SELECT 1, id FROM anp;

alter table anp add  column n_cells integer not null default -1;

update anp set n_cells=array_length(ARRAY(select b.id FROM anp as a JOIN grid_1km as b on st_intersects(a.geom, b.geom) WHERE a.id=anp.id), 1);

CREATE INDEX idx_anp_geom ON anp USING GIST (geom);

CREATE INDEX idx_anp_nombre ON anp(nombre);
CREATE INDEX idx_anp_id ON anp(id);

CREATE INDEX idx_grid_1km_geom ON grid_1km USING GIST (geom);
CREATE INDEX idx_grid_1km_id ON anp(id);

CREATE INDEX idx_user_anp_relations_id_user ON user_anp_relations(id_user);

CREATE INDEX idx_user_anp_relations_id_anp ON user_anp_relations(id_anp);

CREATE INDEX idx_colouration_id_user ON colouration(id_user);

CREATE INDEX idx_colouration_id_anp ON colouration(id_anp);

--select pg_terminate_backend(pid) from pg_stat_activity;