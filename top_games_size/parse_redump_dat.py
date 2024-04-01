import xml.etree.ElementTree as ET


class Game:
    def __init__(self, name, category, description, roms):
        self.name = name
        self.category = category
        self.description = description
        self.roms = roms


class Rom:
    def __init__(self, name, size, crc, md5, sha1):
        self.name = name
        self.size = size
        self.crc = crc
        self.md5 = md5
        self.sha1 = sha1


def parse_redump_xml(xml_string):
    root = ET.fromstring(xml_string)

    games = []

    for game_element in root.findall("game"):
        name = game_element.attrib["name"]
        category = game_element.find("category").text
        description = game_element.find("description").text

        roms = []
        for rom_element in game_element.findall("rom"):
            rom = Rom(
                rom_element.attrib["name"],
                int(rom_element.attrib["size"]),
                rom_element.attrib.get("crc", ""),
                rom_element.attrib.get("md5", ""),
                rom_element.attrib.get("sha1", ""),
            )
            roms.append(rom)

        game = Game(name, category, description, roms)

        ## Filter out junk
        if category == "Games":
            games.append(game)

    return games
