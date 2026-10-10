"""Character sprites, painted by figure.py in the manner of Fate of Atlantis-era VGA adventures.

Walkable characters (Micah, Daniel) get a 10 x 3 sheet of 64x96 frames:
  row 0  side view, facing right : idle, walk 1-8, talk
  row 1  front 3/4 view          : idle, walk 1-6, talk A, talk B
  row 2  back 3/4 view           : idle, walk 1-6
NPCs get a 3-frame strip of 56x96 frames (idle, talk A, talk B) in a 3/4 view facing screen-right; scenes flip them.
"""
from .common import save
from .figure import figure as _figure, pose, walk_pose, sheet, kneel_figure as _kneel


def figure(spec, ps, fw, fh):
    return _figure(dict(spec, h=spec["h"] * SCALE), ps, fw, fh)

FW, FH = 64, 96
NPC_W = 56
SCALE = 1.2  # FOTA-sized: about a third of the play area tall
STRIDE_FRAMES = 8


def _vee(y1=0.33, w=0.034, col="e3d7bf", tie=None, top=0.215):
    d = [("strip", top, y1, w, 0.0, col)]
    if tie:
        d.append(("strip", top + 0.012, y1 - 0.01, 0.007, 0.009, tie))
    return d


MICAH = dict(h=66, sw=0.142, skin="d8a480", hair="2a1d16", hat="fedora", hat_col="5c4838", band="1a120e",
             torso="ae8848", collar="ae8848", coat=dict(col="ae8848", top=0.40, hem=0.745, flare=0.035),
             pants="4a433b", shoes="2b1b14",
             decals=_vee(0.335, 0.036, "e3d7bf", "7b1f2a") + [("belt", 0.415, "6a4e26"), ("line", 0.44, 0.74)])
DANIEL = dict(h=64, sw=0.13, skin="e0b090", hair="5a4636", torso="476d5c", collar="d8d2c2", pants="4d6288",
              shoes="ddd7ca", hipw=0.094, top_hem=0.47)
# Teddy Harrington: a rich man's son in a tailored double-breasted grey suit with peaked lapels, a burgundy tie,
# a white pocket square and polished brown oxfords.
TEDDY = dict(h=65, sw=0.14, skin="e7c1a3", hair="9f7430", hair_style="slick", mustache=True, torso="5f6672",
             coat=dict(col="5f6672", top=0.40, hem=0.58, flare=0.0), pants="5f6672", shoes="5a3420",
             decals=[("strip", 0.212, 0.36, 0.05, 0.004, "474d58")] + _vee(0.31, 0.028, "f2ede2", "8a2632") +
             [("patch", -0.06, 0.27, "f4f0e6"), ("buttons", 0.37, 0.47, 2, "2e323a", True)])
CONCIERGE = dict(h=63, sw=0.13, skin="e0b090", hair="9a9890", hair_style="slick", mustache=True, torso="7a1f31",
                 coat=dict(col="7a1f31", top=0.40, hem=0.62, flare=0.0), pants="2a1b24", shoes="181213",
                 decals=_vee(0.32, 0.03, "f6efe2", "171717") + [("buttons", 0.35, 0.5, 3, "e8c050", True)])
BELLBOY = dict(h=56, sw=0.13, skin="ca9272", hair="3a2418", hat="pillbox", hat_col="c62924", band="f0c74b",
               torso="cf2e26", collar="cf2e26", pants="312028", shoes="181213", hipw=0.09,
               decals=[("buttons", 0.26, 0.44, 4, "f0c74b", True), ("belt", 0.455, "8a1a18")])
SAL = dict(h=70, sw=0.155, hw=0.058, waist=0.1, hipw=0.108, leg_r=1.12, skin="c99878", hair="171313", hat="cap",
           hat_col="47525c", torso="394148", coat=dict(col="394148", top=0.40, hem=0.64, flare=0.01),
           pants="26262c", shoes="141414", decals=_vee(0.29, 0.028, "b5ab97"))
BARTENDER = dict(h=64, sw=0.14, waist=0.092, hipw=0.1, skin="d7a786", hair="3a2a20", hair_style="bald",
                 mustache=True, torso="4a3434", sleeves="ebe6d8", forearm="d7a786", cuff="ebe6d8", pants="2b2424",
                 shoes="141414",
                 decals=_vee(0.30, 0.03, "ebe6d8", "2a1818") +
                 [("strip", 0.42, 0.82, 0.078, 0.098, "e7e0d0", ("torso", "hips", "leg1", "leg-1")),
                  ("belt", 0.42, "d8d0c0")])
# Sober upper-class mourning black: long-sleeved crepe dress to mid-calf, high black neckline, a single strand of pearls.
ELEANOR = dict(h=62, sw=0.112, hw=0.046, waist=0.066, hipw=0.088, leg_r=0.84, foot=0.058, skin="ecc4a2",
               hair="4a2a1c", hair_style="long", soft_face=True, lips="a83e3c", eye="3a2416", brow="2e1a12",
               torso="2c2830", coat=dict(col="2c2830", top=0.40, hem=0.84, flare=0.016), stockings="3e3434",
               shoes="141014",
               decals=[("strip", 0.235, 0.6, 0.0, 0.0, "2c2830"),
                       ("pearls", 0.232, "cfc8ba"), ("belt", 0.40, "1e1a20")])
ROSE = dict(h=60, sw=0.108, hw=0.044, waist=0.07, hipw=0.088, leg_r=0.8, foot=0.058, skin="ecc4a4", hair="c49a52",
            hair_style="bob", soft_face=True, glasses="b09a6a", lips="b06a64", torso="9a6672", abdomen="34465e", pelvis="34465e",
            coat=dict(col="34465e", top=0.40, hem=0.80, flare=0.012), stockings="c49c84", shoes="3a2620",
            decals=[("strip", 0.215, 0.235, 0.032, 0.026, "f0eadc"), ("strip", 0.235, 0.42, 0.02, 0.026, "34465e"),
                    ("buttons", 0.27, 0.38, 3, "e8dcc8")])
# Theodore Harrington Jr., Teddy's father: old money in evening dress, white wing collar and a black bow tie.
HARRINGTON = dict(h=63, sw=0.13, waist=0.09, hipw=0.096, skin="e2bca2", hair="e4e0d8", hair_style="bald", old=True,
                  eye="3a4a5a", brow="cfcac0", torso="1e1c24", collar="f2eee4",
                  coat=dict(col="1e1c24", top=0.40, hem=0.6, flare=0.0), pants="1e1c24", shoes="0e0c10",
                  decals=_vee(0.33, 0.036, "f2eee4") + [("bow", 0.205, "121016"), ("buttons", 0.25, 0.31, 2, "d8d2c4"),
                                                        ("strip", 0.34, 0.4, 0.05, 0.06, "3a3440")])
CALEB = dict(h=65, sw=0.138, skin="d2a07c", hair="2e2018", torso="38363e", collar="38363e",
             coat=dict(col="38363e", top=0.40, hem=0.95, flare=0.02), pants="26252b", shoes="1a1618",
             decals=[("strip", 0.19, 0.215, 0.009, 0.009, "f2f0ea", ("neck",)),
                     ("buttons", 0.25, 0.9, 9, "5c2a32")])
# An older, stern nun in a 1920s habit: floor-length black tunic, black veil over a white coif and wimple, a white
# guimpe over the chest and a rosary with a cross hanging from the cincture.
NUN = dict(h=61, sw=0.122, hw=0.046, waist=0.084, hipw=0.096, skin="dcb49a", hair="e8e4dc", hair_style="bald",
           old=True, soft_face=True, lips="a07468", lips_lo="8a5e54", eye="3a3a44", brow="5a4a44", hat="veil",
           hat_col="1a181e", coif="e8e4dc", torso="2a2830", sleeves="2a2830",
           coat=dict(col="2a2830", top=0.40, hem=0.97, flare=0.03), pants="2a2830", shoes="141216",
           decals=[("strip", 0.205, 0.285, 0.05, 0.072, "e6e2da"), ("strip", 0.285, 0.315, 0.072, 0.03, "e6e2da"),
                   ("belt", 0.415, "16141a"), ("rosary", 0.045, 0.43, 0.62, "6a4a34", "c8b070")])
# The old librarian: thin and a little stooped, bald on top with grey at the sides, round wire spectacles, a
# grey-brown buttoned cardigan over a white shirt with a small burgundy bow tie.
LIBRARIAN = dict(h=63, sw=0.118, hw=0.044, waist=0.07, hipw=0.082, skin="dcb496", hair="b4b0a8", hair_style="bald",
                 old=True, specs="c8b070", eye="3a3a44", brow="a8a49c", torso="6e6252", sleeves="6e6252",
                 cuff="6e6252", collar="ece8de", coat=dict(col="6e6252", top=0.40, hem=0.53, flare=0.0),
                 pants="3e3a38", shoes="2a1e18",
                 decals=_vee(0.33, 0.034, "ece8de") + [("bow", 0.205, "7a2030"),
                                                       ("buttons", 0.34, 0.51, 3, "3a3228")])
# Micah getting dressed: no hat or coat, an open white shirt with the tie hanging loose round the collar, braces
# unclipped and hanging in loops at the hips.
MICAH_DRESSING = dict(h=66, sw=0.142, skin="d8a480", hair="2a1d16", torso="e4ddcc", sleeves="e4ddcc",
                      cuff="e4ddcc", collar="ece6d6", pants="4a433b", shoes="2b1b14", top_hem=0.43,
                      decals=[("strip", 0.205, 0.29, 0.03, 0.0, "d8a480"),
                              ("ribbon", 0.03, 0.212, 0.37, 0.005, "7b1f2a"),
                              ("ribbon", -0.026, 0.212, 0.31, 0.005, "7b1f2a"),
                              ("buttons", 0.31, 0.41, 3, "b8ae9a"), ("belt", 0.43, "3a342e"),
                              ("hang", 0.44, 0.17, "6a3e22")])


def _arms(kind_r, kind_l=None):
    def one(k):
        return {"down": ("swing", 3, 6, 10), "hip": ("hip", 0, 0, 0), "pocket": ("pocket", 0, 0, 0),
                "fold": ("fold", 0, 0, 0)}[k]
    return {1: one(kind_r), -1: one(kind_l or kind_r)}


def player_sheet(spec, name):
    side = [figure(spec, pose(90), FW, FH)]
    side += [figure(spec, walk_pose(90, i), FW, FH) for i in range(STRIDE_FRAMES)]
    side += [figure(spec, pose(90, mouth=1, nod=0.004), FW, FH)]
    front = [figure(spec, pose(16), FW, FH)]
    front += [figure(spec, walk_pose(16, i * 8 / 6, amp=0.8), FW, FH) for i in range(6)]
    # talking only moves the mouth and nods the head; the arms stay where they are
    front += [figure(spec, pose(16, mouth=1), FW, FH), figure(spec, pose(16, mouth=2, nod=0.004), FW, FH)]
    back = [figure(spec, pose(164), FW, FH)]
    back += [figure(spec, walk_pose(164, i * 8 / 6, amp=0.8), FW, FH) for i in range(6)]
    img = sheet([side, front, back], FW, FH, cols=10)
    save(img, "sprites", f"{name}.png")
    return img


def npc_strip(spec, name, arms, phi=35, **extra):
    """extra: pose overrides (e.g. lean for a stoop); a "nod" here adds to the talk-frame nod."""
    nod = extra.pop("nod", 0.0)
    frames = [figure(spec, pose(phi, arms=arms, nod=nod, **extra), NPC_W, FH),
              figure(spec, pose(phi, arms=arms, mouth=1, nod=nod, **extra), NPC_W, FH),
              figure(spec, pose(phi, arms=arms, mouth=2, nod=nod + 0.004, **extra), NPC_W, FH)]
    img = sheet([frames], NPC_W, FH)
    save(img, "sprites", f"{name}.png")
    return img


NPCS = (("teddy", TEDDY, _arms("down")), ("concierge", CONCIERGE, _arms("fold")),
        ("bellboy", BELLBOY, _arms("down")), ("sal", SAL, _arms("pocket")),
        ("bartender", BARTENDER, _arms("down")), ("eleanor", ELEANOR, _arms("down")),
        ("rose", ROSE, _arms("fold")), ("caleb", CALEB, _arms("fold")),
        ("harrington", HARRINGTON, _arms("down", "pocket")), ("nun", NUN, _arms("fold")),
        ("librarian", LIBRARIAN, _arms("fold"), dict(lean=9.0, nod=0.006)))


def kneel_frame(spec, name):
    """Single 64x96 frame of a character down on hands and knees, soles' baseline shared with the player sheet."""
    img, head = _kneel(dict(spec, h=spec["h"] * SCALE), FW, FH)
    save(img, "sprites", f"{name}.png")
    return img, head


def build():
    player_sheet(MICAH, "micah")
    player_sheet(DANIEL, "daniel")
    player_sheet(MICAH_DRESSING, "micah_dressing")
    kneel_frame(MICAH, "micah_kneel")
    for name, spec, arms, *extra in NPCS:
        npc_strip(spec, name, arms, **(extra[0] if extra else {}))
