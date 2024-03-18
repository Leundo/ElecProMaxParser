import os
import re

from typing import Optional

from src.file_manager import Rlt


def parse_body(text: str, label: str):
    founds = re.findall('(<{}>\n([^<][^\n]+\n)+)'.format(label), text, re.S)
    if len(founds) > 0:
        return founds[0][0]
    return None


    