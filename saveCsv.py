import csv
import matplotlib.pyplot as plt
import numpy as np


def saveCsv(path_t, path_x, path_y, path_v, path_yaw, path_a, path_steer, path_steer_rate, init_x, init_y, sampleT, 
            exp_name, path_num, args=None, data_num=0, stringEx=''):
    # 使用 stringEx 更新所有文件和目录路径
    base_path = "./Result/{}case-{}".format(stringEx, path_num)
    data_path = "{}/data_{}".format(base_path, data_num) if args and args.gen_npy else ""

    with open('{}/{}-result-{}.csv'.format(base_path, exp_name, path_num), 'w', encoding='utf-8', newline='') as fp:
        # 写
        writer = csv.writer(fp)
        for i in range(len(path_t)):
            writer.writerow([path_t[i], path_x[i], path_y[i], path_yaw[i]])

    with open('{}/{}-result-state-{}.csv'.format(base_path, exp_name, path_num), 'w', encoding='utf-8', newline='') as fp:
        # 写
        writer = csv.writer(fp)
        for i in range(len(path_t)):
            writer.writerow([path_t[i], path_x[i], path_y[i], path_v[i], path_yaw[i], path_steer[i]])

    with open('{}/{}-result-control-{}.csv'.format(base_path, exp_name, path_num), 'w', encoding='utf-8', newline='') as fp:
        # 写
        writer = csv.writer(fp)
        for i in range(len(path_a)):
            writer.writerow([path_t[i], path_a[i], path_steer_rate[i]])

    # 保存图片
    fig, ax = plt.subplots()
    ax.plot(path_x, path_y, 'go', ms=3, label='optimized path')
    ax.plot(init_x, init_y, 'ro', ms=3, label='init path')
    ax.legend()
    plt.savefig("{}/{}-err-traj-{}.svg".format(base_path, exp_name, path_num))

    fig2, ax2 = plt.subplots(4)
    plt.subplots_adjust(hspace=0.35)
    t_v = [sampleT*k for k in range(len(path_v))]
    t_a = [sampleT*k for k in range(len(path_a))]
    t_steer = [sampleT * k for k in range(len(path_steer))]
    t_steer_rate = [sampleT*k for k in range(len(path_steer_rate))]
    ax2[0].plot(t_v, path_v, label='v-t')
    ax2[0].set_ylabel('y/(m/s)')
    ax2[1].plot(t_a, path_a, label='a-t')
    ax2[1].set_ylabel('y/(m/s^2)')
    ax2[2].plot(t_steer, path_steer, label='steer-t')
    ax2[2].set_ylabel('y/(rad)')
    ax2[3].plot(t_steer_rate, path_steer_rate, label='steer-rate-t')
    ax2[3].set_ylabel('y/(rad/s)')
    ax2[-1].set_xlabel('time/s')  # -1表示最后一个子图
    for ax in ax2:
        ax.legend()
    plt.tight_layout()  # 添加这一行
    plt.savefig("{}/{}-kina-{}.svg".format(base_path, exp_name, path_num))

    # 如果生成 numpy 文件
    if args and args.gen_npy:
        npy_files = ['array_x', 'array_y', 'array_v', 'array_yaw', 'array_a', 'array_steer', 'array_steer_rate', 'array_t']
        arrays = [path_x, path_y, path_v, path_yaw, path_a, path_steer, path_steer_rate, path_t]
        for file, array in zip(npy_files, arrays):
            np.save(f"{data_path}/{file}", array)

def saveTxt(path_x,path_y,path_yaw,path_num, stringEx=''):
    with open(f'./Result/{stringEx}case-{path_num}/TPCAP_{path_num}_resultViz_0.txt', 'w') as file:
        for i in range(len(path_x)):
            file.write("1\n")
            file.write(f"{path_x[i]} {path_y[i]} {path_yaw[i]}\n")






