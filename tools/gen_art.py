"""Regenerates all placeholder art.  Usage:  py -3.14 tools/gen_art.py [office|lobby|hotel|eleanor_room|speakeasy|alley|convent|convent_road|chicago_map|street|attic|club|library|motel|outskirts|church|rose_house|harrington|bedroom|act3|sprites|items|ui|puzzles]"""
import sys
from art import office, lobby, hotel, hotel_mess, speakeasy, alley, convent, convent_road, chicago_map, street, attic, club, library, motel, outskirts, church, act2_rooms, act3_rooms, sprites, items, ui, puzzles

STEPS = {"sprites": sprites.build, "items": items.build, "office": office.build, "lobby": lobby.build,
         "hotel": hotel.build, "eleanor_room": hotel_mess.build, "speakeasy": speakeasy.build, "alley": alley.build, "convent": convent.build, "convent_road": convent_road.build, "chicago_map": chicago_map.build, "street": street.build, "attic": attic.build, "club": club.build,
         "library": library.build, "motel": motel.build, "outskirts": outskirts.build, "church": church.build,
         "rose_house": act2_rooms.build_rose, "harrington": lambda: (act2_rooms.build_road(), act2_rooms.build_office()),
         "bedroom": act2_rooms.build_bedroom, "act3": act3_rooms.build,
         "ui": ui.build, "puzzles": puzzles.build}

if __name__ == "__main__":
    for name in (sys.argv[1:] or STEPS):
        STEPS[name]()
