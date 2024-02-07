import matplotlib.pyplot as plt
from pypoman import plot_polygon


def show(path, case, path_num,stringEx, exp_name, args=None, data_num=0,title = None):
    plt.figure()
    # plt.subplot(1, 2, 1)
    plt.xlim(case.xmin, case.xmax)
    plt.ylim(case.ymin, case.ymax)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().set_axisbelow(True)
    if title is not None:
        # plt.title('Case %d' % (path_num))
        plt.title(title)
    plt.grid(linewidth=0.2)
    plt.xlabel('X / m', fontsize=8)
    plt.ylabel('Y / m', fontsize=8)
    for j in range(0, case.obs_num):
        plt.fill(case.obs[j][:, 0], case.obs[j][:, 1], facecolor='k', alpha=0.5)

    temp = case.vehicle.create_polygon(case.x0, case.y0, case.theta0)
    plt.plot(temp[:, 0], temp[:, 1], linestyle='--', linewidth=0.4, color='green')
    temp = case.vehicle.create_polygon(case.xf, case.yf, case.thetaf)
    plt.plot(temp[:, 0], temp[:, 1], linestyle='--', linewidth=0.4, color='red')

    for i in range(len(path.x)):
        temp = case.vehicle.create_polygon(path.x[i], path.y[i], path.yaw[i])
        # plot_polygon(temp, fill=False, color='b')
        plt.plot(temp[:, 0], temp[:, 1], linestyle='--', linewidth=0.15, color='blue')
        # plt.plot(path.x[i], path.y[i], marker='.', color='red', markersize=0.5)
    plt.plot(path.x, path.y, color='red', linewidth=0.5)
    plt.tight_layout()
    plt.savefig("./Result/{}case-{}/{}-traj{}.svg".format(stringEx,path_num, exp_name, path_num),bbox_inches='tight',pad_inches=0.05)
    if args.gen_npy:
        plt.savefig("./Result/{}case-{}/data_{}/{}-traj{}.svg".format(stringEx,path_num, data_num, exp_name, path_num),bbox_inches='tight',pad_inches=0.05)
    plt.show()



def show_compare(path1, path2, case, path_num, stringEx, exp_name, args=None, data_num=0, title=None):
    plt.figure()
    plt.xlim(case.xmin, case.xmax)
    plt.ylim(case.ymin, case.ymax)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().set_axisbelow(True)
    if title is not None:
        plt.title(title)
    plt.grid(linewidth=0.2)
    plt.xlabel('X / m', fontsize=8)
    plt.ylabel('Y / m', fontsize=8)

    # 绘制障碍物
    for j in range(case.obs_num):
        plt.fill(case.obs[j][:, 0], case.obs[j][:, 1], facecolor='k', alpha=0.5)

    # 绘制起始和终点位置
    temp = case.vehicle.create_polygon(case.x0, case.y0, case.theta0)
    plt.plot(temp[:, 0], temp[:, 1], linestyle='--', linewidth=0.4, color='green')
    temp = case.vehicle.create_polygon(case.xf, case.yf, case.thetaf)
    plt.plot(temp[:, 0], temp[:, 1], linestyle='--', linewidth=0.4, color='orange')

    plt.plot(path1.x, path1.y, color='blue', linewidth=1,label='Optimal Path')

    plt.plot(path2.x, path2.y, color='red', linewidth=1,label='Init Path')

    plt.tight_layout()
    plt.legend(loc = "best")
    plt.savefig("./Result/{}case-{}/{}-traj{}.svg".format(stringEx, path_num, exp_name, path_num), bbox_inches='tight', pad_inches=0.05)
    if args and args.gen_npy:
        plt.savefig("./Result/{}case-{}/data_{}/{}-traj{}.svg".format(stringEx, path_num, data_num, exp_name, path_num), bbox_inches='tight', pad_inches=0.05)
    plt.show()
