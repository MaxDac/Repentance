"""Regenerates all placeholder art.  Usage:  py -3.14 tools/gen_art.py [office|lobby|speakeasy|attic|sprites|items|ui]"""
import sys
from art import office, lobby, speakeasy, attic, sprites, items, ui

STEPS = {"sprites": sprites.build, "items": items.build, "office": office.build, "lobby": lobby.build,
         "speakeasy": speakeasy.build, "attic": attic.build, "ui": ui.build}

if __name__ == "__main__":
    for name in (sys.argv[1:] or STEPS):
        STEPS[name]()
