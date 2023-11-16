# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dtify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
def home():
    """Homepage"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    station_data = session.query(Station.station, Station.name).all()

    station_list = [{"station": station, "name": name} for station, name in station_data]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(Measurement.station, func.count(Measurement.station).label('count')) \
                  .group_by(Measurement.station) \
                  .order_by(func.count(Measurement.station).desc()) \
                  .first()

    most_active_station_id = most_active_station.station

    temperature_data = session.query(Measurement.date, Measurement.tobs) \
                      .filter(Measurement.station == most_active_station_id) \
                      .filter(Measurement.date >= one_year_ago) \
                      .all()

    temperature_list = [{"date": date, "temperature": temp} for date, temp in temperature_data]

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    temperature_data = session.query(func.min(Measurement.tobs).label('TMIN'),
                                           func.avg(Measurement.tobs).label('TAVG'),
                                           func.max(Measurement.tobs).label('TMAX')) \
                                    .filter(Measurement.date >= start) \
                                    .all()

    temperature_list_start = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperature_data]

    return jsonify(temperature_list_start)

if __name__ == "__main__":
    app.run(debug=True)