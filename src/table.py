import re
import os
import sys
import pickle
from enum import Enum
from typing import List, Optional, Dict, Callable, Tuple

import src.constant as constant
from src.file_manager import Rlt
from src.util import equal


class Table:
    def __init__(self, title: str, headers: List[str], header_dict: Dict[str, int], rows: List[List[str]]):
        self.title = title
        self.headers = headers
        self.header_dict = header_dict
        self.rows = rows
            
    
    def pick(self, fixed_header: str, fixed_value: str, target_header: str) -> Optional[str]:
        fixed_location = self.header_dict.get(fixed_header, None)
        target_location = self.header_dict.get(target_header, None)
        if fixed_location is None or target_location is None:
            raise RuntimeError()
        
        for tuples in self.rows: 
            if tuples[fixed_location] == fixed_value:
                return tuples[target_location]
            
        return None
    
    
    def crop(self, headers: List[str], title: Optional[str] = None) -> 'Table':
        new_header_dict = {}
        new_rows = []
        locations = []
        for index, header in enumerate(headers):
            location = self.header_dict.get(header, None)
            if location is None:
                raise RuntimeError()
            locations.append(location)
            new_header_dict[header] = index
        
        for tuples in self.rows:
            new_rows.append([tuples[location] for location in locations])
        
        
        return Table(
            title=self.title if title is None else title,
            headers=headers,
            header_dict=new_header_dict,
            rows=new_rows
        )
        
    # Callable(self) -> (items, headers)
    def expand(self, new_headers: List[str], fn: Callable[['Table', List[str]], List[str]]):
        header_length = len(self.headers)
        self.headers += new_headers
        for index, new_header in enumerate(new_headers):
            self.header_dict[new_header] = header_length + index
            
        for index in range(len(self.rows)):
            self.rows[index] += fn(self, self.rows[index])
            
    def compare_and_set(self, header: str, expectation: str, value: str):
        location = self.header_dict.get(header, None)
        if location is None:
            raise RuntimeError()
        for index in range(len(self.rows)):
            if self.rows[index][location] == expectation:
                self.rows[index][location] = value
        
        
    def join(self, table: 'Table', this_headers: List[str], that_headers: List[str], title: Optional[str] = None):
        if len(this_headers) != len(that_headers) or len(this_headers) == 0:
            raise RuntimeError()
        
        new_rows = []
        new_headers = []
        new_header_dict = {}
                
        this_remaining_headers = [header for header in self.headers if header not in this_headers]
        that_remaining_headers = [header for header in table.headers if header not in that_headers]
        new_headers = this_headers + this_remaining_headers + that_remaining_headers
        for index, header in enumerate(new_headers):
            new_header_dict[header] = index

        this_header_locations = []
        that_header_locations = []
        this_remaining_header_locations = []
        that_remaining_header_locations = []
        
        for header in this_headers:
            location = self.header_dict.get(header, None)
            if location is None:
                raise RuntimeError()
            this_header_locations.append(location)
            
        for header in this_remaining_headers:
            location = self.header_dict.get(header, None)
            if location is None:
                raise RuntimeError()
            this_remaining_header_locations.append(location)
            
        for header in that_headers:
            location = table.header_dict.get(header, None)
            if location is None:
                raise RuntimeError()
            that_header_locations.append(location)
            
        for header in that_remaining_headers:
            location = table.header_dict.get(header, None)
            if location is None:
                raise RuntimeError()
            that_remaining_header_locations.append(location)
            
        for this_tuples in self.rows:
            for that_tuples in table.rows:
                if (equal([this_tuples[location] for location in this_header_locations], [that_tuples[location] for location in that_header_locations])):
                    new_tuples = [this_tuples[location] for location in this_header_locations] + [this_tuples[location] for location in this_remaining_header_locations] + [that_tuples[location] for location in that_remaining_header_locations]
                    new_rows.append(new_tuples)
        
        return Table(
            title=self.title if title is None else title,
            headers=new_headers,
            header_dict=new_header_dict,
            rows=new_rows
        )
        
        
    @staticmethod
    def new(body: str, isX: bool) -> Optional['Table']:
        lines = body.split('\n')
        if (len(lines) <= 3):
            return None
        title = lines[0][1:-1]
        if isX:
            headers = lines[1][2:].split()
        else:
            headers = lines[1][1:].split()
        header_dict = {}
        for index, header in enumerate(headers):
            header_dict[header] = index
            
        lines = lines[2:]
        rows = []
        for line in lines:
            if isX:
                tuples = line.split()
            else:
                tuples = line[1:].split()
            if len(tuples) > 0:
                rows.append(tuples)
        
        return Table(title=title, headers=headers, header_dict=header_dict, rows=rows)
        
        
    def standlize(self, rlt: Rlt, area_table: 'Table', is_first: bool) -> 'Table':
        if is_first:
            new_table = self.crop(rlt.first_targets())
            new_rows = []
            
            if rlt == Rlt.jiaoliuxianduan:
                yiduan_location = new_table.header_dict.get('一端厂站ID号', None)
                erduan_location = new_table.header_dict.get('二端厂站ID号', None)
                if yiduan_location is None or erduan_location is None:
                    raise RuntimeError()
                
                for tuples in new_table.rows:
                    if area_table.pick('厂站ID', tuples[yiduan_location], '分区名称') in ['西北', '新疆', '甘肃', '青海', '宁夏', '陕西'] and area_table.pick('厂站ID', tuples[erduan_location], '分区名称') in ['西北', '新疆', '甘肃', '青海', '宁夏', '陕西']:
                        new_rows.append(tuples)
            elif rlt == Rlt.fadianji:
                location = new_table.header_dict.get('厂站ID号', None)
                if location is None:
                    raise RuntimeError()
                
                # bpa_location = new_table.header_dict.get('BPA名', None)
                # for index, tuples in enumerate(new_table.rows):
                #     if tuples[bpa_location] == '胡二40__':
                #         print(area_table.pick('厂站ID', tuples[location], '分区名称'))
                #         print(tuples)
                
                for tuples in new_table.rows:
                    if area_table.pick('厂站ID', tuples[location], '分区名称') in ['西北', '新疆', '甘肃', '青海', '宁夏', '陕西']:
                        new_rows.append(tuples)
                        
            else:
                if rlt == Rlt.huanliuqi:
                    location = new_table.header_dict.get('厂站', None)
                else:
                    location = new_table.header_dict.get('厂站ID号', None)
                if location is None:
                    raise RuntimeError()
                
                for tuples in new_table.rows:
                    if area_table.pick('厂站ID', tuples[location], '分区名称') in ['西北', '新疆', '甘肃', '青海', '宁夏', '陕西']:
                        new_rows.append(tuples)
                        
            new_table.rows = new_rows
            
        else:
            new_table = self.crop(rlt.second_targets())
        
        return new_table
    
        
    @staticmethod
    def build_area_catalogue(changzhang_table: 'Table', fenqu_table: 'Table') -> 'Table':
        changzhang_table = changzhang_table.crop(['厂站ID', '区域ID'])
        fenqu_table = fenqu_table.crop(['区域ID号', '分区名称'])
        area_table = changzhang_table.join(fenqu_table, ['区域ID'], ['区域ID号'], 'Area')
        return area_table
    
    
    def save(self, title: Optional[str] = None):
        filename = '{}.data'.format(title if title is not None else self.title)
        with open(os.path.join(constant.middle_folder_path, filename), 'wb') as file:
            pickle.dump(self, file)
            
            
    @staticmethod
    def load(title: str) -> 'Table':
        filename = '{}.data'.format(title)
        with open(os.path.join(constant.middle_folder_path, filename), 'rb') as file:
            return pickle.load(file)