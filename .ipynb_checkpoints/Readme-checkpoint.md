## ESP
# Continium urbano-rural

Continium urbano-rural es una colección de funciones para delimitar y analizar la ocupación del territorio peruano empleando datos de densidad de viviendas por hectáreas y datos de población actualizados al 2017. Los algoritmos fueron desarrollado en el contexto del artículo "Nuevas herramientas para analizar la ocupación del territorio peruano: hacia un cambio de paradigma en la gestión pública", publicado en la revista indexada Espacio y Desarrollo (39).

El algoritmo ha sido desarrollado en Python (100%) para el uso de cualquier interesado, principalmente para la gestión pública y la investigación. Las bases de datos resultantes de la presente investigación pueden ser descargas de la carpeta 02. Results

## Algoritmos

### Creación del continuo-poblado

```python
import pandas as pd
import geopandas as gpd

from Continuum import create_continuum
from Continuum import open_raster_rio

### Se carga el shp de centros poblados 2017(INEI)
path_d=r"C:\Users\Guillermo\Desktop/Python\01. Continuo urbano-rural"
ccpp=gpd.read_file(path_d+'\\01. Dataset\\inei_centros_poblados_2017_edits.shp')

### Se obtiene la banda y el affine del raster de densidad
path_density=(path_d+"\\01. Dataset\\DensidadViviendas.tif")
band_1, aff_1=open_raster_rio(path_density)

### definimos el valor de densidad y el de población de ser el caso
density_values=[3.9, 0.8, 0.13]
population_values=[50000, 5000]

## Se calcula el conglomerado de alta densidad utilizando la función "create_continuum"
high=create_continuum(density_values[0], band=band_1, affine=aff_1, ccpp_shp=ccpp,
                      pob_minima=population_values[0], no_holes=True)
medium=create_continuum(density_values[1],band=band_1, affine=aff_1,ccpp_shp=ccpp,
                        pob_minima=population_values[1], no_holes=True)
low=create_continuum(density_values[2], band=band_1, affine=aff_1)
```
### Resultados
#### Conglomerados vistos a través de transectos
![alt text](https://github.com/gprietoe/Continuo-urbano-rural/blob/main/03.%20Images/transectos_pais_2.jpg?raw=true "Transectos")
           
### Análisis tipologico

```python
import geopandas as gpd 
from Continuum import spatial_tipology

## Se cargan los conglomerados
high=gpd.read_file('01_Conglomerado_alta_densidad.shp')
medi=gpd.read_file('02_Conglomerado_media_densidad.shp')
low=gpd.read_file('03_Conglomerado_baja_densidad.shp')

## se calcula la tipología para cada densidad 
tipology=spatial_tipology(high, medium, low)
tipology.head(3)

       density  id_n  tipology 
0      low      1     B0     
1      low      2     B0
2      low      3     B0
...

```
### Resultados
#### Conglomerados de Lima Metropolitana, Tacna, Madre de Dios y Chepén-Guadalupe - tipos D4, D3, D1 y B2
![alt text](https://github.com/gprietoe/Continuo-urbano-rural/blob/main/03.%20Images/Casos_tipología_pais_2.jpg?raw=true "Casos_tipología")




## Citado
Por favor, citar de la siguiente manera:
Prieto, Torero, Rondon & Huaire (2022). Nuevas herramientas para analizar la ocupación del territorio peruano: hacia un cambio de paradigma en la gestión pública. Espacio y Desarrollo (39). PUCP. Lima

## License

(EN CONSTRUCCIÓN)




## ENG
# Continium urbano-rural

The following algorithm has been developted in the context of the paper "New tools for the analysis of territorial occupation in Peru: towards a paradigm shift in public administration" which has been published in the indexed journal Espacio y Desarrollo (39). 

The algorithm has been developed 100% in python with the purpose to be used by anyone. Aim: public administration and research.

For citation purpose please use the following:
Prieto, Torero, Rondon & Huaire (2022). Nuevas herramientas para analizar la ocupación del territorio peruano: hacia un cambio de paradigma en la gestión pública. Espacio y Desarrollo (39). PUCP. Lima