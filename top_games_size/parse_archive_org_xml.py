import xml.etree.ElementTree as ET

from top_games_size.game_size import GameSize


class File:
    def __init__(self, name, size, format):
        self.name = name
        self.size = size
        self.format = format

    @classmethod
    def from_xml(cls, xml_element):
        name = xml_element.get("name")
        size_element = xml_element.find("size")
        size = int(size_element.text) if size_element is not None else None
        format_element = xml_element.find("format")
        format = format_element.text if format_element is not None else None
        return cls(name, size, format)


def parse_archive_org_xml(xml_string):
    root = ET.fromstring(xml_string)

    game_sizes = []

    for file_element in root.findall("file"):
        file_obj = File.from_xml(file_element)
        if file_obj.format == "ZIP":
            game_sizes.append(GameSize(file_obj.name, file_obj.size))

    return game_sizes
