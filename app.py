import uuid
from flask import Flask, request, jsonify
from flaskext.mysql import MySQL
import database
# import report_database

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'test'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
db = database.Report(mysql=mysql)


if __name__ == "-__main__":
    app.run()

@app.route("/")
def first_page():
    try:
        # db.store_report(str(uuid.uuid4()), "2022-10-10", "images/catto.jpg")
        db.store_patient_details(str(uuid.uuid4()), "Proggya", 21, "female", "images/catto.jpg")
        return "works fineeeeeeee"
    except Exception as e:
        print(e)
    
    try:
        db.read_report(1)
        return "wooooo"
    except Exception as e:
        print(e)
        
@app.route("/store-report")
def store_report():
    patient_id = request.args.get("patient_id")
    date = request.args.get("date")
    report_id = str(uuid.uuid4())
    report = request.args.get("report")
    db.store_report(patient_id, date, report_id, report)
    # db.store_report(patient_id, "2022-04-04", report_id, report)
    return "okoooo"

@app.route("/read-report")
def read_report():
    patient_id = "9b1f0708-89c0-4257-9a49-3418e4a26bab"
    # patient_id = request.args.get("patient_id")
    patient_reports = db.read_report(patientId= patient_id)
    return jsonify(patient_reports)

@app.route("/store-patient-details")
def store_patient_details():
    patient_id = str(uuid.uuid4())
    patient_name = request.args.get("patient_name")
    age = request.args.get("age")
    gender = request.args.get("gender")
    profile_picture = "images/default_profile_picture.png"
    try:
        profile_picture = request.args.get("profile_picture")
    except Exception as e:
        print(e)
    db.store_patient_details(patient_id, patient_name, age, gender, profile_picture)
    # db.store_patient_details(str(uuid.uuid4()), "Proggya", 21, "female", profile_picture)
    return "well well well"

@app.route("/get-patient-details")
def get_patient_details():
    patient_id = request.args.get("patient_id")
    db.read_patient_details(patient_id)