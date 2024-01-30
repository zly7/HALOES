import casadi as ca
from casadi import *
from coordinatesTrans import coTrans
import time
from Vehicle import *
from PIL import Image, ImageDraw
class ZLYAnswer:
    def __init__(self,index,mul = 0.1,whtether_use_success_file=True):
        # 打开图片
        self.index = index
        self.whtether_use_success_file = whtether_use_success_file
        self.mul = mul
        self.vehicleNode3D = [] # for quba
        self.final_path = Path([], [], [])

       

    def process_type_1(self,draw, words, i):
        vehicle_x, vehicle_y = float(words[i+1]) * self.mul, float(words[i+2]) * self.mul
        yaw = float(words[i+3])
        self.vehicleNode3D.append(OBCAPath(vehicle_x, vehicle_y, yaw))
        self.final_path.x.append(vehicle_x)
        self.final_path.y.append(vehicle_y)
        self.final_path.yaw.append(yaw)
        return i + 11  

    def process_type_2(self,words, i):
        vehicle_x, vehicle_y =float(words[i+1]) * self.mul, float(words[i+2]) * self.mul
        quaternion = [float(words[j]) for j in range(i+4, i+8)]
        # roll, pitch, yaw = quaternion_to_euler(*quaternion)
        # vehicleNode3D.append([vehicle_x, vehicle_y, yaw])
        return i + 15  

    def process_type_3(self,draw, words, i):
        points = []
        i+=1
        for _ in range(4):
            point_x, point_y =float(words[i]), float(words[i+1])
            points.append((point_x, point_y))
            i += 3
        # draw.line(points + [points[0]], fill='blue', width=4)
        return i
    def readTXT(self):
        if self.whtether_use_success_file:
            with open(f'./ZLYoutput/TPCAP_{self.index}_resultViz_0_success.txt', 'r') as file:
                content = file.read()
        else:
            with open(f'./ZLYoutput/TPCAP_{self.index}_resultViz_0.txt', 'r') as file:
                content = file.read()

        save_path = f"./ZLYresult/trajectory/TPCAP_{self.index}_answer_trajectory.png"
        # 使用split()按空白字符分割文件内容
        words = content.split()

        #draw = ImageDraw.Draw(tmp)
        draw = -1
        length=len(words)
        flag=False
        i = 0
        while i < length:
            if words[i] == "1":
                i = self.process_type_1(draw, words, i)
            elif words[i] == "2":
                i = self.process_type_2(words, i)
            elif words[i] == "3":
                i = self.process_type_3(draw, words, i)