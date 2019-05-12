from bs4 import element

from typing import Optional, List


def select_one(tag: element.Tag, selector: str, attribute: str, default: Optional[str] = None) -> Optional[str]:
    el = tag.select_one(selector)
    if el is None:
        return default
    if attribute == 'text':
        return el.text
    return el.get(attribute, default)


def select_text_one(tag: element.Tag, selector: str):
    return select_one(tag, selector, 'text', '')


def select_all(tag: element.Tag, selector: str, attribute: str) -> List[str]:
    result = []
    for el in tag.select(selector):
        if attribute == 'text':
            result.append(el.text)
        else:
            attr_value = el.get(attribute)
            if attr_value is not None:
                result.append(attr_value)
    return result
