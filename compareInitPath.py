import os.path

import numpy as np
import time
import csv
from case import Case
from Vehicle import Vehicle, Path, OBCAPath
from Show import show, show_compare
from quadraticOBCA import quadraticPath
from pyobca.search import *
from pympc.mpc_optimizer import MPCOptimizer
from saveCsv import saveCsv,saveTxt
import argparse
from readZLYAnswer import ZLYAnswer
import math
import matplotlib.pyplot as plt

path_nums = [2,5,8,11,12,14,24,27,32,35]
alg_names = ['HA','ENHA','EHHA']

index = 0
for path_num in path_nums:
    zlyAnswer = {}
    case = Case.read('BenchmarkCasesZLY/Case%d.csv' % path_num)
    for alg_name in alg_names:
        zlyAnswer[alg_name] = ZLYAnswer(path_num,mul=0.1,whtether_use_success_file=False,alg_name=alg_name,viz_index=0)
        zlyAnswer[alg_name].readTXT(case)
    plt.figure()
    plt.xlim(case.xmin, case.xmax)
    plt.ylim(case.ymin, case.ymax)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().set_axisbelow(True)
    plt.grid(linewidth=0.2)
    plt.xlabel('X / m', fontsize=8)
    plt.ylabel('Y / m', fontsize=8)
    for j in range(0, case.obs_num):
        plt.fill(case.obs[j][:, 0], case.obs[j][:, 1], facecolor='k', alpha=0.5)

    temp = case.vehicle.create_polygon(case.x0, case.y0, case.theta0)
    plt.plot(temp[:, 0], temp[:, 1], linestyle='--', linewidth=0.4, color='green')
    temp = case.vehicle.create_polygon(case.xf, case.yf, case.thetaf)
    plt.plot(temp[:, 0], temp[:, 1], linestyle='--', linewidth=0.4, color='red')
    # for alg_name in alg_names:
    #     path = zlyAnswer[alg_name].final_path
    #     plt.plot(path.x, path.y, color='red', linewidth=0.5)
    plt.plot(zlyAnswer['ENHA'].final_path.x, zlyAnswer['ENHA'].final_path.y, color='blue', linewidth=1.5, label='Extreme Narrow Space Hybrid A*')
    plt.plot(zlyAnswer['HA'].final_path.x, zlyAnswer['HA'].final_path.y, color='red', linewidth=1.5, label='Hybrid A*')
    plt.plot(zlyAnswer['EHHA'].final_path.x, zlyAnswer['EHHA'].final_path.y, color='green', linewidth=1.5, label='Enhanced Hybrid A*')
    plt.legend()
    plt.tight_layout()
    if not os.path.exists(f'./paper/compareInitPath'):
        os.mkdir(f'./paper/compareInitPath')
    plt.savefig(f'./paper/compareInitPath/case-{index}.png', dpi=300)
    index = index + 1
