import casadi as ca
from casadi import *
from coordinatesTrans import coTrans
import time
from Vehicle import *
from PIL import Image, ImageDraw
from case import Case
class ZLYAnswer:
    def __init__(self,index,mul = 0.1,whtether_use_success_file=False,alg_name="OCBA",more_ocba=False):
        # 打开图片
        self.index = index
        self.whtether_use_success_file = whtether_use_success_file
        self.mul = mul
        self.vehicleNode3D = [] # for quba
        self.final_path = Path([], [], [])
        self.vehicle_2d_path = []
        self.vehicle_2d_ha_path = []
        if alg_name=="OCBA" and more_ocba == False:
            self.alg_name = "EHHA"
        else:
            self.alg_name = alg_name
        self.more_ocba = more_ocba

       

    def process_type_1(self, words, i):
        vehicle_x, vehicle_y = float(words[i+1]) * self.mul, float(words[i+2]) * self.mul
        yaw = float(words[i+3])
        self.vehicleNode3D.append(OBCAPath(vehicle_x, vehicle_y, yaw))
        self.final_path.x.append(vehicle_x)
        self.final_path.y.append(vehicle_y)
        self.final_path.yaw.append(yaw)
        x,y = vehicle_x, vehicle_y
        yaw = 0
        self.vehicle_2d_ha_path.append(OBCAPath(x,y,yaw))
        return i + 4 

    def process_type_2(self,words, i):
        # vehicle_x, vehicle_y =float(words[i+1]) * self.mul, float(words[i+2]) * self.mul
        # quaternion = [float(words[j]) for j in range(i+4, i+8)]
        # roll, pitch, yaw = quaternion_to_euler(*quaternion)
        # vehicleNode3D.append([vehicle_x, vehicle_y, yaw])
        return i + 7

    def process_type_3(self, words, i,case:Case):
        points = []
        i+=1
        for _ in range(4):
            point_x, point_y =float(words[i]) * self.mul, float(words[i+1]) * self.mul
            points.append((point_x, point_y))
            case.xmax = max(case.xmax, point_x+1)
            case.xmin = min(case.xmin, point_x-1)
            case.ymax = max(case.ymax, point_y+1)
            case.ymin = min(case.ymin, point_y-1)
            i += 2
        # draw.line(points + [points[0]], fill='blue', width=4)
        return i
    def process_type_0(self,words, i):
        x,y = float(words[i+1]) * self.mul, float(words[i+2]) * self.mul
        yaw = 0
        self.vehicle_2d_path.append(OBCAPath(x,y,yaw))
        return i + 3 # 要记得算自己
    def readTXT(self,case):
        if self.whtether_use_success_file:
            with open(f'./ZLYoutput/{self.alg_name}/TPCAP_{self.index}_resultViz_0_success.txt', 'r') as file:
                content = file.read()
        elif (self.alg_name == "OCBA" or self.alg_name == "MPC_OCBA") and self.more_ocba:
            with open(f'./Result/{self.alg_name}/case-{self.index}/TPCAP_{self.index}_resultViz_0.txt', 'r') as file:
                content = file.read()
        else:
            with open(f'./ZLYoutput/{self.alg_name}/TPCAP_{self.index}_resultViz_0.txt', 'r') as file:
                content = file.read()
        words = content.split()
        length=len(words)
        i = 0
        while i < length:
            if words[i] == "1":
                i = self.process_type_1( words, i)
            elif words[i] == "2":
                i = self.process_type_2(words, i)
            elif words[i] == "3":
                i = self.process_type_3(words, i,case)
            elif words[i] == "0":
                i = self.process_type_0(words, i)
            else:
                print("error")
                print("当前的i 是"+str(i))