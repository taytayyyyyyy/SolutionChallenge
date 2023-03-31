import read_image
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

    def connect_points(self, point1, point2, color):
        x_values = [point1[0], point2[0]]
        y_values = [point1[1], point2[1]]
        plt.plot(x_values, y_values, color , linestyle= 'solid')

    def draw_graph(self, points_dict):
        fig, ax = plt.subplots()
        # print(points_dict)
        for element in points_dict:
            # print(element)
            p1, p2, color = points_dict[element]
            # print(p1, p2, color)
            plt.plot(p1[0], p1[1], marker="o", markersize=5, markerfacecolor= color)
            plt.plot(p2[0], p2[1], marker="o", markersize=5, markerfacecolor= color)
            plt.annotate(' ' + element + " " + str(p1[1]), p1, fontsize = 8)
            plt.annotate(' ' + element + " " + str(p2[1]), p2, fontsize = 8)
            self.connect_points(p1, p2, color)
        
    def find_date(self,date_given):
        date_modified = datetime.datetime.strptime(date_given, '%m-%d-%Y').date()
        return date_modified

    def generate_random_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        rand_color = (r, g, b)
        return '#%02x%02x%02x' % rand_color

    def plot_analysis(self, patientId, path1, path2):
        # path1 = "images\\test8.png"
        # path2 = "images\\test9.png"
        
        test_values1 = self.find_result(path1)
        test_values2 = self.find_result(path2)
        
        date1 = self.find_date("01-01-2005")
        date2 = self.find_date("04-01-2005")
        
        points_dict = {}

        for key in test_values1:
            if key in test_values2:
                # print(key, test_values1[key], test_values2[key])
                point1 = [date1, int(test_values1[key])]
                point2 = [date2, int(test_values2[key])]
                color = self.generate_random_color()
                # print(color)
                points_dict[key] = (point1, point2, color)
                
        self.draw_graph(points_dict)
        fileName = "reports\\report_"+patientId+".jpg"
        plt.savefig("reports\\report_"+patientId+".jpg")
        # plt.show()
        return fileName
        
    # test_diff()