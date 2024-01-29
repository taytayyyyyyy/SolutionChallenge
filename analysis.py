import read_image as read_image
import matplotlib.pyplot as plt
import numpy as np
import datetime
import random
import matplotlib.colors as col


class Analysis:
    def __init__(self, patientId):
        self.patientId = patientId

    def find_result(self, path : str):
        return read_image.find_values(path)
        
    def find_date(self,date_given):
        date_modified = datetime.datetime.strptime(date_given, '%m-%d-%Y').date()
        return date_modified

    def generate_random_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        rand_color = (r, g, b)
        return '#%02x%02x%02x' % rand_color

    def plot_analysis(self, patientId, paths, dates):
        
        report_values_list = []
        #store them in a list of arrays and connect the dots
        for path in paths:
            report_values = self.find_result(path)
            report_values_list.append(report_values)
        
        points_dict = {}

        for i, point_list in enumerate(report_values_list):
            for key in point_list:
                if key in points_dict:
                    points_dict[key].append([dates[i], int(point_list[key])])
                else:
                    points_dict[key] = [[dates[i], int(point_list[key])]]
        
        plt.figure(figsize=(8, 8))
        
        for key, points in points_dict.items():
            color = self.generate_random_color()

            # Sort points by date
            points.sort(key=lambda x: x[0])

            x_values = [point[0] for point in points]
            y_values = [point[1] for point in points]

            plt.scatter(x_values, y_values, color=color)
            plt.plot(x_values, y_values, color=color, label=f'ALUPACHA')
        
            for point in points:
                plt.annotate(f'{key}{point[1]}', (point[0], point[1]), textcoords="offset points", xytext=(0,5), ha='center')

        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title('Scatter Plot of Points')
             
        fileName = "reports\\report_"+patientId+".jpg"
        plt.savefig("reports\\report_"+patientId+".jpg")
        return fileName