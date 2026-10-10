"""Regenerates all placeholder art.  Usage:  py -3.14 tools/gen_art.py [office|lobby|hotel|eleanor_room|speakeasy|alley|convent|convent_road|street|attic|club|library|motel|outskirts|church|sprites|items|ui]"""
import sys
from art import office, lobby, hotel, hotel_mess, speakeasy, alley, convent, convent_road, street, attic, club, library, motel, outskirts, church, sprites, items, ui

STEPS = {"sprites": sprites.build, "items": items.build, "office": office.build, "lobby": lobby.build,
         "hotel": hotel.build, "eleanor_room": hotel_mess.build, "speakeasy": speakeasy.build, "alley": alley.build, "convent": convent.build, "convent_road": convent_road.build, "street": street.build, "attic": attic.build, "club": club.build,
         "library": library.build, "motel": motel.build, "outskirts": outskirts.build, "church": church.build,
         "ui": ui.build}

if __name__ == "__main__":
    for name in (sys.argv[1:] or STEPS):
        STEPS[name]()
