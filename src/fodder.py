import re
import os
import sys
import pickle
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict

import src.file_manager as file_manager
import src.parser as parser
import src.constant as constant
from src.file_manager import Rlt
from src.table import Table
from src.util import equal


class Fodder:
    def __init__(self, name: str, nutrient_dict: Dict['Fodder.Nutrient', Table], power_dicts: List[Dict['Fodder.Power', Table]]):
        self.name = name
        self.nutrient_dict = nutrient_dict
        self.power_dicts = power_dicts

    class Nutrient(str, Enum):
        fadianji = 'fadianji'
        fuhe = 'fuhe'
        muxian = 'muxian'
        jiaoliuxianduan = 'jiaoliuxianduan'
        bianyaqiraozu = 'bianyaqiraozu'
        huanliuqi = 'huanliuqi'
        rongkangqi = 'rongkangqi'
        
    class Power(str, Enum):
        guzhang_xinxi = 'guzhangxinxi_xinxi' # 故障信息
        diyadipinjianzai_dongzuo = 'diyadipinjianzai_dongzuo' # 低压低频减载动作
        gaozhouqieji_dongzuo = 'gaozhouqieji_dongzuo' # 高周切机动作
        
        
    def save(self, save_path: str, title: Optional[str] = None):
        filename = '{}.data'.format(title if title is not None else self.name)
        with open(os.path.join(save_path, filename), 'wb') as file:
            pickle.dump(self, file)
            
            
    @staticmethod
    def load(load_path: str, title: str) -> 'Fodder':
        filename = '{}.data'.format(title)
        with open(os.path.join(load_path, filename), 'rb') as file:
            return pickle.load(file)
        
    
    # For 2024-03-18
    @staticmethod
    def new_v0(bundle_path: str, area_table: Table) -> 'Fodder':
        rlt = Rlt.fadianji
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        table = [Table.new(body, rlt.isX()) for body in bodys][0]
        fadianji_table = table.standlize(rlt, area_table, True)
        
        rlt = Rlt.fuhe
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        table = [Table.new(body, rlt.isX()) for body in bodys][0]
        fuhe_table = table.standlize(rlt, area_table, True)
        
        rlt = Rlt.muxian
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        table = [Table.new(body, rlt.isX()) for body in bodys][0]
        muxian_table = table.standlize(rlt, area_table, True)
        
        rlt = Rlt.jiaoliuxianduan
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        table = [Table.new(body, rlt.isX()) for body in bodys][0]
        jiaoliuxianduan_table = table.standlize(rlt, area_table, True)
        
        rlt = Rlt.bianyaqiraozu
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        table = [Table.new(body, rlt.isX()) for body in bodys][0]
        bianyaqiraozu_table = table.standlize(rlt, area_table, True)
        
        rlt = Rlt.huanliuqi
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        table = [Table.new(body, rlt.isX()) for body in bodys][0]
        huanliuqi_table = table.standlize(rlt, area_table, True)
        
        rlt = Rlt.rongkangqi
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        table = [Table.new(body, rlt.isX()) for body in bodys][0]
        rongkangqi_table = table.standlize(rlt, area_table, True)
        
        rlt = Rlt.x1
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        x1_tables = [Table.new(body, rlt.isX()) for body in bodys]

        rlt = Rlt.x2
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        x2_tables = [Table.new(body, rlt.isX()) for body in bodys]

        rlt = Rlt.x3
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        x3_tables = [Table.new(body, rlt.isX()) for body in bodys]

        nutrient_dict = {}
        nutrient_dict[Fodder.Nutrient.fadianji] = fadianji_table
        nutrient_dict[Fodder.Nutrient.fuhe] = fuhe_table
        nutrient_dict[Fodder.Nutrient.muxian] = muxian_table
        nutrient_dict[Fodder.Nutrient.jiaoliuxianduan] = jiaoliuxianduan_table
        nutrient_dict[Fodder.Nutrient.bianyaqiraozu] = bianyaqiraozu_table
        nutrient_dict[Fodder.Nutrient.huanliuqi] = huanliuqi_table
        nutrient_dict[Fodder.Nutrient.rongkangqi] = rongkangqi_table
        
        power_dict_x1 = {}
        power_dict_x1[Fodder.Power.guzhang_xinxi] = x1_tables[0]
        power_dict_x1[Fodder.Power.diyadipinjianzai_dongzuo] = x1_tables[1]
        power_dict_x1[Fodder.Power.gaozhouqieji_dongzuo] = x1_tables[2]
        
        power_dict_x2 = {}
        power_dict_x2[Fodder.Power.guzhang_xinxi] = x2_tables[0]
        power_dict_x2[Fodder.Power.diyadipinjianzai_dongzuo] = x2_tables[1]
        power_dict_x2[Fodder.Power.gaozhouqieji_dongzuo] = x2_tables[2]
        
        power_dict_x3 = {}
        power_dict_x3[Fodder.Power.guzhang_xinxi] = x3_tables[0]
        power_dict_x3[Fodder.Power.diyadipinjianzai_dongzuo] = x3_tables[1]
        power_dict_x3[Fodder.Power.gaozhouqieji_dongzuo] = x3_tables[2]
        
        power_dicts = [power_dict_x1, power_dict_x2, power_dict_x3]
        
        return Fodder(
            name=Path(bundle_path).stem,
            nutrient_dict=nutrient_dict,
            power_dicts=power_dicts
        )
        