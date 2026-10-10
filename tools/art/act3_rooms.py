"""Act 3 locations: the back of the Harrington mansion at night (kitchen door, alarm bell, coal bin), the dark kitchen,
Harrington senior's study, his bedroom (see mansion.py), the prison visiting room and the car on the outskirts road
(see act3_extra.py).

Like act2_rooms, each room is painted once per state and the state overlays are cut against the base so they line up
pixel-exactly at the printed top-left."""
from .mansion import build_exterior, build_kitchen, build_study, build_bedroom


def build():
    build_exterior()
    build_kitchen()
    build_study()
    build_bedroom()
    from . import act3_extra
    act3_extra.build_prison()
    act3_extra.build_car()