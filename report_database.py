from flaskext.mysql import MySQL

class Report:
    def __init__(self, mysql) -> None:
        self.mysql = mysql
        conn = self.mysql.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('''CREATE TABLE if not exists `Patient_Report` ( `patientId` INT NOT NULL PRIMARY KEY , `date` DATE NOT NULL , `report` BLOB NOT NULL)''')
            # print("DOES THIS WORK????????")
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

    def store_report(self, patientId, date, report):
       
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            report_binary = self.convert_to_binary_data(report)
            cursor.execute('''INSERT INTO Patient_Report VALUES(%s, %s, %s)''', (patientId, date, report_binary))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)

    def read_report(self, patientId):

        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = '''SELECT * from Patient_Report where patientId = %s'''
            cursor.execute(query, (patientId, ))
            record = cursor.fetchall()
            for row in record:
                report_binary = row[2]
                self.convert_to_image(report_binary, "images/cat.jpg")
        except Exception as e:
            print(e)