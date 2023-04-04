from flaskext.mysql import MySQL
import analysis as analysis 
import analysis as analysis 
import pickle 

# reports database should have a reportid too
class Report:
    def __init__(self, mysql) -> None:
        self.mysql = mysql
        conn = self.mysql.connect()
        cursor = conn.cursor()

        # Creating reports database
        try:
            # report_id has to be unique not patient id in this table.
            # there can be multiple entries of the same patient id 
            query = '''CREATE TABLE if not exists `Patient_Report` ( 
             `patientId` VARCHAR(100) NOT NULL , 
             `date` DATE NOT NULL , 
             `reportId` VARCHAR(100) PRIMARY KEY, 
             `report` MEDIUMBLOB NOT NULL)'''
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

        # Creating hospital reports database
        try:
            query = '''CREATE TABLE if not exists `HOSPITAL_REPORTS` (
                `patientId` VARCHAR(100),
                `hospitalId` VARCHAR(100), 
                `reportId` VARCHAR(100),
                `gender` VARCHAR(10) NOT NULL)'''
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

        # Creating hospital reports database
        try:
            query = '''CREATE TABLE if not exists `HOSPITAL_REPORTS` (
                `patientId` VARCHAR(100),
                `hospitalId` VARCHAR(100), 
                `reportId` VARCHAR(100))'''
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
            file.write(data)

    def store_patient_details(self, patientId, patientName, password, age, gender):

        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = '''INSERT INTO PATIENT_DETAILS VALUES(%s, %s, %s, %s, %s)'''
            cursor.execute(query, (patientId, patientName, password, age, gender))
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
            query = '''SELECT * from Patient_Report where patientId = %s'''
            cursor.execute(query, (patient_id, ))
            record = cursor.fetchall()
            for row in record:
                patient_id, patient_name, age, gender, profile_pic_binary = row
                self.convert_to_image(profile_pic_binary, "images/profile_pic_"+patient_id+".jpg")
                # row[-1] = profile_pic_binary
                return row
        except Exception as e:
            print(e)    
            return 403   

    def store_report(self, patientId, date, reportId, report):
       
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            report = pickle.dumps(report)
            query = '''INSERT INTO Patient_Report VALUES(%s, %s, %s, %s)'''
            cursor.execute(query, (patientId, date, reportId, report))
            conn.commit()
            cursor.close()
            conn.close()
            query = '''SELECT * FROM Patient_Report WHERE patientId = %s AND date = %s AND reportId = %s'''
            print(reportId)
            cursor.execute(query, (patientId, date, reportId,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result is not None:
                print("Result", result)
                return 200  # Report added successfully
            else:
                return 403  # Report not added
            
        except Exception as e:
            print(e)
            return 403

    def read_report(self, patientId):

        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = '''SELECT * from Patient_Report where patientId = %s'''
            cursor.execute(query, (patientId, ))
            record = cursor.fetchall()
            # reportsRecord = []
            reportNames = []
            reportDates = []
            for row in record:
                reports = {}
                pid, reports["date"], reports["reportId"], reports["report"] = row
                reportId = row[-2]
                reportBinary = row[-1]
                reportName = "reports/report_"+patientId+"_"+reportId+".jpg"
                self.convert_to_image(reportBinary, reportName)
                reports["report"] = [reportName, reports["date"]]
                reportNames.append(reportName)
                reportDates.append(reports["date"])

            return reportNames, reportDates

        except Exception as e:
            print(e)
            return 403

    def store_hospital_details(self, hospitalId, hospitalName, password, hospitalAddress, hospitalConact):
        
        try:
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

    def check_password(self, accountType, accountId, password):
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            queryPatient = '''SELECT password FROM PATIENT_DETAILS WHERE patientId = %s'''
            queryHospital = '''SELECT password FROM HOSPITAL_DETAILS WHERE hospitalId = %s'''
            
            if accountType == 'H':
                cursor.execute(queryHospital, (accountId,))
            else:
                cursor.execute(queryPatient, (accountId,))
            # print(cursor.fetchall())
            
            accountPassword = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            if password == accountPassword:
                return "CORRECT PASSWORD"
            return "WRONG PASSWORD"

        except Exception as e:
            print(e)
            return 403
    
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