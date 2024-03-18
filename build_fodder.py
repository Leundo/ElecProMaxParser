import os
import re

import src.constant as constant
import src.file_manager as file_manager
import src.parser as parser
from src.table import Table
from src.fodder import Fodder
from src.file_manager import Rlt
from tqdm import tqdm


fodder_subname = '20231101'
area_table = Table.load('Area')

bundle_paths = file_manager.get_bundle_paths(fodder_subname)

for bundle_path in tqdm(bundle_paths):   
    # fodder = Fodder.new_v0(bundle_path, area_table)
    # fodder.standlize_power()
    # fodder.save(os.path.join(constant.fodder_folder_path, fodder_subname))
         
    try:
        fodder = Fodder.new_v0(bundle_path, area_table)
        fodder.standlize_power()
        fodder.save(os.path.join(constant.fodder_folder_path, fodder_subname))
    except Exception as error:
        print(bundle_path, error)
    