import pandas as pd
import geopandas as gpd

import numpy as np
import rasterio as rio 

from rasterio import features                                                                                 
from shapely.geometry import Polygon                   
from pyproj import CRS                                 

########################################################

### WE'VE STARTED DEFINING A PAIR OF FUNCTION FOR OPENING THE RASTER AND THE SHP OF CCPP
def open_raster_rio(path_r):
    with rio.open(path_r) as val_density:
        band_1=val_density.read(1, masked=True)         
        band_1_aff=val_density.transform                
        return band_1, band_1_aff

### BEFORE APPLYING THE FEATURES()'S FUNCTION WE'VE TO RECODE THE RASTER'S VALUES STORED IN THE FIRST BAND AS BOOLEAN. BY DOING THIS, THE FUNCTION WILL RETRIVE ONLY THE DATA OF INTEREST
def recode_raster(density_val, band=None):                   
    if band is not None:
        band_re=band.copy()
        band_re[band_re < density_val] = 0
        band_re[band_re >= density_val] = 1
    return band_re

### SINCE THE FEATURES()'S FUNCTION RETRIEVES A PAIR OF DATA (GEOMETRY AND VALUE), IS NECESSARY TO DEFINE A FUNCTION FOR EXTRACTING AND CONVERTING THE RETRIVED GEOMETRY TO POLYGON.
### TO DO THIS WE GOING TO USE SHAPELY'S FUNCTION NAMED POLYGON
def extract_coord(coor, close_holes=False):
    coor_tuple=coor.get('coordinates') 
    
    if close_holes==False:
        if len(coor_tuple)>1:          
            interior_num=list(range(1,len(coor_tuple)))
            poly=Polygon(coor_tuple[0], [coor_tuple[interior_coor] for interior_coor in interior_num])
        else:                          
             poly=Polygon(coor_tuple[0])
    else:
        poly=Polygon(coor_tuple[0])
    return poly

### THE FUNCTION "EXTRACT_SHAPES" RETRIEVE THE POLYGONS FROM THE DENSITY'S RASTER ACCORDING TO AN ESPECIFIED DENSITY VALUE.
def extract_shapes(density_val_2, band_ex_2, band_1_aff_2, close_holes, crs_EPSG):
    data={'raw_geometry':[]}
    
    band_ex_2=recode_raster(density_val_2, band_ex_2)                             
    mask_shp = band_ex_2 == 1                                                    
    for geom, value in features.shapes(band_ex_2,                                
                                       mask=mask_shp, transform=band_1_aff_2,    
                                       connectivity=4):                          
        data['raw_geometry'].append(extract_coord(geom, close_holes))
    
    den_1=gpd.GeoDataFrame(data, geometry='raw_geometry')                        
    den_1.crs = CRS.from_epsg(crs_EPSG)                                             
    return den_1

### SINCE THE CONTINUUM ARE DEFINED AS POLYGONES WITH WITH A MINIMUN NUMBER OF PEOPLE, WE NEED TO PASS THE POPULATION'S DATA IN ORDER TO ONLY KEEP THE POLYGON THAT MATCH THE GIVEN CRITERIA.
def population_criteria(density_shp,ccpp_x, pob_min_0):
    pob_d1=density_shp.sjoin(ccpp_x, how='right',predicate='contains')          

    pob_d1=pob_d1.dropna(subset=['index_left']).groupby('index_left').sum()     
    pob_d1=pob_d1[pob_d1.pob_tot17>=pob_min_0].copy()                           

    den_1f=density_shp.merge(pob_d1, left_index=True, right_index=True, how='inner')                                       
    return den_1f

### AT LAST, WE CALL THE FUNCTION DEFINED ABOVE TO CREATE A NEW FUNCTION NAMED CONTINUUM WHICH RETRIEVE POLYGONS ACCORDING THE DENSITY'S VALUE AND THE MINIMUN POPULATION ACCEPTED
def create_continuum(density_val_3, density_tif=None, band=None, affine=None, ccpp_shp=None, pob_minima=None, no_holes=False, crs_EPSG=32718):
    """
    - density_val_3: It's the density's value that will be used tu create the urban-rural continuoun
    - density_tif: optinal - it's the raster's path to create the urban-rural continuoun
    - band: optional - if it's provided, the function use the specified band instead of open rasterio
    - affain: optional - if it's provided the function use the specified raster's affain 
    - ccpp_shp: opional - it's the ccpp's shape that include population data for each ccpp
    - pob_minima: opional - it's the minimun value of population accepted for creating the urban-rural continoun
    - no_holes: opional - If it's True the retrived shapes haven't have any holes in their interior
    - crs_EPSG: optional - Default = EPSG:32718. It's the projection value used to project the new shape
    """
    if density_tif is None:
        den_1=extract_shapes(density_val_3, band, affine, no_holes, crs_EPSG)      
    else:
        band, affine=open_raster_rio(density_tif)                                  
        den_1=extract_shapes(density_val_3, band, affine, no_holes, crs_EPSG)      
    
    if (ccpp_shp is None) & (pob_minima is None):
        return den_1
    else:
        shp_density= population_criteria(den_1,ccpp_shp, pob_minima)               
        return shp_density