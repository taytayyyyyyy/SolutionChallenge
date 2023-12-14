from flaskext.mysql import MySQL
import analysis as analysis 
import analysis as analysis 
import pickle 
from password_utils import hash_password, check_password
import base64
from transformation_utils import compress_data, decompress_data
from constants import HOSPITAL, PATIENT

#should we close the cursor after every operation?

class Report:
    def __init__(self, mysql) -> None:
        self.mysql = mysql
        conn = self.mysql.connect()
        cursor = conn.cursor()

        # Creating reports database
        try:
            # report_id has to be unique not patient id in this table.
            # there can be multiple entries of the same patient id 
            query = '''CREATE TABLE IF NOT EXISTS `REPORTS` ( 
             `reportId` VARCHAR(100) NOT NULL,
             `date` DATE NOT NULL , 
             `report` MEDIUMBLOB NOT NULL,
             `patientId` VARCHAR(100) NOT NULL,
             `hospitalId` VARCHAR(100) NOT NULL,
             FOREIGN KEY(`patientId`) REFERENCES `Patient_Details`(`patientId`),
             FOREIGN KEY(`hospitalId`) REFERENCES `Hospital_Details`(`hospitalId`)
             )'''
            cursor.execute(query)
        except Exception as e: 
            print(e)

        # Creating patient details database
        try:
            query = '''CREATE TABLE IF NOT EXISTS `PATIENT_DETAILS` (
                `patientId` VARCHAR(100) PRIMARY KEY, 
                `patientName` VARCHAR(50), 
                `password` VARCHAR(100),
                `gender` VARCHAR(100),
                `age` VARCHAR(3) NOT NULL)'''
            cursor.execute(query)
        except Exception as e:
            print(e)

        # Creating hospital details database
        try: 
            query = '''CREATE TABLE IF NOT EXISTS `HOSPITAL_DETAILS` (
                `hospitalId` VARCHAR(100) PRIMARY KEY,
                `hospitalName` VARCHAR(50), 
                `password` VARCHAR(100),
                `hospitalAddress` VARCHAR(100),
                `hospitalContact` VARCHAR(10)
                )'''
            cursor.execute(query)
        except Exception as e:
            print(e)

        cursor.close()
        conn.close()

    def convert_to_binary_data(self, filename):
        with open(filename, 'rb') as file:
            binary_data = file.read()
        return binary_data

    def convert_to_image(self, data, filename):
        with open(filename, 'wb') as file:
            file.write(base64.b64decode(data))

    def login(self, accountType, account_id, password):
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            queryPatient = '''SELECT password FROM PATIENT_DETAILS WHERE patientId = %s'''
            query_hospital = '''SELECT password FROM HOSPITAL_DETAILS WHERE hospitalId = %s'''
            if accountType == HOSPITAL:
                cursor.execute(query_hospital, (account_id,))
            else:
                cursor.execute(queryPatient, (account_id,))
            
            account_password = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            print("PASSWORD", password)
            if check_password(password, account_password):
                return 1
            return 0
        except Exception as e:
            print(e)
            return 0
    
    def store_patient_details(self, patient_id, patient_name, password, age, gender):

        try:
            password = hash_password(password)
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = '''INSERT INTO PATIENT_DETAILS VALUES(%s, %s, %s, %s, %s)'''
            cursor.execute(query, (patient_id, patient_name, password, age, gender))
            conn.commit()
            cursor.close()
            conn.close()
            return 1
        except Exception as e:
            print(e)
            return 0

    def store_hospital_details(self, hospital_id, hospital_name, password, hospital_address, hospital_contact):
            
            try:
                password = hash_password(password)
                conn = self.mysql.connect()
                cursor = conn.cursor()
                query = '''INSERT INTO HOSPITAL_DETAILS VALUES(%s, %s, %s, %s, %s)'''
                cursor.execute(query, (hospital_id, hospital_name, password, hospital_address, hospital_contact))
                conn.commit()
                cursor.close()
                conn.close()
                print("entered here")
                return 200
            except Exception as e:
                print(e)
                return 403

    def read_patient_details(self, patient_id):

        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = '''SELECT patientId, reportId, report, hospitalId, date from REPORTS where patient_id = %s'''
            cursor.execute(query, (patient_id, ))
            record = cursor.fetchall()
            for row in record:
                patient_id, report_id, report, hospital_id, date = row
                self.convert_to_image(report, 'test.jpg')
                return patient_id, report_id, hospital_id, date
        except Exception as e:
            print(e)    
            return None  

    def store_report(self, patient_id, report_id, hospital_id, report, date):
       
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            # report = base64.b64decode(report)
            # report = compress_data(report)
            query = '''INSERT INTO REPORTS(patientId, reportId, hospitalId, report, date) VALUES(%s, %s, %s, %s, %s)'''
            cursor.execute(query, (patient_id, report_id, hospital_id, report, date))
            conn.commit()
            cursor.close()
            conn.close()
            
            return 1
        
        except Exception as e:
            print(e)
            return 0

    def read_report(self, patient_id, current_user, user_account_type = PATIENT):

        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            #while generating analysis we don't need hospital names just the report and date
            query = '''SELECT reportId, date, report from REPORTS where patient_id = %s'''
            
            #If there are no entries for that hospital and patient, they aren't connected
            if user_account_type == HOSPITAL:
                cursor.execute('''SELECT COUNT(*) FROM REPORTS WHERE patientId = %s and hospitalId = %s''', (patient_id, current_user))
                if not cursor.fetchall():
                    return 0

            cursor.execute(query, (patient_id, ))
            records = cursor.fetchall()

            reports = {}
            for row in records:
                report_id, date, report = row
                report_name = "reports/report_"+patient_id+"_"+report_id+".jpg"
                report = self.convert_to_image(report, report_name)
                reports[str(date)] = report_name
            return reports
        
        except Exception as e:
            print(e)
            return 0

    def analyse_two_reports(self, patient_id, paths, dates):
        anal = analysis.Analysis(patient_id= patient_id)
        report_name = anal.plot_analysis(patient_id, paths, dates)
        binary_report = self.convert_to_binary_data(report_name)
        return binary_report, report_name
        
    def generate_analysis(self, patient_id):
        
        # see how to link >2 reports if time permits
        try:
 
            paths, dates = self.read_report(patient_id)
            binary_report, report_name = self.analyse_two_reports(patient_id, paths, dates)
            return binary_report, report_name
        
        except Exception as e:
            print(e)