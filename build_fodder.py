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
# area_table = Table.load('Area')
empty_diya_table = Table.load('Empty_Diya')
empty_gaozhou_table = Table.load('Empty_Gaozhou')

def build_area_table(bundle_path: str) -> Table:
    rlt = Rlt.fenqu
    text = file_manager.read_body(bundle_path, rlt)
    bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
    fenqu_table = [Table.new(body, rlt.isX()) for body in bodys][0].crop(['区域ID号', '分区名称'])


    rlt = Rlt.changzhan
    text = file_manager.read_body(bundle_path, rlt)
    bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
    changzhan_table = [Table.new(body, rlt.isX()) for body in bodys][0].crop(['厂站ID', '区域ID'])

    area_table = Table.build_area_catalogue(changzhan_table, fenqu_table)
    return area_table


bundle_paths = file_manager.get_bundle_paths(fodder_subname)

for bundle_path in tqdm(bundle_paths):
    ## Area Begin
    area_table = build_area_table(bundle_path)
    ## Area End

    # fodder = Fodder.new_v0(bundle_path, area_table, empty_diya_table, empty_gaozhou_table)
    # fodder.standlize_power()
    # fodder.save(os.path.join(constant.fodder_folder_path, fodder_subname))
         
    try:
        fodder = Fodder.new_v0(bundle_path, area_table, empty_diya_table, empty_gaozhou_table)
        fodder.standlize_power()
        fodder.save(os.path.join(constant.fodder_folder_path, fodder_subname))
    except Exception as error:
        print('\n', bundle_path, error, '\n')
    