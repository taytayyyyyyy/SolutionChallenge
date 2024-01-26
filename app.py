import uuid
from flask import Flask, request, jsonify, send_from_directory, make_response
from flaskext.mysql import MySQL
import database as database, analysis as analysis
import os, datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from constants import HOSPITAL, PATIENT
import constants

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = str(uuid.uuid4())
jwt = JWTManager(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'SolutionChallenge23'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
db = database.Report(mysql=mysql)

if __name__ == "-__main__":
    app.run()

@app.route("/login", methods = ["POST"])
def check_login_creds():
    content = request.get_json()
    account_type = content["account_type"]
    account_id = content["user_id"]
    password = content["password"]
    login_check = db.login(account_type, account_id, password)
    if login_check:
        access_token = create_access_token(identity= account_id, additional_claims={'Account Type': account_type})
        return jsonify(access_token), constants.RSP_SUCCESS
    return jsonify({'message': 'Invalid credentials'}), constants.RSP_CLIENT_ERROR_INVALID_CREDS
    
@app.route("/store-patient-details", methods = ["PUT"])
def store_patient_details():
    content = request.get_json()
    patient_id = str(uuid.uuid4())
    patient_name = content["patient_name"]
    password = content["password"]
    age = content["age"]
    gender = content["gender"]

    status = db.store_patient_details(patient_id, patient_name, password, age, gender)
    if status:
        access_token = create_access_token(identity= patient_id, additional_claims={'Account Type': PATIENT})
        return jsonify(access_token), constants.RSP_SUCCESS
    return jsonify({'message': 'Invalid credentials'}), constants.RSP_CLIENT_ERROR_INVALID_CREDS 
    
@app.route("/store-hospital-details", methods = ["PUT"])
def store_hospital_details():
    content = request.get_json()
    hospital_id = str(uuid.uuid4())
    hospital_name = content["hospital_name"]
    password = content["password"]
    hospital_address = content["hospital_address"]
    hospital_contact = content["hospital_contact"]
    
    status = db.store_hospital_details(hospital_id, hospital_name, password, hospital_address, hospital_contact)
    if status:
        access_token = create_access_token(identity= hospital_id, additional_claims={'Account Type': HOSPITAL})
        return jsonify(access_token), constants.RSP_SUCCESS
    return jsonify({'message': 'Invalid credentials'}), constants.RSP_CLIENT_ERROR_INVALID_CREDS 
    
#report is immutable
@app.route("/add-report", methods = ["POST"])
@jwt_required()
def add_report_to_db():
    current_user = get_jwt_identity()
    user_account_type = get_jwt()['Account Type']

    content = request.get_json()
    #extract hospitalId from jwt token 
    hospital_id = current_user
    patient_id = content['patient_id']
    date = content['date']
    report = content['report']
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    reportId = str(uuid.uuid4())
    
    # Authorizing only hospitals to store reports in databse
    if user_account_type == HOSPITAL:
        status = db.store_report(patient_id, reportId, hospital_id, report, date)
        if status:
            return jsonify({'message': 'Successfully inserted report'}), constants.RSP_SUCCESS
        else:
            return jsonify({'message': 'Could not insert report'}), constants.RSP_SERVER_ERROR
    return jsonify({'message': 'Invalid credentials to upload report'}), constants.RSP_CLIENT_ERROR_INVALID_CREDS

@app.route("/read-analysis", methods = ["GET"])
@jwt_required()
def read_analysis():
    current_user = get_jwt_identity()

    patient_id = request.args.get('patientId')
    binary_analysis, analysis_name, status = db.generate_analysis(patient_id)
    if status:
        bytes_data = bytes(binary_analysis)
        int_list = []
        for byte in bytes_data:
            int_list.append(byte)
        return make_response(int_list, constants.RSP_SUCCESS)
    return jsonify({'message': 'Analysis could not be generated'}), constants.RSP_SERVER_ERROR

@app.route("/read-report")
@jwt_required()
def read_report():
    current_user = get_jwt_identity()
    user_account_type = get_jwt()['Account Type']

    content = request.get_json()
    patient_id = content['patient_id']
    #only a hospital connected to patient and the patient themself can access their medical records
    if (user_account_type == PATIENT and current_user == patient_id):
        reports = db.read_report(patient_id)
    elif user_account_type == HOSPITAL:
        reports = db.read_report(patient_id, current_user, user_account_type)
    
    return jsonify(reports), constants.RSP_SUCCESS

@app.route("/get-patient-details")
def get_patient_details():
    patient_id = request.args.get("patient_id")
    details = db.read_patient_details(patient_id)
    if details:
        return jsonify(details), constants.RSP_SUCCESS
    return jsonify({'message': 'Details could not be found'}), constants.RSP_CLIENT_ERROR
