import pandas as pd
import numpy as np
from geopy.distance import geodesic

def calculate_monthly_distances(data, vessel_col, date_col, lat_col, lon_col):
    """
    Calcula las distancias recorridas mensualmente por cada embarcación.

    Parámetros:
    - data: DataFrame con los datos.
    - vessel_col: Nombre de la columna que contiene los nombres de las embarcaciones.
    - date_col: Nombre de la columna que contiene las fechas.
    - lat_col: Nombre de la columna que contiene las latitudes.
    - lon_col: Nombre de la columna que contiene las longitudes.

    Retorna:
    - DataFrame con las distancias recorridas mensualmente por cada embarcación.

    # _Ejemplo
        new_file_path = r'filtrado_01 - 01 -15 ENE  2023.csv'
        new_data = pd.read_csv(new_file_path)

        # Aplicar la función con los nombres de columnas apropiados
        new_result = calculate_monthly_distances(new_data, 'Nombre', 'Fecha', 'Latitud', 'Longitud')

        # Mostrar el resultado
        print(new_result.head(10))
    """
    # Asegurarse de que las columnas de longitud y latitud sean del tipo float
    data[lon_col] = data[lon_col].astype(float)
    data[lat_col] = data[lat_col].astype(float)

    # Extraer año y mes de la columna de fecha
    data[date_col] = pd.to_datetime(data[date_col], dayfirst=True)
    data['Anio'] = data[date_col].dt.year
    data['Mes'] = data[date_col].dt.month

    # Ordenar los datos por embarcación y fecha
    data = data.sort_values(by=[vessel_col, date_col])

    # Función para calcular la distancia entre dos puntos geográficos
    def haversine_distance(row):
        if pd.isna(row['prev_lat']) or pd.isna(row['prev_lon']):
            return 0
        else:
            return geodesic((row['prev_lat'], row['prev_lon']), (row[lat_col], row[lon_col])).kilometers

    # Calcular las distancias
    data['prev_lat'] = data.groupby(vessel_col)[lat_col].shift(1)
    data['prev_lon'] = data.groupby(vessel_col)[lon_col].shift(1)
    data['distance_km'] = data.apply(haversine_distance, axis=1)

    # Sumar las distancias por mes y embarcación
    data['YearMonth'] = data['Anio'].astype(str) + '-' + data['Mes'].astype(str).str.zfill(2)
    monthly_distances = data.groupby([vessel_col, 'YearMonth'])['distance_km'].sum().reset_index()

    return monthly_distances