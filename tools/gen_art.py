"""Regenerates all placeholder art.  Usage:  py -3.14 tools/gen_art.py [office|lobby|hotel|speakeasy|street|attic|club|library|motel|outskirts|church|sprites|items|ui]"""
import sys
from art import office, lobby, hotel, speakeasy, street, attic, club, library, motel, outskirts, church, sprites, items, ui

STEPS = {"sprites": sprites.build, "items": items.build, "office": office.build, "lobby": lobby.build,
         "hotel": hotel.build, "speakeasy": speakeasy.build, "street": street.build, "attic": attic.build, "club": club.build,
         "library": library.build, "motel": motel.build, "outskirts": outskirts.build, "church": church.build,
         "ui": ui.build}

if __name__ == "__main__":
    for name in (sys.argv[1:] or STEPS):
        STEPS[name]()
