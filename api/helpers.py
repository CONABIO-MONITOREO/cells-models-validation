import os
import psycopg2
from dotenv import load_dotenv
import cryptocode
import json
from datetime import datetime, timedelta

load_dotenv()

dbname = os.getenv('POSTGRES_DB')
dbuser = os.getenv('POSTGRES_USER')
dbpass = os.getenv('POSTGRES_PASSWORD')
dbhost = os.getenv('POSTGRES_HOST')
dbport = os.getenv('POSTGRES_PORT')
jwtkey = os.getenv('JWTKEY')

conn = psycopg2.connect(f'dbname={dbname} user={dbuser} \
                        password={dbpass} host={dbhost} port={dbport}')


def get_anp(anp_id):
    cur = conn.cursor()
    cur.execute(f"SELECT st_asgeojson(geom), st_asgeojson(centroid) \
                FROM anp WHERE id = {anp_id}")
    data = cur.fetchone()
    cur.close()
    return data


def get_anps(user_id):
    cur = conn.cursor()
    cur.execute(f"SELECT a.id, a.nombre, st_asgeojson(a.geom) FROM anp as a \
                JOIN user_anp_relations as b ON a.id=b.id_anp WHERE b.id_user = {user_id} ORDER BY a.nombre")
    data = cur.fetchall()
    cur.close()
    return data


def get_grid_anp(anp_id, user_id):
    cur = conn.cursor()
    cur.execute(f"SELECT a.id, st_asgeojson(a.geom), CASE WHEN id_user = {user_id} THEN c.id_colour ELSE null END \
                FROM grid_1km as a JOIN anp as b ON st_intersects(a.geom, b.geom) \
                LEFT JOIN colouration as c ON a.id=c.id_cell \
                WHERE b.id = {anp_id}")
    data = cur.fetchall()
    cur.close()
    return data


def insert_colouration(colouration, user_id, anp_id):
    try:
        cur = conn.cursor()
        for cell in colouration:
            cur.execute(f"SELECT * FROM colouration \
                        WHERE id_cell={cell['id']} AND id_user={user_id} AND id_anp={anp_id}")
            aux = cur.fetchall()
            if len(aux) > 0:
                if cell['colour'] != 0:
                    cur.execute(f"UPDATE colouration SET id_colour={cell['colour']}, updated_at=NOW() \
                            WHERE id_cell={cell['id']} AND id_user={user_id} AND id_anp={anp_id}")
                else:
                    cur.execute(f"DELETE FROM colouration \
                                WHERE id_cell={cell['id']} AND id_user={user_id} AND id_anp={anp_id}")
            else:
                if cell['colour'] != 0:
                    cur.execute(f"INSERT INTO colouration(id_cell, id_colour, id_user, id_anp) \
                            VALUES ({cell['id']}, {cell['colour']}, {user_id}, {anp_id})")
        conn.commit()
        cur.close()
    except Exception as e:
        print(str(e))
        return False
    finally:
        cur.close()
    return True


def login(email, password):
    data = None
    try:
        cur = conn.cursor()
        cur.execute(f'SELECT id, "role" FROM "user" WHERE username=\'{email}\' and password=md5(\'{password}\')')
        data = cur.fetchone()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        cur.close()
    return data


def encrypt_bearer_token(id_user):
    current_datetime = datetime.now()
    current_datetime = current_datetime + timedelta(days=1)
    current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    data = {'id_user': id_user, 'ends_at': current_datetime}
    string_data = json.dumps(data)
    bearer_token = cryptocode.encrypt(string_data, jwtkey)
    return bearer_token


def validate_bearer_token(headers):
    try:
        bearer_token = headers['Authorization'].split(' ')[1]
        string_data = cryptocode.decrypt(bearer_token, jwtkey)
        data = json.loads(string_data)
        ends_at = datetime.strptime(data['ends_at'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() > ends_at:
            print('jwt expirado')
        return  data['id_user']
    except Exception as e:
        print('Error al validar el jwt', str(e))
    return None


def get_cells_by_polygon(polygon, id_anp):
    data = None
    try:
        cur = conn.cursor()
        cur.execute(f'SELECT a.id, st_asgeojson(a.geom), c.id_colour \
                    FROM grid_1km as a JOIN anp as b ON st_intersects(a.geom, b.geom) \
                    LEFT JOIN colouration as c ON a.id=c.id_cell \
                    WHERE b.id={id_anp} and \
                        st_intersects(st_setsrid(a.geom, 4326), st_setsrid(st_geomfromgeojson(\'{polygon}\'), 4326))')
        data = cur.fetchall()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        cur.close()
    return data

def get_dashboard_data():
    data = None
    try:
        cur = conn.cursor()
        cur.execute(f'select id_user, c.username, (count(id_cell)::float/b.n_cells::float)*100 as progress, a.id_anp, b.nombre as anp_name, max(updated_at) as updated_at \
                    from colouration as a \
                    LEFT JOIN anp as b ON a.id_anp=b.id \
                    LEFT JOIN "user" as c ON a.id_user=c.id \
                    group by id_user, c.username, a.id_anp, b.nombre, b.n_cells \
                    order by updated_at desc, id_user')
        data = cur.fetchall()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        cur.close()
    return data



