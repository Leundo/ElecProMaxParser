import os
import re

import src.constant as constant
import src.file_manager as file_manager
import src.parser as parser
from src.table import Table
from src.file_manager import Rlt


bundle_path = file_manager.get_bundle_paths()[0]
rlt = Rlt.fenqu
text = file_manager.read_body(bundle_path, rlt)
bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
fenqu_table = [Table.new(body, rlt.isX()) for body in bodys][0].crop(['区域ID号', '分区名称'])


rlt = Rlt.changzhan
text = file_manager.read_body(bundle_path, rlt)
bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
changzhan_table = [Table.new(body, rlt.isX()) for body in bodys][0].crop(['厂站ID', '区域ID'])

area_table = Table.build_area_catalogue(changzhan_table, fenqu_table)

area_table.save()