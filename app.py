import uuid
from flask import Flask, request, jsonify, send_from_directory, make_response
from flaskext.mysql import MySQL
import database as database, analysis as analysis
import os, datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from constants import HOSPITAL, PATIENT

# import find_breed 
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

#Customer decorator for role-based access
# def roles_required(required_role):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             # Get the current user's identity from the JWT
#             current_user = get_jwt_identity()

#             # Check if the required role is present in the JWT
#             if 'role' in current_user and current_user['role'] == required_role:
#                 return func(*args, **kwargs)
#             else:
#                 return jsonify({'message': 'Unauthorized: Insufficient role'}), 403

#         return wrapper

#     return decorator

if __name__ == "-__main__":
    app.run()

@app.route("/login", methods = ["POST"])
def check_login_creds():
    content = request.get_json()
    account_type = content["accountType"]
    account_id = content["userId"]
    password = content["password"]
    login_check = db.login(account_type, account_id, password)
    if login_check:
        access_token = create_access_token(identity= account_id, additional_claims={'Account Type': account_type})
        return jsonify(access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 403 
    
@app.route("/store-patient-details", methods = ["PUT"])
def store_patient_details():
    content = request.get_json()
    patientId = str(uuid.uuid4())
    patientName = content["patientName"]
    password = content["password"]
    age = content["age"]
    gender = content["gender"]

    status = db.store_patient_details(patientId, patientName, password, age, gender)
    if status:
        access_token = create_access_token(identity= patientId, additional_claims={'Account Type': PATIENT})
        return jsonify(access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 403 
    
@app.route("/store-hospital-details", methods = ["PUT"])
def store_hospital_details():
    content = request.get_json()
    hospitalId = str(uuid.uuid4())
    hospitalName = content["hospitalName"]
    password = content["password"]
    hospitalAddress = content["hospitalAddress"]
    hospitalContact = content["hospitalContact"]
    
    status = db.store_hospital_details(hospitalId, hospitalName, password, hospitalAddress, hospitalContact)
    if status:
        access_token = create_access_token(identity= hospitalId, additional_claims={'Account Type': HOSPITAL})
        return jsonify(access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 403 
    
@app.route("/add-report", methods = ["PUT"])
@jwt_required()
def add_report_to_db():
    current_user = get_jwt_identity()
    user_account_type = get_jwt()['Account Type']

    content = request.get_json()
    #extract hospitalId from jwt token 
    hospitalId = current_user
    patientId = content['patientId']
    date = content['date']
    report = content['report']
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    reportId = str(uuid.uuid4())
    
    # Authorizing only hospitals to store reports in databse
    if user_account_type == HOSPITAL:
        status = db.store_report(patientId, reportId, hospitalId, report, date)
        if status:
            return jsonify({'message': 'Successfully inserted report'}), 200
        else:
            return jsonify({'message': 'Could not insert report'}), 500
    return jsonify({'message': 'Invalid credentials to upload report'}), 403

@app.route("/read-analysis", methods = ["GET"])
@jwt_required()
def read_analysis():
    current_user = get_jwt_identity()

    patientId = request.args.get('patientId')
    binaryAnalysis, analysisName = db.generate_analysis(patientId= patientId)
    bytes_data = bytes(binaryAnalysis)
    int_list = []
    for byte in bytes_data:
        int_list.append(byte)
    return make_response(int_list, 200)

@app.route("/read-report")
@jwt_required()
def read_report():
    current_user = get_jwt_identity()
    user_account_type = get_jwt()['Account Type']

    content = request.get_json()
    patientId = content['patientId']
    #only a hospital connected to patient and the patient themself can access their medical records
    if (user_account_type == PATIENT and current_user == patientId):
        reports = db.read_report(patientId)
    elif user_account_type == HOSPITAL:
        reports = db.read_report(patientId, current_user, user_account_type)
    
    return jsonify(reports), 200

@app.route("/get-patient-details")
def get_patient_details():
    patient_id = request.args.get("patient_id")
    details = db.read_patient_details(patient_id)
    if details:
        return jsonify(details), 200
    return jsonify({'message': 'Details could not be found'}), 403
