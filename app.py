import uuid
from flask import Flask, request, jsonify, send_from_directory, make_response
from flaskext.mysql import MySQL
import database as database, analysis as analysis
import os, datetime

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'SolutionChallenge23'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
db = database.Report(mysql=mysql)

# return proper messages

if __name__ == "-__main__":
    app.run()

@app.route("/login", methods = ["POST"])
def check_login_creds():
    content = request.get_json()
    account_type = content["accountType"]
    account_id = content["userId"]
    password = content["password"]
    password_check = db.check_password(account_type, account_id, password)
    return password_check
    
@app.route("/store-patient-details", methods = ["PUT"])
def store_patient_details():
    content = request.get_json()
    patientId = str(uuid.uuid4())
    patientName = content["patientName"]
    password = content["password"]
    age = content["age"]
    gender = content["gender"]
    db.store_patient_details(patientId, patientName, password, age, gender)
    return patientId

@app.route("/store-hospital-details", methods = ["PUT"])
def store_hospital_details():
    content = request.get_json()
    hospitalId = str(uuid.uuid4())
    hospitalName = content["hospitalName"]
    password = content["password"]
    hospitalAddress = content["hospitalAddress"]
    hospitalContact = content["hospitalContact"]
    db.store_hospital_details(hospitalId, hospitalName, password, hospitalAddress, hospitalContact)
    return hospitalId

@app.route("/add-report", methods = ["PUT"])
def add_report_to_db():
    content = request.get_json()
    patientId = content['patientId']
    date = content['date']
    report = content['report']
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    reportId = str(uuid.uuid4())
    db.store_report(patientId, date, reportId, report)
    return patientId

@app.route("/read-analysis", methods = ["GET"])
def read_analysis():
    patientId = request.args.get('patientId')
    binaryAnalysis, analysisName = db.generate_analysis(patientId= patientId)
    bytes_data = bytes(binaryAnalysis)
    int_list = []
    for byte in bytes_data:
        int_list.append(byte)
    return make_response(int_list, 200)

@app.route("/read-report")
def read_report():
    patientId = request.args.get('patientId')
    patientReports, reportNames = db.read_report(patientId)
    return jsonify(patientReports)


@app.route("/get-patient-details")
def get_patient_details():
    patient_id = request.args.get("patient_id")
    db.read_patient_details(patient_id)

