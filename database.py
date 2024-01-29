import analysis 
from password_utils import hash_password, check_password
import constants
from typing import Optional
import base64

class Report:
    def __init__(self, mysql) -> None:
        self.mysql = mysql
        conn = self.mysql.connect()
        cursor = conn.cursor()

        # Creating patient details database
        try:
            query = '''CREATE TABLE IF NOT EXISTS `PATIENT_DETAILS` (
                `patientId` VARCHAR(100), 
                `patientName` VARCHAR(50), 
                `password` VARCHAR(100),
                `gender` VARCHAR(100),
                `age` VARCHAR(3) NOT NULL,
                `patientContact` VARCHAR(10) PRIMARY KEY
                )'''
            cursor.execute(query)
        except Exception as e:
            print(e)

        # Creating hospital details database
        try: 
            query = '''CREATE TABLE IF NOT EXISTS `HOSPITAL_DETAILS` (
                `hospitalId` VARCHAR(100),
                `hospitalName` VARCHAR(50), 
                `password` VARCHAR(100),
                `hospitalAddress` VARCHAR(100),
                `hospitalContact` VARCHAR(10) PRIMARY KEY
                )'''
            cursor.execute(query)
        except Exception as e:
            print(e)
            
        # Creating reports database
        try:
            # report_id has to be unique not patient id in this table.
            # there can be multiple entries of the same patient id 
            query = '''CREATE TABLE IF NOT EXISTS `REPORTS` ( 
             `reportId` VARCHAR(100) NOT NULL,
             `date` DATE NOT NULL , 
             `report` MEDIUMBLOB NOT NULL,
             `patientContact` VARCHAR(100) NOT NULL,
             `hospitalContact` VARCHAR(100) NOT NULL,
             FOREIGN KEY(`patientContact`) REFERENCES `PATIENT_DETAILS`(`patientContact`),
             FOREIGN KEY(`hospitalContact`) REFERENCES `HOSPITAL_DETAILS`(`hospitalContact`)
             )'''
            cursor.execute(query)
        except Exception as e: 
            print(e)

        
        cursor.close()
        conn.close()

    def image_to_binary(self, file_path):
        with open(file_path, "rb") as image_file:
            binary_data = base64.b64encode(image_file.read())
            return binary_data
        
    def convert_to_image(self, data, filename):
        with open(filename, 'wb') as file:
            file.write(data)

    def login(self, accountType, account_contact, password):
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            queryPatient = '''SELECT password FROM PATIENT_DETAILS WHERE patientContact = %s'''
            query_hospital = '''SELECT password FROM HOSPITAL_DETAILS WHERE hospitalContact = %s'''
            if accountType == constants.HOSPITAL:
                cursor.execute(query_hospital, (account_contact,))
            else:
                cursor.execute(queryPatient, (account_contact,))
            
            account_password = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            if check_password(password, account_password):
                return constants.DB_OPS_SUCCESS
            return constants.DB_OPS_ERROR
        except Exception as e:
            print(e)
            return constants.DB_OPS_ERROR
    
    def store_patient_details(self, patient_id, patient_name, password, age, gender, patient_contact):

        try:
            password = hash_password(password)
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = '''INSERT INTO PATIENT_DETAILS(patientId, patientName, password, age, gender, patientContact) VALUES(%s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (patient_id, patient_name, password, age, gender, patient_contact))
            conn.commit()
            cursor.close()
            conn.close()
            return constants.DB_OPS_SUCCESS
        except Exception as e:
            print(e)
            return constants.DB_OPS_ERROR

    def store_hospital_details(self, hospital_id, hospital_name, password, hospital_address, hospital_contact):
            
            try:
                password = hash_password(password)
                conn = self.mysql.connect()
                cursor = conn.cursor()
                query = '''INSERT INTO HOSPITAL_DETAILS(hospitalId, hospitalName, password, hospitalAddress, hospitalContact) VALUES(%s, %s, %s, %s, %s)'''
                cursor.execute(query, (hospital_id, hospital_name, password, hospital_address, hospital_contact))
                conn.commit()
                cursor.close()
                conn.close()
                print("entered here")
                return constants.DB_OPS_SUCCESS
            except Exception as e:
                print(e)
                return constants.DB_OPS_ERROR

    def read_patient_details(self, patient_contact, user_account_type, current_user):
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            
            #If hospital and patient aren't connected then hospital can't read patient's reports(unless shared)
            if user_account_type == constants.HOSPITAL:
                cursor.execute('''SELECT COUNT(*) FROM REPORTS WHERE patientContact = %s and hospitalContact = %s''', (patient_contact, current_user))
                if not cursor.fetchall():
                    return constants.DB_OPS_ERROR

            query = '''SELECT patientName, gender, age from PATIENT_DETAILS where patientContact = %s'''
            cursor.execute(query, (patient_contact, ))
            record = cursor.fetchall()
            for row in record:
                patient_name, gender, age = row
                return [patient_contact, patient_name, gender, age], constants.DB_OPS_SUCCESS 
        except Exception as e:
            print(e)    
            return None, constants.DB_OPS_ERROR

    def store_report(self, patient_contact, report_id, hospital_contact, report, date):
       
        try:
            print("ENTERS HERE")
            conn = self.mysql.connect()
            cursor = conn.cursor()
            #better design choice is to host the report in the server and store the location in the table
            query = '''INSERT INTO REPORTS(patientContact, reportId, hospitalContact, report, date) VALUES(%s, %s, %s, %s, %s)'''
            cursor.execute(query, (patient_contact, report_id, hospital_contact, report, date))
            print('[DEBUG]', patient_contact, report_id, hospital_contact, report, date)
            conn.commit()
            cursor.close()
            conn.close()
            
            return constants.DB_OPS_SUCCESS
        
        except Exception as e:
            print(e)
            return constants.DB_OPS_ERROR

    def read_report(self, patient_contact, current_user: Optional[int] = None, user_account_type = constants.PATIENT):

        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            #while generating analysis we don't need hospital names just the report and date
            query = '''SELECT reportId, date, report from REPORTS where patientContact = %s'''
            
            #If hospital and patient aren't connected then hospital can't read patient's reports(unless shared)
            if user_account_type == constants.HOSPITAL:
                cursor.execute('''SELECT COUNT(*) FROM REPORTS WHERE patientContact = %s and hospitalContact = %s''', (patient_contact, current_user))
                if not cursor.fetchall():
                    return constants.DB_OPS_ERROR

            cursor.execute(query, (patient_contact, ))
            records = cursor.fetchall()

            reports = {}
            for idx, row in enumerate(records):
                report_id, date, report = row
                report_name = "reports/report_"+patient_contact+"_"+report_id+".jpg"
                report = self.convert_to_image(report, report_name) #report will be hosted in server
                reports[(str(date), str(idx))] = report_name
            return reports, constants.DB_OPS_SUCCESS
        
        except Exception as e:
            print(e)
            return None, constants.DB_OPS_ERROR

    def analyse_reports(self, patient_contact, paths, dates):
        report_analysis = analysis.Analysis(patient_contact)
        report_name = report_analysis.plot_analysis(patient_contact, paths, dates)
        return report_name
        
    def generate_analysis(self, patient_contact):
        
        try:
            reports, dates = self.read_report(patient_contact)
            paths = []
            dates = []
            for date in reports:
                dates.append(date[0])
                paths.append(reports[date])
            report_name = self.analyse_reports(patient_contact, paths, dates)
            return report_name, constants.DB_OPS_SUCCESS
        
        except Exception as e:
            print(e)
            return None, constants.DB_OPS_ERROR