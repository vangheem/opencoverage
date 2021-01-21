from typing import Dict, List, Optional


class XMLSyntaxError(Exception):
    ...


class Element:
    text: str
    attrib: Dict[str, str]

    def find(self, key: str) -> Optional["Element"]:
        ...

    def findall(self, key: str) -> List["Element"]:
        ...


def fromstring(text) -> Element:
    ...


def tostring(Element) -> str:
    ...
