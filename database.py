from flaskext.mysql import MySQL
import analysis as analysis 
import analysis as analysis 
import pickle 
from password_utils import hash_password, check_password
import base64
from transformation_utils import compress_data, decompress_data

class Report:
    def __init__(self, mysql) -> None:
        self.mysql = mysql
        conn = self.mysql.connect()
        cursor = conn.cursor()

        # Creating reports database
        try:
            # report_id has to be unique not patient id in this table.
            # there can be multiple entries of the same patient id 
            query = '''CREATE TABLE if not exists `Reports` ( 
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
            query = '''CREATE TABLE if not exists `PATIENT_DETAILS` (
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
            query = '''CREATE TABLE if not exists `HOSPITAL_DETAILS` (
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

    def login(self, accountType, accountId, password):
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            queryPatient = '''SELECT password FROM PATIENT_DETAILS WHERE patientId = %s'''
            queryHospital = '''SELECT password FROM HOSPITAL_DETAILS WHERE hospitalId = %s'''
            
            if accountType == 'H':
                cursor.execute(queryHospital, (accountId,))
            else:
                cursor.execute(queryPatient, (accountId,))
            
            accountPassword = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            print("PASSWORD", password)
            if check_password(password, accountPassword):
                return 1
            return 0
        except Exception as e:
            print(e)
            return 0
    
    def store_patient_details(self, patientId, patientName, password, age, gender):

        try:
            password = hash_password(password)
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = '''INSERT INTO PATIENT_DETAILS VALUES(%s, %s, %s, %s, %s)'''
            cursor.execute(query, (patientId, patientName, password, age, gender))
            conn.commit()
            cursor.close()
            conn.close()
            return 1
        except Exception as e:
            print(e)
            return 0

    def store_hospital_details(self, hospitalId, hospitalName, password, hospitalAddress, hospitalConact):
            
            try:
                password = hash_password(password)
                conn = self.mysql.connect()
                cursor = conn.cursor()
                query = '''INSERT INTO HOSPITAL_DETAILS VALUES(%s, %s, %s, %s, %s)'''
                cursor.execute(query, (hospitalId, hospitalName, password, hospitalAddress, hospitalConact))
                conn.commit()
                cursor.close()
                conn.close()
                return 200
            except Exception as e:
                print(e)
                return 403

    def read_patient_details(self, patient_id):

        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = '''SELECT patientId, reportId, report, hospitalId, date from Reports where patientId = %s'''
            cursor.execute(query, (patient_id, ))
            record = cursor.fetchall()
            for row in record:
                patientId, reportId, report, hospitalId, date = row
                self.convert_to_image(report, 'test.jpg')
                return patientId, reportId, hospitalId, date
        except Exception as e:
            print(e)    
            return None  

    def store_report(self, patientId, reportId, hospitalId, report, date):
       
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            # report = base64.b64decode(report)
            # report = compress_data(report)
            query = '''INSERT INTO Reports(patientId, reportId, hospitalId, report, date) VALUES(%s, %s, %s, %s, %s)'''
            cursor.execute(query, (patientId, reportId, hospitalId, report, date))
            conn.commit()
            cursor.close()
            conn.close()
            
            return 1
        
        except Exception as e:
            print(e)
            return 0

    def read_report(self, patientId):

        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            #while generating analysis we don't need hospital names just the report and date
            query = '''SELECT reportId, date, report from Reports where patientId = %s'''
            cursor.execute(query, (patientId, ))
            records = cursor.fetchall()
            
            reports = {}
            for row in records:
                reportId, date, report = row
                reportName = "reports/report_"+patientId+"_"+reportId+".jpg"
                report = self.convert_to_image(report, reportName)
                reports[str(date)] = reportName
            return reports
        
        except Exception as e:
            print(e)
            return 0

    def analyse_two_reports(self, patientId, paths, dates):
        anal = analysis.Analysis(patientId= patientId)
        reportName = anal.plot_analysis(patientId, paths, dates)
        binaryReport = self.convert_to_binary_data(reportName)
        return binaryReport, reportName
        
    def generate_analysis(self, patientId):
        
        # see how to link >2 reports if time permits
        try:
 
            paths, dates = self.read_report(patientId)
            binaryReport, reportName = self.analyse_two_reports(patientId, paths, dates)
            return binaryReport, reportName
        
        except Exception as e:
            print(e)