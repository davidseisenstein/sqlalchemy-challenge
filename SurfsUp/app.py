# Import dependencies

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# create the sqlalchemy engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Start the Flask setup 
app = Flask(__name__)

# Begin defining the flask routes
@app.route("/")
def home():
    "List all available API routes."
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Start Date formatted as YYYY-MM-DD <br/>"
        f"/api/v1.0/Start Date/End Date formatted as YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    "Precipitation API"
    # create a session
    session = Session(engine)
    # query our data and save it in results
    results = session.query(Measurement.date, Measurement.station, func.sum(Measurement.prcp)).group_by(Measurement.date, Measurement.station).all()
    # close the session
    session.close()

    # Create a dictionary from the row data, and append to a list of all dates
    all_precip = []
    for date, station, precip in results:
        date_dict = {}
        date_dict["date"] = date
        date_dict["station"] = station
        date_dict["precipitation"] = precip
        all_precip.append(date_dict)
    # jsonify and return the data
    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    "Return JSON formatted list of all the stations"
    # create a session
    session = Session(engine)
    # query our data and save it in results
    results = session.query(Station.station, Station.name).all()
    # close the session
    session.close()

    # Create a dictionary and append to a list
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)
    # jsonfiy and return
    return jsonify(all_stations)
    

@app.route("/api/v1.0/tobs")
def tobs():
    "Query dates and temperature observations of the most active station"
    # create a session
    session = Session(engine)
    # query our data and save it in results
    # define the most active station for the filter
    stationid = 'USC00519281'
    
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == stationid).all()
    # close the session
    session.close()

    # Create a dictionary and append to a list
    all_temps = []
    for date, temp in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature"] = temp
        all_temps.append(temp_dict)
    # add a layer to our return showing the station id
    final_temps = [{"stationid": stationid}, all_temps]
    return jsonify(final_temps)

@app.route("/api/v1.0/<start>")
def start(start):
    "Return a JSON list of min temp, avg temp and max temp for a given date range"
    # create a session
    session = Session(engine)
    # query our data and save it in results
    # define the most active station for the filter
    stationid = 'USC00519281'
    
    result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station == stationid, Measurement.date >= start).all()
    # close the session
    session.close()

    #convert list of tuples into a normal list
    temps = list(np.ravel(result))
    summary_temps = [stationid, start]
    summary_temps.append(temps)
    return jsonify(summary_temps)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    "Return a JSON list of min temp, avg temp and max temp for a given date range"

    "Return a JSON list of min temp, avg temp and max temp for a given date range"
    # create a session
    session = Session(engine)
    # query our data and save it in results
    # define the most active station for the filter
    stationid = 'USC00519281'
    
    result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station == stationid, Measurement.date >= start, Measurement.date <= end).all()
    # close the session
    session.close()

    #convert list of tuples into a normal list
    temps = list(np.ravel(result))
    summary_temps = [stationid, start, end]
    temps += summary_temps
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)