import pandas as pd
import geopandas as gpd
import numpy as np

def cleaning_gdf(df, geometry='geometry', id_gdf='id_n'):
    ## Seleccionamos solo las variables que nos interesan
    df=df[[id_gdf,geometry]].copy()
    return df
    
def variables_names(relation):
    if relation==1:
        p='n3_2'
        q='dum3_2'
    elif relation==2:
        p='n3_1'
        q='dum3_1'
    elif relation==3:
        p='n2_1'
        q='dum2_1'
    return p,q

def sjoin_den(gdf_1, gdf_2, relation_s):
    '''
    gdf_1 density's value < gdf_2 density's value
    '''
    var1,var2=variables_names(relation_s)
    
    p1 = gpd.sjoin(gdf_1, gdf_2, how="left", predicate='intersects')
    p1[var1]=np.where(p1.index_right.notna(),1,0) ##toma valor 1 cuando encuentra algún polígono de densidad 3.9 en el polígono de densidad 0.8
    p1=p1.groupby('id_n_left').sum().reset_index().sort_values(var1) ## se suma el número de continuos de densidad 3.9 en el polígono de densidad 0.8
    p1[var2]=np.where(p1[var1]>=1,1,0) ## Creamos una variable dummy 1 sí continene un continuo poblado de densidad 3; 0, no contiene un continuo poblado de densidad 3

    # # ## Nos quedamos con las variables que nos interesan 
    p1=p1[['id_n_left',var1,var2]].copy()
    return p1

def pre_tipology(gdf1, gdf2):
    ## Creamos la tipología de continuos poblados
    gdf1['tipology']='B0'
    gdf1['tipology']=np.where((gdf1.dum2_1==1)&(gdf1.n2_1==1),'B1',gdf1.tipology)
    gdf1['tipology']=np.where((gdf1.dum2_1==1)&(gdf1.n2_1>1),'B2',gdf1.tipology)
    gdf1['tipology']=np.where((gdf1.dum3_1==1)&(gdf1.n3_1==1),'C1',gdf1.tipology)
    gdf1['tipology']=np.where((gdf1.dum3_1==1)&(gdf1.n3_1>1),'C2',gdf1.tipology)

    gdf1['tipology']=np.where((gdf1.dum2_1==1)&(gdf1.n2_1==1)&(gdf1.dum3_1==1)&(gdf1.n3_1==1),'D1',gdf1.tipology)
    gdf1['tipology']=np.where((gdf1.dum2_1==1)&(gdf1.n2_1==1)&(gdf1.dum3_1==1)&(gdf1.n3_1>1),'D2',gdf1.tipology)
    gdf1['tipology']=np.where((gdf1.dum2_1==1)&(gdf1.n2_1>1)&(gdf1.dum3_1==1)&(gdf1.n3_1==1),'D3',gdf1.tipology)
    gdf1['tipology']=np.where((gdf1.dum2_1==1)&(gdf1.n2_1>1)&(gdf1.dum3_1==1)&(gdf1.n3_1>1),'D4',gdf1.tipology)
    
    gdf2['tipology']='E0'
    gdf2['tipology']=np.where((gdf2.dum3_2==1)&(gdf2.n3_2==1),'E1',gdf2.tipology)
    gdf2['tipology']=np.where((gdf2.dum3_2==1)&(gdf2.n3_2>1),'E2',gdf2.tipology)
    
    return gdf1,gdf2

def agg_gdf(np_1r,np_2r,np_3r):
    ##Mediana densidad con alta densidad
    p1=sjoin_den(np_2r,np_3r,1)
    ##Baja densidad con alta densidad
    p2=sjoin_den(np_1r,np_3r,2)
    ##Baja densidad con mediana
    p3=sjoin_den(np_1r,np_2r,3)
    
    p1_f=p3.merge(p2, on='id_n_left', how='outer', validate='1:1')
    ##Aplicamos la tipologia 
    p1_f,p1=pre_tipology(p1_f,p1)    
    
    ## Todos los NP de baja densidad con la variable de tipología 
    np_1r2=np_1r.merge(p1_f, left_on='id_n', right_on='id_n_left',
                       how='outer', validate='1:1', indicator=True)[['id_n_left','geometry','n3_1','dum3_1','tipology']] ##match perfecto
    
    ## Todos los NP de media densidad con la variable de tipología
    np_2r2=np_2r.merge(p1, left_on='id_n', right_on='id_n_left',
                   how='outer', validate='1:1', indicator=True)[['id_n_left','geometry','n3_2','dum3_2','tipology']] ##match perfecto

    return np_1r2, np_2r2

def spatial_tipology(np_1,np_2,np_3, geometry='geometry', id_gdf='id_n'):
    '''
    Returns a DataFrame containing the tipology for each density cluster 
    Parameters
    ----------
    np_1: High density GeoDataFrame
    np_2: Medium density GeoDataFrame
    np_3: Low density GeoDataFrame
    geometry: optional - Geometry's name
    id_gdf: optional - Identification value
    
    Notes
    -----
    To achive the right results it's so important keeping the suggestion GeoDataFrame orden: High density cluster (np_1), Medium density cluster (np_2) and low density cluster (np_3)
    '''
    np_1re=cleaning_gdf(np_1,geometry, id_gdf)
    np_2re=cleaning_gdf(np_2,geometry, id_gdf)
    np_3re=cleaning_gdf(np_3,geometry, id_gdf)
    
    np_1ref, np_2ref= agg_gdf(np_1re,np_2re,np_3re)
    
    np_1r3=gpd.sjoin(np_1ref[['tipology','geometry']], np_2ref, how="right", predicate='intersects')
    np_1r3['tipology_left']=np.where(np_1r3.index_left.isna(),np_1r3.tipology_right, np_1r3.tipology_left)
    np_1r3=np_1r3.reset_index()[['id_n_left','geometry','n3_2','dum3_2','tipology_left']].copy()
    np_1r3.rename({'tipology_left':'tipology'},axis=1, inplace=True)
    np_1r3["density"]="medium"

    np_3r2=gpd.sjoin(np_1ref[['tipology','geometry']], np_3re, how='right', predicate='intersects').reset_index()
    np_3r2['tipology_left']=np.where(np_3r2.index_left.isna(),'A0',np_3r2.tipology)
    np_3r2=np_3r2[['id_n','geometry','tipology_left']].copy()
    np_3r2.rename({'id_n':'id_n_left','tipology_left':'tipology'},axis=1, inplace=True)
    np_3r2["density"]="high"
    
    np_ft=(np_1ref.
           assign(density="low").
           append(np_1r3).
           append(np_3r2).
           rename({'id_n_left':'id_n'},axis=1))[['density','id_n','tipology']].copy()
    
    return np_ft
    