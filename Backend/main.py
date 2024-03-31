import math

import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import csv
from sklearn.cluster import KMeans, DBSCAN
import numpy as np
from flask import Flask, request, jsonify

zipcode = 0

app = Flask(__name__)
@app.route('/process', methods=['POST'])
def process():
    data = request.json
    zipcode = data['zipcode']
    range_km = data['range']
    # Process the data as needed
    print(zipcode, range_km)  # Example of processing
    return jsonify({'status': 'success', 'zipcode': zipcode, 'range': range_km})

DAYS_IN_A_YEAR = 365
PERCENTAGE_VISITS_YEAR = 0.101

def get_zip_coordinates(zip, dfZips, dfHospitals, miles):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    row = dfZips[dfZips['zip'] == zip]
    lat = float(row['lat'].values[0])
    lng = float(row['lng'].values[0])
    min_lat, max_lat, min_lng, max_lng = calculate_mile_bounds(lat, lng, miles)
    filteredZips = dfZips[(dfZips['lat'] >= min_lat) & (dfZips['lat'] <= max_lat) &
                     (dfZips['lng'] >= min_lng) & (dfZips['lng'] <= max_lng)]
    filteredHospitals = dfHospitals[(dfHospitals['LATITUDE'] >= min_lat) & (dfHospitals['LATITUDE'] <= max_lat) &
                          (dfHospitals['LONGITUDE'] >= min_lng) & (dfHospitals['LONGITUDE'] <= max_lng)]
    return filteredZips, filteredHospitals, min_lat, max_lat, min_lng, max_lng

def calculate_mile_bounds(latitude, longitude, miles):
    # Constants
    miles_per_degree = 69

    # Calculate the latitude change for 5 miles
    delta_lat = 14 / miles_per_degree

    # Calculate the longitude change for 5 miles, adjusting for latitude
    latitude_rad = math.radians(latitude)
    delta_lng = 14 / (math.cos(latitude_rad) * miles_per_degree)

    # Calculate the bounding box
    min_lat = latitude - delta_lat
    max_lat = latitude + delta_lat
    min_lng = longitude - delta_lng
    max_lng = longitude + delta_lng

    return (min_lat, max_lat, min_lng, max_lng)

def optimize(cities, hospitals, potential_locations):
    def euclidean_distance(point1, point2):
        return np.sqrt(np.sum((point1 - point2) ** 2))

    # Set up your Gurobi model
    model = gp.Model()

    # Decision variables for each potential hospital location
    # Assuming we treat each city's location as a potential new hospital location
    x = model.addVars(len(potential_locations), vtype=GRB.BINARY, name="hospital")

    distance_to_cities = gp.quicksum(x[i] * np.min([np.linalg.norm(city[:2] - potential_locations[i])
                                                    * city[2] * PERCENTAGE_VISITS_YEAR / DAYS_IN_A_YEAR for city in cities])
                                     for i in range(len(potential_locations)))
    distance_from_hospitals = gp.quicksum(
        x[i] * np.min([np.linalg.norm(hospital[:2] - potential_locations[i]) * hospital[2] for hospital in hospitals])
        for i in range(len(potential_locations)))

    model.setObjective(distance_to_cities - distance_from_hospitals, GRB.MINIMIZE)

    # Constraint: Only one new hospital can be built
    model.addConstr(x.sum() == 1, "OneHospital")

    # Optimize the model
    model.optimize()

    if model.status == GRB.OPTIMAL:
        for i in model.getVars():
            if i.X > 0.5:  # If the decision variable for this location is selected
                optimal_index = int(i.VarName.split('[')[1].split(']')[0])
                optimal_location = potential_locations[optimal_index]
                print(
                    f"Optimal location for the new hospital is at coordinates: {optimal_location[0]}, {optimal_location[1]}")
    else:
        print("No optimal solution found.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #run flask app
    app.run(debug=True)
    #load the appropriate dataframes within a 5 mile radius
    dfZips = pd.read_csv("zips.csv")
    dfHospitals = pd.read_csv("hospital_locations.csv")
    dfZips, dfHospitals, min_lat, max_lat, min_lng, max_lng = (
        get_zip_coordinates(zipcode, dfZips, dfHospitals, 5))

    # create needed info for optimization
    cities = dfZips[['lat', 'lng', 'population']].to_numpy()
    hospitals = dfHospitals[['LATITUDE', 'LONGITUDE', 'BEDS']].to_numpy()
    lat_values = np.round(np.arange(min_lat, max_lat, 0.01), 2)
    lng_values = np.round(np.arange(min_lng, max_lng, 0.01), 2)
    potential_locations = np.array(np.meshgrid(lat_values, lng_values)).T.reshape(-1, 2)

    optimize(cities, hospitals ,potential_locations)
