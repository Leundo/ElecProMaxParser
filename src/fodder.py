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
        
        
    def standlize_power(self):
        for index in range(len(self.power_dicts)):
            self.power_dicts[index][Fodder.Power.guzhang_xinxi] = self.power_dicts[index][Fodder.Power.guzhang_xinxi].crop(['功角裕度', '暂态电压安全裕度', '电压稳定裕度', '电压偏移裕度', '暂态频率偏移裕度', '动态阻尼裕度', '静态安全裕度'])
            self.power_dicts[index][Fodder.Power.diyadipinjianzai_dongzuo] = self.power_dicts[index][Fodder.Power.diyadipinjianzai_dongzuo].crop(['BPA名', '有功减少量', '无功减少量'])
            
            # diyadipinjianzai_dongzuo
            fuhe_helper_table = self.nutrient_dict[Fodder.Nutrient.fuhe].crop(['负荷ID号', 'BPA名', '有功值', '无功值'])
            length = len(self.power_dicts[index][Fodder.Power.diyadipinjianzai_dongzuo].rows)
            self.power_dicts[index][Fodder.Power.diyadipinjianzai_dongzuo] = self.power_dicts[index][Fodder.Power.diyadipinjianzai_dongzuo].join(fuhe_helper_table, ['BPA名'], ['BPA名'])
            if len(self.power_dicts[index][Fodder.Power.diyadipinjianzai_dongzuo].rows) != length:
                print(self.name)
                raise RuntimeError()
            self.power_dicts[index][Fodder.Power.diyadipinjianzai_dongzuo].expand(['有功减少量百分比', '无功减少量百分比'], Fodder.expand_diyadipinjianzai_dongzuo)

            # gaozhouqieji_dongzuo
            self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo] = self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo].crop(['机组BPA名', '识别码'])
            
            self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo].compare_and_set('识别码', '\'\'', '0')
            fadianji_helper_table = self.nutrient_dict[Fodder.Nutrient.fadianji].crop(['发电机ID号', 'BPA名', '机组识别码'])
            
            # location = fadianji_helper_table.header_dict.get('BPA名', None)
            # for tuples in fadianji_helper_table.rows:
            #     if tuples[location] == '胡二40__':
            #         print(tuples)
                
            length = len(self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo].rows)
            # print(self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo].rows)
            self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo] = self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo].join(fadianji_helper_table, ['机组BPA名', '识别码'], ['BPA名', '机组识别码'])
            # print(self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo].rows)

            # if len(self.power_dicts[index][Fodder.Power.gaozhouqieji_dongzuo].rows) != length:
            #     raise RuntimeError()
               

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
        
    @staticmethod
    def expand_diyadipinjianzai_dongzuo(table: Table, tuples: List[str]):
        yd_location = table.header_dict.get('有功减少量', None)
        y_location = table.header_dict.get('有功值', None)
        wd_location = table.header_dict.get('无功减少量', None)
        w_location = table.header_dict.get('无功值', None)
        if yd_location is None or y_location is None or wd_location is None or w_location is None:
            raise RuntimeError()
        
        if float(tuples[y_location]) == 0 or float(tuples[w_location]) == 0:
            return ['0', '0']
        elif float(tuples[y_location]) == 0:
            return [str(float(tuples[wd_location]) / float(tuples[w_location])), str(float(tuples[wd_location]) / float(tuples[w_location]))]
        else:
            return [str(float(tuples[yd_location]) / float(tuples[y_location])), str(float(tuples[yd_location]) / float(tuples[y_location]))]

    
    # For 2024-03-18
    @staticmethod
    def new_v0(bundle_path: str, area_table: Table, empty_diya_table: Table, empty_gaozhou_table: Table) -> 'Fodder':
        rlt = Rlt.fadianji
        text = file_manager.read_body(bundle_path, rlt)
        bodys = [parser.parse_body(text, grip) for grip in rlt.grips()]
        table = [Table.new(body, rlt.isX()) for body in bodys][0]
        
        # location = table.header_dict.get('BPA名', None)
        # for tuples in table.rows:
        #     if tuples[location] == '胡二40__':
        #         print(tuples)
                    
        fadianji_table = table.standlize(rlt, area_table, True)
        fadianji_table.compare_and_set('机组识别码', '\'\'', '0')
        
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
        power_dict_x1[Fodder.Power.diyadipinjianzai_dongzuo] = x1_tables[1] if x1_tables[1] is not None else empty_diya_table
        power_dict_x1[Fodder.Power.gaozhouqieji_dongzuo] = x1_tables[2] if x1_tables[2] is not None else empty_gaozhou_table
        
        power_dict_x2 = {}
        power_dict_x2[Fodder.Power.guzhang_xinxi] = x2_tables[0]
        power_dict_x2[Fodder.Power.diyadipinjianzai_dongzuo] = x2_tables[1] if x2_tables[1] is not None else empty_diya_table
        power_dict_x2[Fodder.Power.gaozhouqieji_dongzuo] = x2_tables[2] if x2_tables[2] is not None else empty_gaozhou_table
        
        power_dict_x3 = {}
        power_dict_x3[Fodder.Power.guzhang_xinxi] = x3_tables[0]
        power_dict_x3[Fodder.Power.diyadipinjianzai_dongzuo] = x3_tables[1] if x3_tables[1] is not None else empty_diya_table
        power_dict_x3[Fodder.Power.gaozhouqieji_dongzuo] = x3_tables[2] if x3_tables[2] is not None else empty_gaozhou_table
        
        power_dicts = [power_dict_x1, power_dict_x2, power_dict_x3]
        
        return Fodder(
            name=Path(bundle_path).stem,
            nutrient_dict=nutrient_dict,
            power_dicts=power_dicts
        )
        