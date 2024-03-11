import glob
import os
import shutil
import re
import cairosvg

basePath = "./Result"
method = 'ENHA'
folders = glob.glob(f"{basePath}/{method}/*")  # 更正路径以匹配实际文件夹
folders = sorted(folders, key=lambda x: int(re.search(r'case-(\d+)', x).group(1)))
folders = [folder for folder in folders if not re.search(r'case-10', folder)]
indexes = [re.search(r'case-(\d+)', path).group(1) for path in folders]
assert len(indexes) == len(set(indexes))
folder_suffix = "_kina"
for i in range(len(folders)):
    new_folder_path = os.path.join(folders[i], 'time-1')
    # source_path = os.path.join(new_folder_path, f'test-obca-traj{indexes[i]}.svg')
    source_path = os.path.join(new_folder_path, f'test-kina-{indexes[i]}.svg')
    if not os.path.exists(f"./paper/{method}{folder_suffix}"):
        os.makedirs(f"./paper/{method}{folder_suffix}")
    # 修改目标路径，以保存PNG格式的文件
    # dest_path_svg = os.path.join(f"./paper/{method}{folder_suffix}", f'case{i}FinalOptimizedPath.svg')
    # dest_path_png = os.path.join(f"./paper/{method}{folder_suffix}", f'case{i}FinalOptimizedPath.png')
    dest_path_png = os.path.join(f"./paper/{method}{folder_suffix}", f'case{i}FinalKinematics.png')
    # shutil.copy(source_path, dest_path_svg)  # 复制SVG文件
    # 将SVG转换成PNG
    cairosvg.svg2png(url=source_path, write_to=dest_path_png,dpi=300)
