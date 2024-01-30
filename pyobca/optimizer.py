from .search import GridMap, VehicleConfig, a_star_search
from casadi import *
from pypoman import compute_polytope_halfspaces


class OBCAOptimizer:
    def __init__(self, cfg: VehicleConfig = VehicleConfig()) -> None:
        self.L = cfg.length
        self.offset = cfg.length/2 - cfg.baselink_to_rear
        # self.lf = cfg.lf
        # self.lr = cfg.lr
        self.lwb = cfg.wheel_base
        self.v_cfg = cfg
        self.n_controls = 2
        self.n_states = 5
        self.n_dual_variable = 4
        self.constrains = []
        self.lbg = []
        self.ubg = []
        self.lbx = []
        self.ubx = []
        self.variable = []
        self.N = 0
        self.x0 = []
        self.obstacles = []
        self.G = DM([[1, 0],
                     [-1, 0],
                     [0, 1],
                     [0, -1], ])
        self.g = vertcat(SX([cfg.length/2, cfg.length/2,
                             0.5*cfg.width, 0.5*cfg.width]))
        self.T = cfg.T

    def initialize(self, init_guess, obs, max_x, max_y, min_x, min_y):
        self.init_state = SX([init_guess[0].x, init_guess[0].y,
                             init_guess[0].v, init_guess[0].heading, init_guess[0].steer])
        self.end_state = SX([init_guess[-1].x, init_guess[-1].y,
                            init_guess[-1].v, init_guess[-1].heading, init_guess[-1].steer])
        print(init_guess[-1].__dict__)
        self.N = len(init_guess)

        self.obstacles = obs
        for i in range(len(self.obstacles)):
            for j in range(len(self.obstacles[i])):
                self.obstacles[i][j] = self.obstacles[i][j].tolist()

        for state in init_guess:
            self.x0 += [[state.x, state.y, state.v,
                         state.heading, state.steer]]
        self.x0 += [[0]*(self.n_controls*(self.N-1))]
        self.x0 += [[0.1]*(self.n_dual_variable*(self.N)*2*len(obs))]
        self.ref_state = init_guess
        self.max_x = max_x
        self.max_y = max_y
        self.min_x = min_x
        self.min_y = min_y

    def build_model(self) -> bool:
        if self.N < 1:
            print('empty init guess')
            return False
        x = SX.sym('x') # 没有用SX.sym标记的都不是最基本的变量
        y = SX.sym('y')
        v = SX.sym('v')
        theta = SX.sym('theta')
        steering = SX.sym('steering')
        a = SX.sym('a')
        steering_rate = SX.sym('steering_rate')
        self.state = vertcat(vertcat(x, y, v, theta), steering)
        self.control = vertcat(a, steering_rate)
        # 这里使用的是Single-Track Model 修改为Kinematic Single-Track Model(KS),因此不需要知道lr以及lf的值
        # beta = atan(self.lr*tan(steering)/(self.lr+self.lf))
        # self.rhs = vertcat(vertcat(v*cos(theta+beta), v*sin(theta+beta),
        #                            a, v/self.lr*sin(beta)), steering_rate)
        # beta = atan(self.lr * tan(steering) / (self.lr + self.lf))
        self.rhs = vertcat(vertcat(v * cos(theta), v * sin(theta),
                                   a, v / self.lwb * tan(steering)), steering_rate) # 这里都是速度的指标。所以要有离散时间
        self.f = Function('f', [self.state, self.control], [self.rhs])
        self.X = SX.sym('X', self.n_states, self.N)
        self.U = SX.sym('U', self.n_controls, self.N-1) # 表示维度为n_controls*N-1，是一个二维数组
        self.MU = SX.sym('MU', self.n_dual_variable,
                         self.N*len(self.obstacles))
        self.LAMBDA = SX.sym('LAMBDA', self.n_dual_variable,
                             self.N*len(self.obstacles))
        self.obj = 0

        return True

    def solve(self):
        nlp_prob = {'f': self.obj, 'x': vertcat(*self.variable),
                    'g': vertcat(*self.constrains)} # 其中f是目标函数（这里初始设置为0），x是优化变量（状态和控制变量），g是约束条件
        solver = nlpsol('solver', 'ipopt', nlp_prob)
        sol = solver(x0=vertcat(*self.x0), lbx=self.lbx, ubx=self.ubx,
                     ubg=self.ubg, lbg=self.lbg) # 这一行已经解决完了
        u_opt = sol['x']
        self.x_opt = u_opt[0:self.n_states*(self.N):self.n_states]
        self.y_opt = u_opt[1:self.n_states*(self.N):self.n_states]
        self.v_opt = u_opt[2:self.n_states*(self.N):self.n_states]
        self.theta_opt = u_opt[3:self.n_states*(self.N):self.n_states]
        self.steer_opt = u_opt[4:self.n_states*(self.N):self.n_states]
        self.a_opt = u_opt[self.n_states*(self.N):self.n_states*(
            self.N)+self.n_controls*(self.N-1):self.n_controls]
        self.steerate_opt = u_opt[self.n_states*(self.N)+1:self.n_states*(
            self.N)+self.n_controls*(self.N-1):self.n_controls]

    def generate_object(self, r, q):
        R = SX(r)
        Q = SX(q)
        for i in range(self.N-1):
            st = self.X[:, i]
            ref_st = self.x0[i]
            error = st - ref_st
            con = self.U[:, i]

            self.obj += (con.T@R@con)
            self.obj += (error.T@Q@error)

    def generate_variable(self):
        for i in range(self.N):
            self.variable += [self.X[:, i]]
            # self.lbx += [0, 0, -self.v_cfg.max_v, -2 *
            #              pi, -self.v_cfg.max_front_wheel_angle]
            self.lbx += [self.min_x, self.min_y, -self.v_cfg.max_v, -2 *
                         pi, -self.v_cfg.max_front_wheel_angle]
            self.ubx += [self.max_x, self.max_y,
                         self.v_cfg.max_v, 2 * pi, self.v_cfg.max_front_wheel_angle]

        for i in range(self.N-1):
            self.variable += [self.U[:, i]]
            self.lbx += [-self.v_cfg.max_acc, -self.v_cfg.max_steer_rate]
            self.ubx += [self.v_cfg.max_acc, self.v_cfg.max_steer_rate]
        for i in range(len(self.obstacles)*self.N):
            self.variable += [self.MU[:, i]]
            self.lbx += [0.0, 0.0, 0.0, 0.0]
            self.ubx += [100000, 100000, 100000, 100000]
            self.variable += [self.LAMBDA[:, i]]
            self.lbx += [0.0, 0.0, 0.0, 0.0]
            self.ubx += [100000, 100000, 100000, 100000]

    def generate_constrain(self):
        # 起点约束
        self.constrains += [self.X[:, 0]-self.init_state]
        self.lbg += [0, 0, 0, 0, 0]
        self.ubg += [0, 0, 0, 0, 0]
        for i in range(self.N-1):
            st = self.X[:, i]
            con = self.U[:, i]
            f_value = self.f(st, con)
            st_next_euler = st+self.T*f_value
            st_next = self.X[:, i+1]
            # 中间点约束
            self.constrains += [st_next-st_next_euler]
            self.lbg += [0, 0, 0, 0, 0]
            self.ubg += [0, 0, 0, 0, 0]

        # 终点约束
        self.constrains += [self.X[:, -1]-self.end_state]
        self.lbg += [0, 0, 0, 0, 0]
        self.ubg += [0, 0, 0, 0, 0]

        for i in range(self.N):
            index = 0
            for obstacle in self.obstacles:
                A, b = compute_polytope_halfspaces(obstacle)
                st = self.X[:, i]
                heading = st[3]
                x = st[0]
                y = st[1]
                t = vertcat(x+self.offset*cos(heading),
                            y+self.offset*sin(heading))
                r = np.array([[cos(heading), -sin(heading)],
                              [sin(heading), cos(heading)]])
                lamb = vertcat(self.LAMBDA[:, len(self.obstacles)*i+index]) # 取到具体的lambda and mu
                mu = vertcat(self.MU[:, len(self.obstacles)*i+index])
                index += 1
                # 公式10的第四项约束
                self.constrains += [dot(vertcat(A.T)@lamb, vertcat(A.T)@lamb)]
                self.lbg += [0]
                self.ubg += [1]
                # 穿透距离（pen）
                self.constrains += [self.G.T@mu+(r.T@vertcat(A.T))@lamb]
                self.lbg += [0, 0]
                self.ubg += [0, 0]
                # 有符号距离（dist）
                self.constrains += [(-dot(self.g, mu)+dot(vertcat(A)@t-vertcat(b), lamb))]
                self.lbg += [0.001]
                self.ubg += [100000]
