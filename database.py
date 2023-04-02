from flaskext.mysql import MySQL
import analysis as analysis 
import analysis as analysis 

# reports database should have a reportid too
class Report:
    def __init__(self, mysql) -> None:
        self.mysql = mysql
        conn = self.mysql.connect()
        cursor = conn.cursor()

        # Creating reports database
        try:
            # report_id has to be unique not patient id in this table.
            # there can be multiple entries of the same table 
            query = '''CREATE TABLE if not exists `Patient_Report` ( 
             `patientId` VARCHAR(100) NOT NULL , 
             `date` DATE NOT NULL , 
             `reportId` VARCHAR(100) PRIMARY KEY, 
             `report` BLOB NOT NULL)'''
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
            # profilePicture_binary = self.convert_to_binary_data(profilePicture)
            # profilePicture_binary = self.convert_to_binary_data(profilePicture)
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
            # report_binary = self.convert_to_binary_data(report)
            query = '''INSERT INTO Patient_Report VALUES(%s, %s, %s, %s)'''
            cursor.execute(query, (patientId, date, reportId, report))
            conn.commit()
            cursor.close()
            conn.close()
            return 200
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
            reportsRecord = []
            reportNames = []
            for row in record:
                reports = {}
                pid, reports["date"], reports["reportId"], reports["report"] = row
                reportId = row[-2]
                reportBinary = row[-1]
                reportName = "reports/report_"+patientId+"_"+reportId+".jpg"
                self.convert_to_image(reportBinary, reportName)
                reports["report"] = reportName
                reportsRecord.append(reports)

                # storing the report names for that patient 
                reportNames.append(reportName)
                print("this report read correctly")

            patientReports = {"patient_id" : patientId, "reports": reportsRecord}
            return patientReports, reportNames
        
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
    
    def placeholder():
    # def check_username(self, username):
    #    try:
    #         conn = self.mysql.connect()
    #         cursor = conn.cursor()
    #         query = '''SELECT * from Patient_Report where patientId = %s'''
    #         cursor.execute(query, (patientId, ))
    #         record = cursor.fetchall()
    #         reports_record = []
    #         for row in record:
    #             reports = {}
    #             pid, reports["date"], reports["report_id"], reports["report"] = row
    #             report_id = row[-2]
    #             report_binary = row[-1]
    #             self.convert_to_image(report_binary, "images/report_"+patientId+"_"+report_id+".jpg")
    #             reports["report"] = "images/report_"+patientId+"_"+report_id+".jpg"
    #             reports_record.append(reports)
    #             print("this report read correctly")
    #         # patient_reports = {"patient_id" : patientId }
    #         patient_reports = {"patient_id" : patientId, "reports": reports_record}
    #         return patient_reports
    #     except Exception as e:
    #         print(e) 
        print("useless placeholder")

    def analyse_two_reports(self, patientId, path1, path2):
        anal = analysis.Analysis(patientId= patientId)
        reportName = anal.plot_analysis(patientId, path1, path2)
        binaryReport = self.convert_to_binary_data(reportName)
        return binaryReport, reportName
        

    def generate_analysis(self, patientId):
        
        # patientReports, reportNames = self.read_report(patientId)

        # see how to link >2 reports if time permits
        # for name in reportNames:
        # path1, path2 = reportNames[0], reportNames[1]
        path1 = "images\\test9.png"
        path2 = "images\\test10.png"
        
        binaryReport, reportName = self.analyse_two_reports(patientId, path1, path2)

        # path1 = "images\\test8.png"
        # path2 = "images\\test9.png"
        # Find the acutal path to the reports bruh bruh bruh too much work
        return binaryReport, reportName