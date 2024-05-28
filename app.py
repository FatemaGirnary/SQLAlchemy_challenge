# Import the dependencies.
#%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
# Declare a Base using `automap_base()`
base = automap_base()

# Use the Base class to reflect the database tables
base.prepare(engine, reflect = True)

# Assign the measurement class to a variable called `Measurement` and
# assign the station class to a variable called `Station`
measurement = base.classes.measurement
station = base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return(
        f" Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")

@app.route("/api/v1.0/precipitation")
def precipitation():
   # Find the most recent date in the data set.
    recent_date = session.query(func.max(measurement.date)).first()[0]

    #Starting from the most recent data point in the database.
    recent_date_dt = dt.datetime.strptime(recent_date, "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    one_year_ago = recent_date_dt - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()

    #Conver the query results to a dictionary
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def station():
    #Perform a query to retrieve the stations
    stations_data = session.query(station.station).all()
    stations_list = [station[0] for station in stations_data]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    
     # Find the most recent date in the data set.
    recent_date = session.query(func.max(measurement.date)).first()[0]

    #Starting from the most recent data point in the database.
    recent_date_dt = dt.datetime.strptime(recent_date, "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    one_year_ago = recent_date_dt - dt.timedelta(days=365)

    #Calculate the most active stations
    active_stations = session.query(measurement.station, func.count(measurement.id)).\
                    group_by(measurement.station).order_by(func.count(measurement.id).desc()).all()

    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    tobs_data = session.query(measurement.date, measurement.tobs).\
            filter(measurement.station == most_active_station).\
            filter(measurement.date >= one_year_ago).all()

    #Convert the query results to a list of dictionaries
    tobs_list = [{date: tobs} for date, tobs in tobs_data]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    sel = [func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)]

    #if no date is provided, quesry the data for all dates
    if not end:
        results = session.quesry(*sel).filter(measurement.date >= start).all()
    else:
        results = session.quesry(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()

    #conver the query results to a list
    temp_stats = list(results[0])
    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
