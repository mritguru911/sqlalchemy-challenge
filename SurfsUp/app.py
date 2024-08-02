# Import the dependencies.
import sqlalchemy
import numpy as np
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, table
from sqlalchemy import Date
from datetime import datetime, timedelta


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

### 1. '/' *Start homepage and List all the available routes.
@app.route("/")
def welcome():

    """ List all available routes"""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/Precipitation in the last 12 months - <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"/api/v1.0/Weather Stations - <a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"The Temperature Observations - Most Active Station - Prior Year - <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )

################################################################

### 2. Convert the query results from your precipitation analysis

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve only the last 12 months of data and return JSON results."""
    # Create our session (link) from Python to the DB. 
    session = Session(engine)
    
    # Calculate the date one year ago from the most recent date
    recent_date = datetime(2017, 8, 23)
    previous_year = recent_date - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= previous_year).\
        filter(Measurement.date <= recent_date).all()

    # Close the session
    session.close()

#Convert the query results to a dictionary analysis; using date as the key and prcp as the value.
    all_precipitation = []
    for date, prcp in precipitation:
        precipitation = {}
        precipitation["date"] = date
        precipitation["prcp"] = prcp
        all_precipitation.append(precipitation)

    # Return the JSON representation of the dictionary    
    return jsonify(all_precipitation)

### 3. Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # Query the active stations
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Close the session
    session.close()
    
    #Convert the query results to a dictionary using station as the key and count as the value.
    all_stations = []
    for station, count in active_stations:
        active_stations = {}
        active_stations["station"] = station
        active_stations["count"] = count
        all_stations.append(active_stations)
    
    # Return JSON
    return jsonify(all_stations)

##########################################################

### 4. Query the dates and temperature observations of the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def tobs():

    """Return a JSON list of temperature observations for the previous year"""

    # Create our session (link) from Python to the DB.
    session = Session(engine)


    # Query the most-active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()[0]
    
    # Calculate the date one year ago from the most recent date
    recent_date = datetime(2017, 8, 23)
    previous_year = recent_date - timedelta(days=365)
    
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    dates_temps = session.query(Measurement.date, Measurement.tobs).\
        filter(
            Measurement.date >= previous_year, 
            Measurement.date <= recent_date, 
            Measurement.station == most_active_station
            ).all()

    # Close the session
    session.close()

    #Convert the query results to a dictionary using date as the key and tobs as the value.
    all_values = []
    for date, tobs in dates_temps:
        date_tobs = {}
        date_tobs["date"] = date
        date_tobs["tobs"] = tobs
        all_values.append(date_tobs)
    
    # Return JSON
    return jsonify(all_values)


#[5] Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # Query TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    start_date_query = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).first()
    
    # Close the session
    session.close()

    # Convert the query results to a dictionary
    tmin, tavg, tmax = start_date_query
    start_date_value = {
        "min": tmin,
        "average": tavg,
        "max": tmax,
    }
    # Return JSON
    return jsonify(start_date_value)

# @app.route("/api/v1.0/<start>/<end>")
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # Query TMIN, TAVG, and TMAX for dates between start and end date
    start_end_date_query = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start, Measurement.date <= end).first()
    
    # Close the session
    session.close()

    # Convert the query results to a dictionary
    tmin, tavg, tmax = start_end_date_query
    start_end_date_value = {
        "min_temp": tmin,
        "avg_temp": tavg,
        "max_temp": tmax,
    }

    return jsonify(start_end_date_value)

if __name__ == '__main__':
    app.run(debug=True)
    











































