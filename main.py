import os
import re

import src.constant as constant
import src.file_manager as file_manager
import src.parser as parser
from src.table import Table
from src.fodder import Fodder
from src.file_manager import Rlt



area_table = Table.load('Area')

bundle_paths = file_manager.get_bundle_paths('20231101')
for bundle_path in bundle_paths[1:]:
    fodder = Fodder.new_v0(bundle_path, area_table)
    fodder.standlize_power()
    print(fodder)
    break
        
    try:
        fodder = Fodder.new_v0(bundle_path, area_table)
        fodder.standlize_power()
        print(fodder)
        break
    except Exception as error:
        print(error)
    