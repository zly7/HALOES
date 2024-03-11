import glob
import re
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
    map_last_index = {}
    methods = ['HA','EHHA','ENHA']
    for method in methods:
        for index in [2,5,8,10,11,12,14,24,27,32,35]:
            files = glob.glob(f"./ZLYoutput/{method}/*")
            pattern = rf"TPCAP_{index}_resultViz_(\d+)\.txt"

            # 提取并转换Y值为整数
            values = [int(match.group(1)) for file in files if (match := re.search(pattern, file))]

            filesAlreadyRun = glob.glob(f"./Result/{method}/case-{index}/*")
            patternForTime= rf"time-(\d+)\.txt"
            valuesAlreadyRun = [int(match.group(1)) for file in filesAlreadyRun if (match := re.search(patternForTime, file))]
            max_index = max(values) if values else 0
            if map_last_index.get((method,index)) is None:
                map_last_index[(method,index)] = 0
                start_index = 0
            else:
                start_index = map_last_index[(method,index)]
            for i in range(start_index, min(max_index+1, start_index+10)):
                run_script('main.py', script_args=['--path_num', str(index), '--exp_name', "test", 
                                                '--alg', method,'--viz_index', str(i)])
                print(f"Finished running {method} for path {index}")
                time.sleep(1)
                map_last_index[(method,index)] = i
