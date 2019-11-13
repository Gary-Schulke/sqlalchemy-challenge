# sqlalchemy-challenge
# Gary Schulke

# imports
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create the engine for a sqlite database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Use automap to get the table names.
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# A Flask server is used for development.

app = Flask(__name__)


# Utility functions
# Calculates the yyyy,mm,dd from today.
# number_of_days - The differental in days.  Can be positive or negative
def calculate_date(from_date, number_of_days):
    try:
        dt_from = dt.datetime.strptime(from_date, '%Y-%m-%d')
        new_date = dt_from + dt.timedelta(days=number_of_days)
        new_date = new_date.strftime('%Y-%m-%d')
    except ValueError as err:
        print("Date value out of range.")
    return new_date

# Set up server routes.
# The base route.
# Returns the routes that are implememeted.
@app.route("/")
def welcome():
    #List all available api routes.
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"        
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd <br/>"        
    )
# returns a json formatted dictionary of precipitation values for all dates.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precips_dict = {}
    precips_list = []

    for date, precip in results:
        precips_dict = {}
        precips_dict[date] = precip
        precips_list.append(precips_dict)
    return jsonify(precips_list)

# returns a json formatted  list of stations.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

# returns a json formatted list of dates and tobs.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    precip_query = session.query(Measurement.date, Measurement.prcp).\
                            order_by(Measurement.date.desc())

    # The last date in the data
    end_date = precip_query.first()[0]
    # calculate one year back
    start_date =  calculate_date(end_date, -365)
    print(f'Start date: {start_date}, End date: {end_date}')

    precip_query = precip_query.filter(Measurement.date <= end_date, 
                                        Measurement.date >= start_date).\
                                order_by (Measurement.date)
    precip = precip_query.all()
    session.close()

    return jsonify(precip)

# returns json formatte3d list of min, avg, and max tobs between dates.
@app.route("/api/v1.0/<start>/<end>")
def temp_from_range(start, end):
    start_date = start
    end_date = end

    # Create our session (link) from Python to the DB
    session = Session(engine)
    range_query = session.query(func.min(Measurement.tobs), 
                                func.avg(Measurement.tobs), 
                                func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start_date).\
                                filter(Measurement.date <= end_date)
    temp_by_date = range_query.all()
    session.close()
    
    temp_by_date = list(np.ravel(temp_by_date))
    return jsonify(temp_by_date)

# returns json formatted list of tobs between start date and the last date in the db.
@app.route("/api/v1.0/<start>")
def temps_from_start(start):
    start_date = start
    end_date = '9999-01-01'

    # Create our session (link) from Python to the DB
    session = Session(engine)
    range_query = session.query(func.min(Measurement.tobs), 
                                func.avg(Measurement.tobs), 
                                func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start_date).\
                                filter(Measurement.date <= end_date)
    temp_by_date = range_query.all()
    session.close()
    temp_by_date = list(np.ravel(temp_by_date))
    return jsonify(temp_by_date)

# Start the server.
if __name__ == '__main__':
    app.run(debug=True, port=5000)


