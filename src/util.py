from typing import List, Any

def equal(lhs: List[Any], rhs: List[Any]) -> bool:
    if (len(lhs) != len(rhs)):
        return False
    for index in range(len(lhs)):
        if lhs[index] != rhs[index]:
            return False
    return True