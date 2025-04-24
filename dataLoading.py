import json
import os
import pandas as pd
import shutil
import zipfile
import rarfile

class DataLoaderExporter:
    def __init__(self) -> None:
        pass
    def make_json_data(self, base_dir="../data/data_wm"):
        i = 0
        content = {}
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.txt'):
                    path = os.path.join(root, file)
                    path_split = path.split("\\")
                    with open(path, "r", encoding="utf-8") as f:
                        code = f.read()
                    try:
                        content[i] = {"task": path_split[1], "name": path_split[2],"file":path_split[3], "code": code}
                    except:
                        content[i] = {"task": path_split[1], "name": path_split[2],"file": "Nan", "code": code}
                    i += 1
        with open(base_dir + "\summary_data_wm.json", "w", encoding="utf-8") as fp:
            json.dump(content, fp, ensure_ascii=False) 

    def load_json_data(self, base_dir="../data/data_wm/summary_data_wm.json"):
        return  pd.read_json(base_dir, orient="index")
    
    def unpack_files(self, source_dir="../data/data_zip/wm", target_dir="../data/data_wm"):
        files = os.listdir(source_dir)
 
        for file in files:
            file_path = os.path.join(source_dir, file)
            
            if file.endswith('.zip'):
                archive = zipfile.ZipFile(file_path, 'r')
            elif file.endswith('.rar'):
                archive = rarfile.RarFile(file_path, 'r')
            else:
                continue  

            target_folder = os.path.join(target_dir, file.split('.')[0])
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            else:
                continue 
    
            for inner_file in archive.namelist():
                archive.extract(inner_file, target_folder)
   
            archive.close()