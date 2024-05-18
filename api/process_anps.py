#!/usr/bin/env python
# coding: utf-8

# In[29]:


import os
import json
import psycopg2
from osgeo import ogr
from dotenv import load_dotenv


# In[1]:


#get_ipython().system('ls ./anp0224/')


# In[31]:


load_dotenv()

dbname = os.getenv('POSTGRES_DB')
dbuser = os.getenv('POSTGRES_USER')
dbpass = os.getenv('POSTGRES_PASSWORD')
dbhost = os.getenv('POSTGRES_HOST')
dbport = os.getenv('POSTGRES_PORT')


# In[38]:


shapefile = ogr.Open("./anp0224/anpfb2024gw.shp")
layer = shapefile.GetLayer(0)
crs = layer.GetSpatialRef()

insert_sql = """INSERT INTO anp(id_anp, nombre, cat_manejo, estados, municipios, region, superficie, s_terres, s_marina,
    prim_dec, ult_dof, pcm1, sinap, cov_, cov_id, geom, centroid) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', {6}, {7}, 
    {8}, '{9}', '{10}', {11}, '{12}', {13}, {14}, '{15}', '{16}')"""

try:
    conn = psycopg2.connect(f'dbname={dbname} user={dbuser} password={dbpass} host={dbhost} port={dbport}')
    cur = conn.cursor()

    for i in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(i)
        feature_obj = feature.items()
        
        print(i+1, feature_obj['NOMBRE'])
        geometry = feature.GetGeometryRef()
        centroid = geometry.Centroid()
        
        if feature_obj['PCM1'] != None:
            pcm1 = feature_obj['PCM1'].split('/')
            pcm1.reverse()
            pcm1 = "/".join(pcm1)
            pcm1 = "'" + pcm1 + "'"
        
        cur.execute(insert_sql.format(feature_obj['ID_ANP'], feature_obj['NOMBRE'].replace("'", ""), 
            feature_obj['CAT_MANEJO'], feature_obj['ESTADOS'].replace("'", ""), feature_obj['MUNICIPIOS'].replace("'", ""), 
            feature_obj['REGION'], feature_obj['SUPERFICIE'], feature_obj['S_TERRES'], 
            feature_obj['S_MARINA'], feature_obj['PRIM_DEC'], feature_obj['ULT_DOF'], 
            pcm1, feature_obj['SINAP'], feature_obj['COV_'], feature_obj['COV_ID'], 
            geometry, centroid))
        
except Exception as e:
    print(str(e))
finally:
    conn.commit()
    cur.close()
    conn.close()


# In[41]:


try:
    conn = psycopg2.connect(f'dbname={dbname} user={dbuser} password={dbpass} host={dbhost} port={dbport}')
    cur = conn.cursor()
    cur.execute("CREATE TABLE cover as SELECT ST_Envelope(ST_Union(geom)) as geom FROM anp")
except Exception as e:
    print(str(e))
finally:
    conn.commit()
    cur.close()
    conn.close()


# In[42]:


try:
    conn = psycopg2.connect(f'dbname={dbname} user={dbuser} password={dbpass} host={dbhost} port={dbport}')
    cur = conn.cursor()
    cur.execute("CREATE TABLE grid_1km AS select geom from (select (ST_SquareGrid(0.009, geom)).* from cover) as a")
    cur.execute("ALTER TABLE grid_1km ADD COLUMN id serial")
except Exception as e:
    print(str(e))
finally:
    conn.commit()
    cur.close()
    conn.close()


# In[43]:


try:
    conn = psycopg2.connect(f'dbname={dbname} user={dbuser} password={dbpass} host={dbhost} port={dbport}')
    cur = conn.cursor()
    cur.execute("CREATE INDEX idx_grid_1km_id ON grid_1km USING GIST (geom);")
except Exception as e:
    print(str(e))
finally:
    conn.commit()
    cur.close()
    conn.close()


# In[ ]:




