import os
import re

import src.constant as constant
import src.file_manager as file_manager
import src.parser as parser
from src.table import Table
from src.file_manager import Rlt


bundle_path = file_manager.get_bundle_paths('20231101')[1]
rlt = Rlt.x1
text = file_manager.read_body(bundle_path, rlt)
bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
tables = [Table.new(body, rlt.isX()) for body in bodys]

tables[1].rows = []
tables[2].rows = []

tables[1].save('Empty_Diya')
tables[2].save('Empty_Gaozhou')