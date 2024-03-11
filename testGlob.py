import os
import glob

# 创建示例目录和文件
os.makedirs('test_folder', exist_ok=True)
with open('test_folder/test_file.txt', 'w') as f:
    f.write('This is a test file.')

# 使用glob.glob抓取文件
files = glob.glob('test_folder\\*')
print(files)
