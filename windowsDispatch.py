import psutil
import os

# 假设大核是CPU 0, 1, 2, 3
big_cores = {0, 1, 2, 3, 4, 5, 6, 7,8,9,10,11,12}

for proc in psutil.process_iter(['name', 'pid']):
    try:
        process_name = proc.info['name'].lower()
        if "vmware" in process_name or "mkssandbox" in process_name :  
            pid = proc.info['pid']
            # 设置进程优先级为实时，需要管理员权限
            os.system(f'wmic process where ProcessId="{pid}" CALL setpriority "Realtime"')
            # 设置进程CPU亲和性，允许进程只在大核上运行
            affinity_mask = sum([1 << i for i in big_cores])
            os.system(f'PowerShell "$Process = Get-Process -Id {pid}; $Process.ProcessorAffinity={affinity_mask}"')
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
