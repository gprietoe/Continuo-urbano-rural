## ESP
# Continuum urbano-rural

Continuum urbano-rural es una colección de modulos para delimitar y analizar la ocupación del territorio peruano empleando datos de densidad de viviendas por hectáreas y datos de población actualizados al 2017. Los algoritmos fueron desarrollado en el contexto del artículo "Nuevas herramientas para analizar la ocupación del territorio peruano: hacia un cambio de paradigma en la gestión pública", publicado en la revista indexada Espacio y Desarrollo (38).

El algoritmo ha sido desarrollado en Python (100%) para el uso de cualquier interesado, principalmente para la gestión pública y la investigación. Las bases de datos resultantes de la presente investigación pueden ser descargas de la carpeta 02. Results


## ENG
# Continuum urbano-rural

The Continuum urbano-ruran is a collection of modules developted to delineate and analize the Peruvian territory using building density data and population data from the last national census. The following algorithms have been developted in the context of the paper "New tools for the analysis of territorial occupation in Peru: towards a paradigm shift in public administration" which has been published in the indexed journal Espacio y Desarrollo (38). 

The algorithm has been developed 100% in python with the purpose to be used by anyone. Aim: public administration and research.

## Algoritmos

### Creación del conglomerado

```python
import geopandas as gpd
import continuum

### Se carga el shp de centros poblados 2017(INEI) en EPSG:32718
ccpp=gpd.read_file('inei_centros_poblados_2017_edits.shp')

### Se guarda la banda y el affine del raster de densidad
path_density=('DensidadViviendas.tif') ## Raster de densidad de viv/ha.
band_1, aff_1=continuum.open_raster_rio(path_density) ## Función simplificada de rasterio.open()

### definimos el valor de densidad y el de población de corresponder 
density_values=[3.9, 0.8, 0.13]
population_values=[50000, 5000]

## Se calculan los conglomerados
high=continuum.create_continuum(density_values[0], band=band_1, affine=aff_1, ccpp_shp=ccpp,
                      pob_minima=population_values[0], no_holes=True)
medium=continuum.create_continuum(density_values[1],band=band_1, affine=aff_1,ccpp_shp=ccpp,
                        pob_minima=population_values[1], no_holes=True)
low=continuum.create_continuum(density_values[2], band=band_1, affine=aff_1)
```
### Resultados

#### Conglomerados vistos a través de transectos
![alt text](https://github.com/gprietoe/Continuo-urbano-rural/blob/main/03.%20Images/transectos_pais_2.jpg?raw=true "Transectos")
           
### Análisis tipologico

```python
import geopandas as gpd 
import continuum

## Se cargan los conglomerados
high=gpd.read_file('01_Conglomerado_alta_densidad.shp')
medi=gpd.read_file('02_Conglomerado_media_densidad.shp')
low=gpd.read_file('03_Conglomerado_baja_densidad.shp')

## se calcula la tipología para cada densidad 
tipology=continuum.spatial_tipology(high, medium, low)
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


## Creación de clusters usando fuentes de datos abiertos
La libreria *continuum* puede ser facilmente utilizada para identificar conglomerados de grillas de población. Para ello, el modulo incluye la función denominada *add_pop_sum*, la cual permite calcular el total de población del cluster de acuerdo con el método denominado como Grado de Urbanización (European Commission; ILO; FAO; OECD; UN-Habitat; World Bank)

A continuación, se presentan los casos de las ciudades fronterizas de Zarumilla (Perú), Aguas Verdes (Perú) y Huaquillas (Ecuador). Para ello, se utilizó la información de densidad de población con una grilla aproximada de 1km x 1km, de la plataforma de LandScan: https://landscan.ornl.gov/ 

El ejemplo completo, se puede encontrar en Notebooks/Open_data_example

```python
import continuum

pop_density=("north_border_clip.tif")
band_1, aff_1=continuum.open_raster_rio(pop_density)

## Valores de densidad de acuerdo con:
density_values=[1500, 300, 30]
population_values=[50000, 5000,0]

## Se calcula cada una de las densidades, aplicando adicionalmente la función *add_pop_sum* para calcular la suma de la población
high=(continuum.create_continuum(density_values[0], band=band_1, affine=aff_1, no_holes=True,crs_EPSG=4326, pixel_con=8).
      pipe(continuum.add_pop_sum,pop_density,population_values[0]))
medium=(continuum.create_continuum(density_values[1],band=band_1, affine=aff_1, no_holes=True,crs_EPSG=4326, pixel_con=8).
       pipe(continuum.add_pop_sum,pop_density,population_values[1]))
low=(continuum.create_continuum(density_values[2], band=band_1, affine=aff_1, crs_EPSG=4326).
    pipe(continuum.add_pop_sum,pop_density,population_values[2]))

```
### Resultados
#### Conglomerados de Tumbes, Zarumilla, Aguas Verdes y Huaquillas
![alt text](https://github.com/gprietoe/Continuo-urbano-rural/blob/main/03.%20Images/Cities_b.jpg?raw=true "Ciudades fronterizas")

## Citado 

For citation purpose please use the following:
Prieto, Torero, Rondon & Huaire (2021). Nuevas herramientas para analizar la ocupación del territorio peruano: hacia un cambio de paradigma en la gestión pública. Espacio y Desarrollo (38). PUCP. Lima

