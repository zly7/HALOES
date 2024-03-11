import glob
import os
import shutil

basePath = "./Result"
method = 'HA'
folders = glob.glob(f"{basePath}/{method}/*")  # 更正路径以匹配实际文件夹

for folder in folders:
    new_folder_path = os.path.join(folder, 'time-1')
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
    
    # 移动文件到新文件夹
    paths_to_move = glob.glob(folder+ '/*')
    files_to_move = [path for path in paths_to_move if os.path.isfile(path)]
    for file_path in files_to_move:
        shutil.move(file_path, new_folder_path)
    # 重命名文件
    files_to_rename = glob.glob(os.path.join(new_folder_path, 'output_result-test-1.txt'))
    for file_path in files_to_rename:
        new_file_path = file_path.replace('output_result-test-1.txt', 'output_result.txt')
        os.rename(file_path, new_file_path)

    
        