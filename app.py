import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask import Flask, request, jsonify, send_from_directory
from flaskext.mysql import MySQL
import database, analysis
import os 
import database, analysis
import os 

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'SolutionChallenge23'
app.config['MYSQL_DATABASE_DB'] = 'SolutionChallenge23'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
db = database.Report(mysql=mysql)

# return proper messages
# return proper messages

if __name__ == "-__main__":
    app.run()

@app.route("/")
def first_page():
    try:
        db.store_patient_details(str(uuid.uuid4()), "Proggya", 21, "female", "images/catto.jpg")
        return "works fineeeeeeee"
    except Exception as e:
        print(e)
    
    try:
        db.read_report(1)
        return "wooooo"
    except Exception as e:
        print(e)

@app.route("/login")
def check_login_creds():
    account_type = request.args.get("accountType")
    account_id = request.args.get("userId")
    password = request.args.get("password")
    password_check = db.check_password(account_type, account_id, password)
    return password_check
    # return "Account id and password do not match" 

@app.route("/store-patient-details")
def store_patient_details():
    content = request.get_json()
    patientId = str(uuid.uuid4())
    patientName = content["patientName"]
    password = content["password"]
    age = content["age"]
    gender = content["gender"]
    db.store_patient_details(patientId, patientName, password, age, gender)
    return "STORING PAT DETAILS WORKS COOL"

@app.route("/store-hospital-details")
def store_hospital_details():
    content = request.get_json()
    hospitalId = str(uuid.uuid4())
    hospitalName = content["hospitalName"]
    password = content["password"]
    hospitalAddress = content["hospitalAddress"]
    hospitalContact = content["hospitalContact"]
    db.store_hospital_details(hospitalId, hospitalName, password, hospitalAddress, hospitalContact)
    return "STORING HOSPITAL DETAILS WORKS COOL"

@app.route("/add-report", methods = ["POST"])
def add_report_to_db():
    content = request.get_json()
    patientId = content['patientId']
    date = content['date']
    report = content['report']
    reportId = str(uuid.uuid4())
    db.store_report(reportId, patientId, date, report)
    # reportId = str(uuid.uuid4())
    # patientId = request.args.get("patientId")
    # date = request.args.get("date")
    # bodyByteArray = request.get_data()
    # imgName = "appImage.jpg"
    # with open(imgName, "wb") as f:
    #     f.write(bodyByteArray)
    # db.store_report(reportId, date, patientId, bodyByteArray)
    return "REPORT ADDED SUCCESSFULLY" 

@app.route("/read-analysis")
def read_analysis():
    patientId = request.args.get('patientId')
    binaryAnalysis, analysisName = db.generate_analysis(patientId= patientId)
    # workingdir = os.path.abspath(os.getcwd())
    # filepath = workingdir
    # analysisName = "\\"+ analysisName
    # print(filepath, analysisName)
    # return send_from_directory(filepath, analysisName)
    return binaryAnalysis

# SEEE 
@app.route("/add-report-test")
def add_report():
    content = request.get_json()
    patientId = content['patientId']
    date = content['date']
    report = content['report']
    reportId = str(uuid.uuid4())
    db.store_report(reportId, patientId, date, report)
    
    # patientId = request.args.get("patientId")
    # date = request.args.get("date")
    # # report = request.args.get("report")
    # report = request.files['image']
    print("DEBUGGGGGGGGGGGGGGGGGG ", date, reportId, patientId, report)
    # db.store_report(patient_id, date, report_id, report)
    # db.store_report(patient_id, "2022-04-04", report_id, report)
    return "okoooo"



@app.route("/read-report")
def read_report():
    patientId = request.args.get('patientId')
    patientReports, reportNames = db.read_report(patientId)
    return jsonify(patientReports)


@app.route("/get-patient-details")
def get_patient_details():
    patient_id = request.args.get("patient_id")
    db.read_patient_details(patient_id)

