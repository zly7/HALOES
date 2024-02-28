import subprocess
import time

def run_script(script_name, python_options=None, script_args=None):
    """执行指定的 Python 脚本，带有额外的 Python 解释器选项和脚本参数"""
    # 建立命令列表
    command = ['python']
    
    # 添加任何指定的 Python 解释器选项
    if python_options:
        command.extend(python_options)
    
    # 添加脚本名称
    command.append(script_name)
    
    # 添加任何脚本参数
    if script_args:
        command.extend(script_args)
    
    # 执行命令
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name} with options {python_options} and args {script_args}: {e}")

if __name__ == "__main__":
    # methods = ['EHHA']
    # methods = ['HA']
    methods = ['ENHA']
    for index in [2,5,8,10,11,12,14,24,27,31,35]:
    # for index in [28,29,33]:
        for method in methods:
            run_script('main.py', script_args=['--path_num', str(index), '--exp_name', "test", '--alg', method])
            print(f"Finished running {method} for path {index}")
            time.sleep(1)
