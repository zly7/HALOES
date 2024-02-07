import pyobca
import numpy as np
import math as m
import matplotlib.pyplot as plt
import numpy as np

def quadraticPath(initialQuadraticPath, obstacles, vehicle, max_x, max_y, min_x, min_y, gap=1, cfg=None, sampleT=0.1, whether_care_origin_path = False):
    ds_path = downsample_smooth(initialQuadraticPath, gap, vehicle, sampleT)
    if len(ds_path)<2:
        print('no enough path point')
        return
    init_x = []
    init_y = []
    for state in ds_path:
        init_x += [state.x]
        init_y += [state.y]
    # obca optimization
    optimizer = pyobca.OBCAOptimizer(cfg=cfg,whether_fix_4Obs=False)
    optimizer.initialize(ds_path, obstacles, max_x=max_x, max_y=max_y, min_x=min_x, min_y=min_y)
    optimizer.build_model()
    if whether_care_origin_path == 1:
        optimizer.generate_constrain(kinematic_constraints=0.1)
    else:
        optimizer.generate_constrain(kinematic_constraints=0.0)
    optimizer.generate_constrain()
    optimizer.generate_variable()
    r = [[0.1, 0], [0, 0.1]]   #             self.lbx += [-self.v_cfg.max_acc, -self.v_cfg.max_steer_rate]
    if whether_care_origin_path == 1: # 用张力宇的2Da*启发式
        q = [[0.00, 0, 0, 0, 0], #            self.x0 += [[state.x, state.y, state.v,state.heading, state.steer]]
            [0, 0.00, 0, 0, 0],  
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0.0],
            ]
    elif whether_care_origin_path == 2: # 用张力宇的contourAlgorithm启发式
        q = [[0.05, 0, 0, 0, 0], #            self.x0 += [[state.x, state.y, state.v,state.heading, state.steer]]
            [0, 0.05, 0, 0, 0],  
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0.0],
            ]
    else:
        q = [[0, 0, 0, 0, 0],            
            [0, 0, 0, 0, 0],  
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0.0],
            ]
    optimizer.generate_object(r, q)
    optimizer.solve()

    x_opt = optimizer.x_opt.elements()
    y_opt = optimizer.y_opt.elements()
    v_opt = optimizer.v_opt.elements()
    heading_opt = optimizer.theta_opt.elements()
    steer_opt = optimizer.steer_opt.elements()
    a_opt = optimizer.a_opt.elements()
    steer_rate_opt = optimizer.steerate_opt.elements()


    return x_opt, y_opt, v_opt, heading_opt, steer_opt, a_opt, steer_rate_opt



def downsample_smooth(path, gap, cfg, T=0.1):
    if not path:
        print('no path ')
        return []
    ds_path = path[::gap]
    if len(ds_path) < 3:
        return ds_path
    else:
        for i in range(1, len(ds_path)-1):
            v_1 = (ds_path[i].x-ds_path[i-1].x)/T*m.cos(ds_path[i-1].heading) + \
                (ds_path[i].y-ds_path[i-1].y)/T*m.sin(ds_path[i-1].heading)
            v_2 = (ds_path[i+1].x-ds_path[i].x)/T*m.cos(ds_path[i].heading) + \
                (ds_path[i+1].y-ds_path[i].y)/T*m.sin(ds_path[i].heading)
            v = (v_1 + v_2)/2
            ds_path[i].v = v
        for i in range(len(ds_path)-1):
            if ds_path[i+1].heading - ds_path[i].heading > m.pi:
                ds_path[i+1].heading -= 2*m.pi
            elif ds_path[i+1].heading - ds_path[i].heading < -m.pi:
                ds_path[i+1].heading += 2*m.pi

        for i in range(len(ds_path)-1):
            ds_path[i].a += (ds_path[i+1].v - ds_path[i].v)/T
            diff_theta = ds_path[i+1].heading-ds_path[i].heading

            direction = 1
            if ds_path[i].v < 0:
                direction = -1
            move_distance = m.hypot((ds_path[i+1].x - ds_path[i].x), (ds_path[i+1].y - ds_path[i].y))
            # steer = np.clip(m.atan(diff_theta*cfg.lw/(move_distance*direction + 0.0000000000001)),
            #                 -cfg.MAX_STEER, cfg.MAX_STEER)
            steer = m.atan(diff_theta*cfg.lw/(move_distance*direction + 0.0000000000001)) # 所以其实这里的steer计算是有问题的
            if steer > cfg.MAX_STEER or steer < -cfg.MAX_STEER:
                print('最原本计算的转向角度超过了最大值，本身路径有问题')
            ds_path[i].steer = steer
        ds_path[-1] = path[-1]
        plot_path(ds_path=ds_path)
        return ds_path

def plot_path(ds_path):
    # 提取路径点和其他数据
    x = [point.x for point in ds_path]
    y = [point.y for point in ds_path]
    v = [point.v for point in ds_path]
    a = [point.a for point in ds_path]
    steer = [point.steer for point in ds_path]
    heading = [point.heading for point in ds_path]

    # 创建一个包含六个子图的图形
    fig, axs = plt.subplots(3, 2, figsize=(12, 12))

    # 绘制X坐标
    axs[0, 0].plot(x, marker='o')
    axs[0, 0].set_title('X Coordinate')
    axs[0, 0].set_xlabel('Point Index')
    axs[0, 0].set_ylabel('X')

    # 绘制Y坐标
    axs[0, 1].plot(y, marker='o')
    axs[0, 1].set_title('Y Coordinate')
    axs[0, 1].set_xlabel('Point Index')
    axs[0, 1].set_ylabel('Y')

    # 绘制速度
    axs[1, 0].plot(v, marker='o')
    axs[1, 0].set_title('Velocity')
    axs[1, 0].set_xlabel('Point Index')
    axs[1, 0].set_ylabel('Velocity (units/T)')

    # 绘制加速度
    axs[1, 1].plot(a, marker='o')
    axs[1, 1].set_title('Acceleration')
    axs[1, 1].set_xlabel('Point Index')
    axs[1, 1].set_ylabel('Acceleration (units/T^2)')

    # 绘制转向角速度
    axs[2, 0].plot(steer, marker='o')
    axs[2, 0].set_title('Steering Angle')
    axs[2, 0].set_xlabel('Point Index')
    axs[2, 0].set_ylabel('Steering Angle (radians)')

    # 绘制方向角
    axs[2, 1].plot(heading, marker='o')
    axs[2, 1].set_title('Heading')
    axs[2, 1].set_xlabel('Point Index')
    axs[2, 1].set_ylabel('Heading (radians)')

    plt.tight_layout()
    plt.show()