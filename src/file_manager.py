import os
import codecs
from enum import Enum
from typing import List

import src.constant as constant

class Rlt(str, Enum):
    x1 = 'Tscinfo_X_1.rlt'
    x2 = 'Tscinfo_X_2.rlt'
    x3 = 'Tscinfo_X_2.rlt'
    changzhan = '厂站信息.txt'              # 厂站表
    fenqu = '分区信息.txt'                  # 分区表
    fadianji = '发电机信息.txt'             # 发电机
    fuhe = '负荷信息.txt'                   # 负荷
    muxian = '母线信息.txt'                 # 母线
    jiaoliuxianduan = '交流线段信息.txt'    # 交流线路
    bianyaqiraozu = '变压器绕组信息.txt'    # 变压器
    huanliuqi = '换流器信息.txt'             # 直流系统设备
    # 串联补偿器 ?
    rongkangqi = '容抗器信息.txt'           # 并联电容/电抗器
    
    
    
    def isX(self) -> bool:
        return self == Rlt.x1 or self == Rlt.x2 or self == Rlt.x3
    
    def grips(self) -> List[str]:
        if self.isX():
            return ['故障信息', '低压低频减载动作', '高周切机动作']
        elif self == Rlt.changzhan:
            return ['厂站::在线系统']
        elif self == Rlt.fadianji:
            return ['发电机::在线系统']
        elif self == Rlt.fenqu:
            return ['分区::在线系统']
        elif self == Rlt.fuhe:
            return ['负荷::在线系统']
        elif self == Rlt.muxian:
            return ['母线::在线系统']
        elif self == Rlt.jiaoliuxianduan:
            return ['交流线段::在线系统']
        elif self == Rlt.bianyaqiraozu:
            return ['变压器绕组::在线系统']
        elif self == Rlt.huanliuqi:
            return ['换流器::在线系统']
        elif self == Rlt.rongkangqi:
            return ['容抗器::在线系统']
        
        raise Exception("Unknown rlt.")
    
    def first_targets(self) -> List[str]:
        if self.isX():
            raise Exception("Unknown rlt.")
        elif self == Rlt.changzhan:
            return ['厂站ID', '区域ID']
        elif self == Rlt.fenqu:
            return ['区域ID号', '分区名称']
        elif self == Rlt.fadianji:
            return ['发电机ID号', '发电机名称', '拓扑着色', '有功值', '无功值', '电压值', '厂站ID号', '发电机类型']
        elif self == Rlt.fuhe:
            return ['负荷ID号', '负荷名称', '拓扑着色', '有功值', '无功值', '厂站ID号']
        elif self == Rlt.muxian:
            return ['母线ID号', '母线名称', '拓扑着色', '线电压幅值', '电压相角', '厂站ID号']
        elif self == Rlt.jiaoliuxianduan:
            return ['交流线段ID号', '交流线段名称', '拓扑着色', '首端有功', '首端无功', '末端有功', '末端无功', '首端电流值', '末端电流值', '一端厂站ID号', '二端厂站ID号']
        elif self == Rlt.bianyaqiraozu:
            return ['变压器绕组ID号', '变压器绕组名称', '拓扑着色', '首端有功值', '首端无功值', '末端有功值', '末端无功值', '首端电流值', '末端电流值', '厂站ID号']
        elif self == Rlt.huanliuqi:
            return ['换流器序号', '换流器名称', '拓扑着色', '直流功率', '直流电压值', '电流值', '厂站']
        elif self == Rlt.rongkangqi:
            return ['容抗器ID号', '容抗器名称', '拓扑着色', '无功值', '厂站ID号']
        
        
        raise Exception("Unknown rlt.")
    
    def second_targets(self) -> List[str]:
        raise Exception("Unknown rlt.")
    

def get_bundle_paths() -> List[str]:
    bundle_paths = [ file.path for file in os.scandir(constant.data_folder_path) if file.is_dir() ]
    return bundle_paths

def read_body(bundle_path: str, rlt: Rlt) -> str:
    with codecs.open(os.path.join(bundle_path, rlt.value), encoding='GB18030') as file:
        text = file.read()
        return text

def read_tcsinfo(bundle_path: str, number: int) -> str:
    with codecs.open(os.path.join(bundle_path, 'Tscinfo_X_{}.rlt').format(number), encoding='GB18030') as file:
        text = file.read()
        return text
    
def read_changzhan(bundle_path: str) -> str:
    with codecs.open(os.path.join(bundle_path, '厂站信息.txt'), encoding='GB18030') as file:
        text = file.read()
        return text

def read_fadianji(bundle_path: str) -> str:
    with codecs.open(os.path.join(bundle_path, '发电机信息.txt'), encoding='GB18030') as file:
        text = file.read()
        return text
    
    
