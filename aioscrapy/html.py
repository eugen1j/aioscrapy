"""
bs4 helper functions.
"""

from typing import Optional, List
from bs4 import element


def select_one(tag: element.Tag, selector: str,
               attribute: str, default: Optional[str] = None) -> Optional[str]:
    """

    :param tag:
    :param selector:
    :param attribute:
    :param default:
    :return:
    """
    elem = tag.select_one(selector)
    if elem is None:
        return default
    if attribute == 'text':
        return elem.text
    return elem.get(attribute, default)


def select_text_one(tag: element.Tag, selector: str):
    """

    :param tag:
    :param selector:
    :return:
    """
    return select_one(tag, selector, 'text', '')


def select_all(tag: element.Tag, selector: str, attribute: str) -> List[str]:
    """

    :param tag:
    :param selector:
    :param attribute:
    :return:
    """
    result = []
    for elem in tag.select(selector):
        if attribute == 'text':
            result.append(elem.text)
        else:
            attr_value = elem.get(attribute)
            if attr_value is not None:
                result.append(attr_value)
    return result
