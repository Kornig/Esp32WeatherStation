from flask import Flask, request, jsonify
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, cast, Numeric
from sqlalchemy.types import String 
from dataclasses import dataclass
import datetime
import api_utilities

app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://root:jcRkTUiRWKKLdKjVauQs9ojVi8IyeEk6@dpg-curo3udds78s73b4momg-a/storage_xlju"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://root:jcRkTUiRWKKLdKjVauQs9ojVi8IyeEk6@dpg-curo3udds78s73b4momg-a.oregon-postgres.render.com/storage_xlju"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def get_measurements_daily(unix_time_beginning, unix_time_end):
    daily_avgs = db.session.query(
        #sqlite
        #func.date(func.datetime(MeasurementModel.UNIXtime, 'unixepoch')).label('Date'),
        #postgre
        cast(func.date(func.to_timestamp(MeasurementModel.UNIXtime)), String).label("Date"),

        #sqlite
        # func.round(func.avg(MeasurementModel.Humidity),2).label("Humidity"),
        # func.round(func.avg(MeasurementModel.Pressure),2).label("Pressure"),
        # func.round(func.avg(MeasurementModel.Temperature),2).label("Temperature")
        #postgrhe
        func.round(cast(func.avg(MeasurementModel.Humidity), Numeric), 2).label("Humidity"),
        func.round(cast(func.avg(MeasurementModel.Pressure), Numeric), 2).label("Pressure"),
        func.round(cast(func.avg(MeasurementModel.Temperature), Numeric), 2).label("Temperature")
    ).filter(
        MeasurementModel.UNIXtime >= unix_time_beginning, MeasurementModel.UNIXtime < unix_time_end
    ).group_by(
        #sqlite
        #func.date(func.datetime(MeasurementModel.UNIXtime, 'unixepoch'))
        #postgre
        func.date(func.to_timestamp(MeasurementModel.UNIXtime))
    ).order_by(
        #sqlite
        #func.date(func.datetime(MeasurementModel.UNIXtime, 'unixepoch'))
        #postgre
        func.date(func.to_timestamp(MeasurementModel.UNIXtime))
    ).all()

    dict_result = []

    for row in daily_avgs:
        dict_result.append({
            "Date": row.Date,
            "Humidity": row.Humidity,
            "Pressure": row.Pressure,
            "Temperature": row.Temperature
        })

    return jsonify(dict_result )


@dataclass
class MeasurementModel(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    UNIXtime:int = db.Column(db.BigInteger, unique=True, nullable=False)
    Humidity:float = db.Column(db.Float, nullable=False)
    Pressure:float = db.Column(db.Float, nullable=False)
    Temperature:float = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Measurement(UNIXtime = {self.UNIXtime}, Humidity = {self.Humidity}, Pressure = {self.Pressure}, Temperature = {self.Temperature})"




#Zapisywanie pomiaru w bazie
@app.route("/api/measurement", methods=["POST"])
def measurement():
    if not request.is_json:
        return jsonify({"error":"Content type must be application/json"}), 400

    data = request.json

    required_fields = ["UNIXtime","Humidity","Pressure","Temperature"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}!"}), 400

    measurement = MeasurementModel(
        UNIXtime = data["UNIXtime"], 
        Humidity = data["Humidity"], 
        Pressure = data["Pressure"], 
        Temperature = data["Temperature"]
        )
    
    try:
        db.session.add(measurement)
        db.session.commit()
        return jsonify({ 
            "message": "Measurement accepted!",
            "measurement": measurement
            }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

#Pobieranie pomiaru o zadanym id
@app.route("/api/measurement/<int:m_id>", methods=["GET"])
def get_measurement(m_id):
    measurement = MeasurementModel.query.filter_by(id=m_id).first()
    if not measurement:
        return jsonify({"error": "Measurement not found!"}), 400

    return jsonify(measurement), 200

#Pobieranie pomiarów z danego dnia, każdy pomiar zrobiony danego dnia
@app.route("/api/measurements/day/<date>", methods=["GET"])
def get_measurements_day(date):
    dt_obj = datetime.datetime.strptime(date, r"%Y-%m-%d")

    #czas z podanego dnia, z godziny 00:00:00
    unix_time = int(dt_obj.timestamp())
    print(unix_time)
    #czas z następnego dnia, z godziny 00:00:00
    unix_time_next_day = unix_time + 86400

    measurements = MeasurementModel.query.filter(MeasurementModel.UNIXtime >= unix_time, MeasurementModel.UNIXtime < unix_time_next_day).all()

    return jsonify(measurements), 200

#Pobieranie pomiarów z danego tygodnia, średnie z każdego dnia tygodnia
@app.route("/api/measurements/week/<int:year>/<int:week>", methods=["GET"])
def get_measurements_week(year, week):
    unix_time = api_utilities.week_to_timestamp(year, week)
    unit_time_next_week = unix_time + 604800

    return get_measurements_daily(unix_time, unit_time_next_week), 200


#Pobieranie pomiarów z danego miesiąca, średnie z każdego dnia miesiąca
@app.route("/api/measurements/month/<int:year>/<int:month>", methods=["GET"])
def get_measurements_month(year, month):
    date = datetime.datetime(year, month, 1)
    date_next_month = date + relativedelta(months=1)

    return get_measurements_daily(int(date.timestamp()), int(date_next_month.timestamp())), 200

@app.route("/")
def root():
    return "<h1>Welcome to the Weather Station</h1>"


if __name__ == "__main__":
    app.run()