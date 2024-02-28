#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import sys
import glob
import re
import psutil
def get_argparse():
    parse = argparse.ArgumentParser(description="Information of Automated Parking.")
    parse.add_argument("--path_num", type=int, default=3, help="The number of case.")
    parse.add_argument("--exp_name", type=str, default='test', help="The exp name to save.")
    parse.add_argument("--trans", action="store_true", default=False, help="Whether to trans the point to (0,0,0).")
    parse.add_argument("--sample_time", type=float, default=0.15, help="The sample time.")
    parse.add_argument("--pre_length", type=int, default=5, help="The prediction horizon.")
    parse.add_argument("--obca_sample_time", type=float, default=0.1, help="The sample time of OBCA.")
    parse.add_argument("--obca_gap", type=int, default=1, help="The gap of obca.")
    parse.add_argument("--gen_npy", action="store_true", default=False, help="Generate the numpy data of trajectory.")
    parse.add_argument("--data_num", type=int, default=3, help="The number of generate numpy data.")
    parse.add_argument("--alg", type=str, default='HA', help="The algorithm of ZLY.")
    parse.add_argument("--viz_index", type=int, default=0, help="The whether VIZ.")
    parse.add_argument("--more_ocba", type=bool, default=False, help="The whether use ZLY.")
    args = parse.parse_args()
    return args

import threading

def auto_flush(file, interval):
    """
    定期刷新文件的函数。
    :param file: 要刷新的文件对象。
    :param interval: 刷新间隔（秒）。
    """
    while True:
        file.flush()
        time.sleep(interval)

if __name__ == '__main__':
    # 获取当前Python脚本的进程ID
    pid = os.getpid()
    p = psutil.Process(pid)

    # 在Windows系统上设置进程优先级
    # psutil.REALTIME_PRIORITY_CLASS 是最高优先级
    # 其他选项包括：HIGH_PRIORITY_CLASS, ABOVE_NORMAL_PRIORITY_CLASS, NORMAL_PRIORITY_CLASS, BELOW_NORMAL_PRIORITY_CLASS, IDLE_PRIORITY_CLASS
    try:
        p.nice(psutil.REALTIME_PRIORITY_CLASS)
        print(f"Process priority set to real-time for PID {pid}")
    except Exception as e:
        print(f"Failed to set process priority: {e}")
    args = get_argparse()
    path_num = args.path_num
    exp_name = args.exp_name
    use_trans = args.trans
    alg_name = args.alg
    whether_viz = args.viz_index
    more_ocba = args.more_ocba
    vehicle = Vehicle()
    # 模型预测轨迹规划
    case = Case.read('BenchmarkCasesZLY/Case%d.csv' % path_num)
    # case  = Case.read('BenchmarkCasesCase%d.csv' % path_num)
    if alg_name == "HA":
        stringEx = "HA/"
    elif alg_name == "EHHA":
        stringEx = "EHHA/"
    elif alg_name == "ENHA":
        stringEx = "ENHA/"
    elif alg_name == "OCBA":
        stringEx = "OCBA/"
    elif alg_name == "MPC_OCBA":
        stringEx = "MPC_OCBA/"
    else:
        print("Error: The algorithm name is not correct.")
        stringEx = ""
    if not os.path.exists("./Result/{}case-{}".format(stringEx,path_num)):
        os.mkdir("./Result/{}case-{}".format(stringEx,path_num))

    files = glob.glob(f"./Result/{stringEx}case-{path_num}" + "/output_result-*.txt")
    max_index = 0
    for file in files:
        # 提取文件名中的索引部分
        match = re.search(r'output_result-.*-(\d+)\.txt', file)
        if match:
            index = int(match.group(1))
            if index > max_index:
                max_index = index
    new_index = max_index + 1
    out_file = open("./Result/{}case-{}/output_result-{}-{}.txt".format(stringEx,path_num, exp_name,new_index), 'w', encoding='utf-8')
    original_stdout = sys.stdout
    sys.stdout = out_file
    flush_interval = 1  # 设置刷新间隔（秒）
    flush_thread = threading.Thread(target=auto_flush, args=(out_file, flush_interval))
    flush_thread.daemon = True  # 设置为守护线程，确保程序退出时线程也会退出
    flush_thread.start()

    if alg_name=="EHHA" or alg_name=="ENHA" or alg_name=="HA":
        zlyAnswer = ZLYAnswer(path_num,mul=0.1,whtether_use_success_file=False,alg_name=alg_name,)
        zlyAnswer.readTXT(case)
        initQuadraticPath = zlyAnswer.vehicleNode3D
        final_path = zlyAnswer.final_path
    elif alg_name=="OCBA":
        if more_ocba:
            zlyAnswer = ZLYAnswer(path_num,mul=1,whtether_use_success_file=False,alg_name=alg_name,more_ocba=more_ocba)
            zlyAnswer.readTXT(case)
            final_path = zlyAnswer.final_path
            initQuadraticPath = zlyAnswer.vehicleNode3D
        else:
            zlyAnswer = ZLYAnswer(path_num,mul=0.1,whtether_use_success_file=False,alg_name=alg_name)
            zlyAnswer.readTXT(case)
            initQuadraticPath = zlyAnswer.vehicle_2d_path
            initQuadraticPath[0].heading = case.theta0
            initQuadraticPath[-1].heading = case.thetaf
            lengthPath = len(initQuadraticPath)
            for i in range(1,len(initQuadraticPath)-1):
                initQuadraticPath[i].heading = math.atan2((initQuadraticPath[i].y - initQuadraticPath[i-1].y) , (initQuadraticPath[i].x - initQuadraticPath[i-1].x))
                # initQuadraticPath[i].heading = case.theta0 + (case.thetaf - case.theta0) * i / lengthPath
            final_path = Path([initQuadraticPath[i].x for i in range(len(initQuadraticPath))],
                            [initQuadraticPath[i].y for i in range(len(initQuadraticPath))],
                            [initQuadraticPath[i].heading for i in range(len(initQuadraticPath))])


    elif alg_name=="MPC_OCBA":
        if more_ocba:
            zlyAnswer = ZLYAnswer(path_num,mul=1,whtether_use_success_file=False,alg_name=alg_name,more_ocba=more_ocba)
            zlyAnswer.readTXT(case)
            final_path = zlyAnswer.final_path
            initQuadraticPath = zlyAnswer.vehicleNode3D
        else:
            startTime = time.time()
            mpc_optimizer = MPCOptimizer(case, vehicle, args)
            mpc_optimizer.initialize()
            mpc_optimizer.build_model()
            mpc_optimizer.generate_object(disCostFinal=50000, deltaCostFinal=10000, disCost=1000, deltaCost=5000,
                                        aCost=0, steerCost=0, obsPower=1.6)
            mpc_optimizer.generate_constrain()
            final_path, initQuadraticPath = mpc_optimizer.solve()
            endTime = time.time()
            print("MPC 无视障碍物找到初始解所花时间: ", endTime - startTime)
    else:
        print("Error: The algorithm name is not correct.")
        sys.exit(1)
    # OBCA二次优化,这里显然就是生成的path


    cfg = VehicleConfig()
    cfg.T = args.sample_time
    gap = args.obca_gap
    sampleT = args.obca_sample_time
    obstacles = []
    for obs_i in range(len(case.obs)):
        obs = list(case.obs[obs_i])
        obstacles.append(obs)
    if alg_name=="OCBA" or alg_name=="MPC_OCBA":
        whether_care_origin_path = False    
    else:
        whether_care_origin_path = False # 这里感觉care 原本的路径反而会出一些问题
    whether_special_hyperparameter = False
    # if alg_name=="MPC_OCBA" or alg_name=="OCBA":
    #     whether_special_hyperparameter = True
    path_x, path_y, path_v, path_yaw, path_steer, path_a, path_steer_rate = quadraticPath(
                                            initialQuadraticPath=initQuadraticPath, obstacles=obstacles,
                                            vehicle=vehicle, max_x=case.xmax, max_y=case.ymax,
                                            min_x=case.xmin, min_y=case.ymin,
                                            gap=gap, cfg=cfg, sampleT=sampleT,whether_care_origin_path=whether_care_origin_path,
                                            whether_viz=whether_viz,whether_special_hyperparameter=whether_special_hyperparameter)
    # 画图
    obcaPath = Path(path_x, path_y, path_yaw)


    if args.gen_npy and not os.path.exists("./Result/{}case-{}/data_{}".format(stringEx,path_num, args.data_num)):
        os.mkdir("./Result/{}case-{}/data_{}".format(stringEx,path_num, args.data_num))
    show(final_path, case, path_num, stringEx, exp_name+"-init", args, data_num=args.data_num)
    show(obcaPath, case, path_num, stringEx, exp_name+"-obca", args, data_num=args.data_num)
    obcaPath_5gap = Path(path_x[::5], path_y[::5], path_yaw[::5])
    show(obcaPath_5gap, case, path_num, stringEx, exp_name+"-5gap", args, data_num=args.data_num)
    final_path_5gap = Path(final_path.x[::5], final_path.y[::5], final_path.yaw[::5])
    show_compare(obcaPath_5gap, final_path_5gap, case, path_num, stringEx, exp_name+"-compare", args, data_num=args.data_num)
    path_t = [sampleT * k for k in range(len(path_x))]
    saveCsv(path_t=path_t, path_x=path_x, path_y=path_y, path_v=path_v, path_yaw=path_yaw, path_a=path_a,
            path_steer=path_steer, path_steer_rate=path_steer_rate, init_x=final_path.x, init_y=final_path.y,
            sampleT=sampleT, exp_name=exp_name, path_num=path_num, args=args, data_num=args.data_num,stringEx=stringEx)
    if(alg_name=="MPC_OCBA" or alg_name=="OCBA"):
        saveTxt(path_x=path_x, path_y=path_y,  path_yaw=path_yaw, stringEx=stringEx, path_num=path_num)
    sys.stdout = original_stdout
    out_file.close()



