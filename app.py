import uuid
from flask import Flask, request, jsonify, send_from_directory, make_response
from flaskext.mysql import MySQL
import database, analysis
import os, datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
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
    account_contact = content["account_contact"]
    password = content["password"]
    login_check = db.login(account_type, account_contact, password)
    if login_check:
        access_token = create_access_token(identity= account_contact, additional_claims={'Account Type': account_type})
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
    patient_contact = content["patient_contact"]
    
    status = db.store_patient_details(patient_id, patient_name, password, age, gender, patient_contact)
    if status:
        access_token = create_access_token(identity= patient_contact, additional_claims={'Account Type': constants.PATIENT})
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
        access_token = create_access_token(identity= hospital_contact, additional_claims={'Account Type': constants.HOSPITAL})
        return jsonify(access_token), constants.RSP_SUCCESS
    return jsonify({'message': 'Invalid credentials'}), constants.RSP_CLIENT_ERROR_INVALID_CREDS 
    
#report is immutable once uploaded
@app.route("/add-report", methods = ["POST"])
@jwt_required()
def add_report_to_db():
    
    try:
        current_user = get_jwt_identity()
        user_account_type = get_jwt()['Account Type']
        
        if user_account_type != constants.HOSPITAL:
            return jsonify({'message': 'Could not insert report'}), constants.RSP_CLIENT_ERROR_INVALID_CREDS
            
        #extract hospitalcontact from jwt token 
        hospital_contact = current_user
        patient_contact = request.form['patient_contact']
        date = request.form['date']
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        
        for report in request.files:
            reportId = str(uuid.uuid4())
            # Authorizing only hospitals to store reports in databse
            report_img = request.files[report]
            report_img = report_img.read()
            status = db.store_report(patient_contact, reportId, hospital_contact, report_img, date)
            if not status:
                return jsonify({'message': 'Could not insert report'}), constants.RSP_SERVER_ERROR
            
        return jsonify({'message': 'Successfully inserted report'}), constants.RSP_SUCCESS
    except Exception as e:
        return constants.RSP_CLIENT_ERROR
    
@app.route("/read-analysis", methods = ["GET"])
@jwt_required()
def read_analysis():
    current_user = get_jwt_identity()

    #only patient can see their analysis
    patient_contact = request.args.get('patient_contact')
    if patient_contact != current_user:
        return jsonify({'message': 'Analysis could not be accessed'}), constants.RSP_CLIENT_ERROR_INVALID_CREDS
    analysis_name, status = db.generate_analysis(patient_contact)
    #don't send actual image name, host it somewhere and send the hosted link
    if status:
        return make_response(jsonify({'analysis address': analysis_name}), constants.RSP_SUCCESS)
    return jsonify({'message': 'Analysis could not be generated'}), constants.RSP_SERVER_ERROR

@app.route("/read-report", methods=["GET"])
@jwt_required()
def read_report():
    current_user = get_jwt_identity()
    user_account_type = get_jwt()['Account Type']

    content = request.get_json()
    patient_contact = content['patient_contact']
    reports, status = None, None
    #only a hospital connected to patient and the patient themself can access their medical records
    if (user_account_type == constants.PATIENT and current_user == patient_contact):
        reports, status = db.read_report(patient_contact)
        
    elif user_account_type == constants.HOSPITAL:
        reports, status = db.read_report(patient_contact, current_user, user_account_type)
    if status:
        return jsonify(reports), constants.RSP_SUCCESS
    return jsonify({'message': 'Details could not be found'}), constants.RSP_CLIENT_ERROR

@app.route("/get-patient-details", methods=["GET"])
@jwt_required()
def get_patient_details():
    current_user = get_jwt_identity()
    user_account_type = get_jwt()['Account Type']
    patient_contact = request.args.get("patient_contact")
    
    if user_account_type == constants.PATIENT and current_user != patient_contact:
        return jsonify({'message': 'Invalid creds to check patient details'}), constants.RSP_CLIENT_ERROR_INVALID_CREDS

    details = db.read_patient_details(patient_contact, user_account_type, current_user)
    if details:
        return jsonify(details), constants.RSP_SUCCESS
    return jsonify({'message': 'Details could not be found'}), constants.RSP_CLIENT_ERROR
