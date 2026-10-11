"""Character sprites, painted by figure.py in the manner of Fate of Atlantis-era VGA adventures.

Walkable characters (Micah, Daniel) get a 10 x 3 sheet of 64x96 frames:
  row 0  facing right           : 3/4 idle, side walk 1-8, 3/4 talk
  row 1  front 3/4 view          : idle, walk 1-6, talk A, talk B
  row 2  back 3/4 view           : idle, walk 1-6
NPCs get an 11-frame strip of 56x96 frames: idle, talk A, talk B in a 3/4 view facing screen-right, then walk 1-8 in
side view facing screen-right; scenes (and Actor.MoveTo) flip them.
"""
from .common import save
import json
from pathlib import Path
from . import common
from .figure import figure as _figure, pose, walk_pose, sheet, action_figure


def figure(spec, ps, fw, fh):
    return _figure(dict(spec, h=spec["h"] * SCALE), ps, fw, fh)

FW, FH = 64, 96
NPC_W = 56
SCALE = 1.2  # FOTA-sized: about a third of the play area tall
STRIDE_FRAMES = 8
PLAYER_IDLE_YAW = 55


def _vee(y1=0.33, w=0.034, col="e3d7bf", tie=None, top=0.215):
    d = [("strip", top, y1, w, 0.0, col)]
    if tie:
        d.append(("strip", top + 0.012, y1 - 0.01, 0.007, 0.009, tie))
    return d


MICAH = dict(h=66, sw=0.142, skin="d8a480", hair="2a1d16", hat="fedora", hat_col="5c4838", band="1a120e",
             face_w=0.050, jaw_w=0.041,
             torso="ae8848", collar="ae8848", coat=dict(col="ae8848", top=0.40, hem=0.745, flare=0.035),
             pants="4a433b", shoes="2b1b14",
             decals=_vee(0.335, 0.036, "e3d7bf", "7b1f2a") + [("belt", 0.415, "6a4e26"), ("line", 0.44, 0.74)])
DANIEL = dict(h=64, sw=0.13, skin="e0b090", hair="5a4636", torso="476d5c", collar="d8d2c2", pants="4d6288",
              face_w=0.047, jaw_w=0.037,
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
               face_w=0.046, jaw_w=0.034,
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
# The Master of Ceremonies: lodge regalia over evening dress - a sky-blue collar ribbon hanging in a V to a jewel, and
# a white lambskin apron edged in blue tied over the hips.
MOC = dict(h=65, sw=0.136, waist=0.09, hipw=0.098, skin="dcb090", hair="7a7470", hair_style="slick", old=True,
           mustache=True, eye="2a2a34", torso="17161c", collar="f2eee4",
           coat=dict(col="17161c", top=0.40, hem=0.62, flare=0.0), pants="17161c", shoes="0c0b0e",
           sleeves="17161c", cuff="f2eee4",
           decals=_vee(0.33, 0.034, "f2eee4") + [("bow", 0.205, "0e0d10"),
                                                  ("ribbon", 0.05, 0.215, 0.36, 0.008, "5a8ac8"),
                                                  ("ribbon", -0.05, 0.215, 0.36, 0.008, "5a8ac8"),
                                                  ("strip", 0.355, 0.375, 0.012, 0.012, "e0c060"),
                                                  ("strip", 0.43, 0.62, 0.085, 0.095, "f0ece2", ("torso", "hips", "coat", "leg1", "leg-1")),
                                                  ("belt", 0.43, "5a8ac8")])
# The club's bouncer: a big man in a dark three-piece suit and tie.
BRUTE = dict(h=71, sw=0.168, hw=0.06, waist=0.112, hipw=0.112, leg_r=1.14, skin="c8987a", hair="1c1814",
             hair_style="slick", torso="2a2a30", coat=dict(col="2a2a30", top=0.40, hem=0.6, flare=0.0),
             pants="2a2a30", shoes="101012", decals=_vee(0.31, 0.03, "e8e2d6", "5a1a1a"))
# Night watchman at the Harrington building's back door: peaked cap and a navy greatcoat.
WATCHMAN = dict(h=69, sw=0.16, hw=0.058, skin="c89a7c", hair="4a3a2c", hat="cap", hat_col="1e2638",
                torso="26304a", coat=dict(col="26304a", top=0.40, hem=0.66, flare=0.02), pants="1e2638", shoes="141210",
                decals=[("strip", 0.215, 0.62, 0.0, 0.008, "a88c46")])
# The club's members on the night of the rite: a white full-face mask in the shadow of a deep black cowl, the cowl
# falling into a long cloak closed over the arms down to the ankles.
MASKED_MAN = dict(h=66, sw=0.142, skin="d8a480", hair="2a1d16", hat="cowl", hat_col="16141a", mask=("full", "ece8e0"),
                  torso="16141a", collar="16141a", sleeves="16141a", cloak=dict(col="16141a", hem=0.96),
                  pants="16141a", shoes="0e0c10", decals=[])
MICAH_MASKED = dict(MASKED_MAN, decals=[("strip", 0.24, 0.27, 0.012, 0.012, "7b1f2a")])
# The women of the club: short, strapless black-fringed dresses above the knee, bare shoulders and arms, sheer
# stockings and a black domino mask.
MASKED_WOMAN = dict(h=61, sw=0.11, hw=0.045, waist=0.066, hipw=0.088, leg_r=0.84, foot=0.056, skin="ecc6a6",
                    hair="1e1610", hair_style="bob", soft_face=True, lips="a8303a", eye="2a1a14", mask=("half", "121014"),
                    torso="1a1820", sleeves="ecc6a6", neckline=0.262, coat=dict(col="1a1820", top=0.40, hem=0.66, flare=0.03),
                    stockings="c8a088", shoes="141014",
                    decals=[("pearls", 0.226, "e8e2d4"), ("belt", 0.46, "6a5a70")])
MASKED_WOMAN_B = dict(MASKED_WOMAN, hair="7a3a22", skin="e2b494", sleeves="e2b494", lips="b0384a")
# Eleanor on stage: retain the dressed variant for players who opt out of nudity.
ELEANOR_STAGE_CLOTHED = dict(MASKED_WOMAN, hair="4a2a1c", hair_style="long", skin="ecc4a2", sleeves="ecc4a2", lips="a83e3c",
                            eye="3a2416", brow="2e1a12", mask=None)
# The implied-nude variant: front locks define a subtle chest contour, one
# hand lowered over her lap, the other arm hanging at her side.
ELEANOR_STAGE = dict(MASKED_WOMAN, hair="4a2a1c", hair_style="long", skin="e4b898", sleeves="e4b898", lips="a83e3c",
                     eye="3a2416", brow="2e1a12", mask=None, torso="e4b898", pelvis="e4b898", neckline=None,
                     coat=None, stockings="e4b898", shoes="c89a7c", hair_front=0.34, hair_bulge=0.03,
                     hair_back=0.32, hair_back_width=1.12, hair_back_shade=-1,
                     front_line=(0.36, 0.53), rear=(0.04, 0.05),
                     seamless=("torso", "leg1", "leg-1"), decals=[])
# Act 3. Harrington senior at home, late: a burgundy silk dressing gown with a darker shawl collar and a gold sash.
HARRINGTON_GOWN = dict(HARRINGTON, torso="5a1e26", sleeves="5a1e26", cuff="5a1e26", collar="f2eee4",
                       coat=dict(col="5a1e26", top=0.40, hem=0.86, flare=0.02), pants="2a1a1e",
                       decals=[("strip", 0.21, 0.36, 0.05, 0.004, "3a1018"), ("belt", 0.42, "d8b860")])
# Eleanor out of Harrington's bed, wrapped in the white sheet from the armpits down, bare shoulders and arms.
ELEANOR_SHEET = dict(ELEANOR, torso="e8e4dc", sleeves="ecc4a2", neckline=0.262,
                     coat=dict(col="e8e4dc", top=0.40, hem=0.97, flare=0.03), stockings="e8e4dc", shoes="ecc4a2",
                     decals=[("strip", 0.30, 0.95, 0.01, 0.01, "c8c4bc")])
# Micah in Joliet: a faded tan prison coverall buttoned to the throat.
MICAH_INMATE = dict(h=66, sw=0.142, skin="d8a480", hair="2a1d16", torso="b8743a", collar="b8743a", sleeves="b8743a",
                    cuff="b8743a", pants="b8743a", shoes="2b1b14",
                    decals=[("buttons", 0.24, 0.42, 4, "6a4020", True), ("belt", 0.43, "9a5e2c")])


def _arms(kind_r, kind_l=None):
    def one(k):
        return {"down": ("swing", 3, 6, 10), "hip": ("hip", 0, 0, 0), "pocket": ("pocket", 0, 0, 0),
                "fold": ("fold", 0, 0, 0), "cover": ("cover", 0, 0, 0), "side": ("side", 0, 0, 0)}[k]
    return {1: one(kind_r), -1: one(kind_l or kind_r)}


def player_sheet(spec, name):
    side = [figure(spec, pose(PLAYER_IDLE_YAW), FW, FH)]
    side += [figure(spec, walk_pose(90, i), FW, FH) for i in range(STRIDE_FRAMES)]
    side += [figure(spec, pose(PLAYER_IDLE_YAW, mouth=1, nod=0.004), FW, FH)]
    front = [figure(spec, pose(16), FW, FH)]
    front += [figure(spec, walk_pose(16, i * 8 / 6, amp=0.8), FW, FH) for i in range(6)]
    # talking only moves the mouth and nods the head; the arms stay where they are
    front += [figure(spec, pose(16, mouth=1), FW, FH), figure(spec, pose(16, mouth=2, nod=0.004), FW, FH)]
    back = [figure(spec, pose(164), FW, FH)]
    back += [figure(spec, walk_pose(164, i * 8 / 6, amp=0.8), FW, FH) for i in range(6)]
    img = sheet([side, front, back], FW, FH, cols=10)
    save(img, "sprites", f"{name}.png")
    return img


def npc_walk_pose(arms, i, **extra):
    """Side-view stride frame facing screen-right. Arms the character holds still (folded, in a pocket, on the hip)
    stay put; hanging arms counter-swing like the player's."""
    p = walk_pose(90, i)
    p["arms"] = {s: (p["arms"][s] if arms[s][0] == "swing" else arms[s]) for s in (1, -1)}
    p["lean"] += extra.get("lean", 0.0)
    p["nod"] = extra.get("nod", 0.0)
    return p


def npc_strip(spec, name, arms, phi=35, **extra):
    """extra: pose overrides (e.g. lean for a stoop); a "nod" here adds to the talk-frame nod."""
    nod = extra.pop("nod", 0.0)
    frames = [figure(spec, pose(phi, arms=arms, nod=nod, **extra), NPC_W, FH),
              figure(spec, pose(phi, arms=arms, mouth=1, nod=nod, **extra), NPC_W, FH),
              figure(spec, pose(phi, arms=arms, mouth=2, nod=nod + 0.004, **extra), NPC_W, FH)]
    frames += [figure(spec, npc_walk_pose(arms, i, nod=nod, **extra), NPC_W, FH) for i in range(STRIDE_FRAMES)]
    img = sheet([frames], NPC_W, FH)
    save(img, "sprites", f"{name}.png")
    return img


NPCS = (("teddy", TEDDY, _arms("down")), ("concierge", CONCIERGE, _arms("fold")),
        ("bellboy", BELLBOY, _arms("down")), ("sal", SAL, _arms("pocket")),
        ("bartender", BARTENDER, _arms("down")), ("eleanor", ELEANOR, _arms("down")),
        ("rose", ROSE, _arms("fold")), ("caleb", CALEB, _arms("fold")),
        ("harrington", HARRINGTON, _arms("down", "pocket")), ("nun", NUN, _arms("fold")),
        ("librarian", LIBRARIAN, _arms("fold"), dict(lean=9.0, nod=0.006)),
        ("moc", MOC, _arms("fold")), ("brute", BRUTE, _arms("fold")), ("watchman", WATCHMAN, _arms("down", "pocket")),
        ("masked_man", MASKED_MAN, _arms("fold")), ("masked_woman", MASKED_WOMAN, _arms("hip", "down")),
        ("masked_woman_b", MASKED_WOMAN_B, _arms("down")), ("eleanor_stage", ELEANOR_STAGE, _arms("cover", "side")),
        ("eleanor_stage_clothed", ELEANOR_STAGE_CLOTHED, _arms("down")),
        ("harrington_gown", HARRINGTON_GOWN, _arms("down", "pocket")), ("eleanor_sheet", ELEANOR_SHEET, _arms("fold")))


def supine_frame(spec, name, wound=None):
    """Single frame of a character lying on his back on the ground, head to the left; as tall as a walk frame but wider,
    with the body resting on the row the standing figure's soles touch. wound: where along the body (0 = head, 1 = feet)
    a gunshot has soaked the clothes, with a pool of blood on the ground beneath it."""
    if wound is None:
        img, head = action_figure(dict(spec, h=spec["h"] * SCALE), REST)
        action_strip(name, [(img, head)], [1])
        return img
    from PIL import Image, ImageDraw, ImageChops
    stand = figure(spec, pose(90), FW, FH)
    a = stand.getchannel("A").point(lambda v: 255 if v >= 250 else 0)  # drop the soft ground shadow
    stand.putalpha(a)
    box = stand.getbbox()
    body = stand.crop(box).rotate(90, expand=True)
    w = max(FW, body.width + 6) + (20 if wound is not None else 0)
    img = Image.new("RGBA", (w, FH), (0, 0, 0, 0))
    x0, y0 = (w - body.width) // 2, box[3] - body.height
    if wound is not None:
        wx = x0 + int(body.width * wound)
        ImageDraw.Draw(img).ellipse([wx - 14, box[3] - 3, wx + 12, box[3] + 1], fill=(112, 14, 18, 255))
    img.alpha_composite(body, (x0, y0))
    if wound is not None:
        stain = Image.new("RGBA", body.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(stain)
        bx = int(body.width * wound)
        sd.ellipse([bx - 5, -2, bx + 5, body.height // 2], fill=(138, 18, 22, 255))
        sd.ellipse([bx - 2, 0, bx + 1, 3], fill=(176, 30, 30, 255))
        stain.putalpha(ImageChops.multiply(stain.getchannel("A"), body.getchannel("A")))
        img.alpha_composite(stain, (x0, y0))
    save(img, "sprites", f"{name}.png")
    return img


def falling_frame(spec, name):
    """Single frame of a character facing right, hit and toppling backwards, arms flung up."""
    from PIL import Image
    ps = pose(90, arms={1: ("swing", -70, 30, 20), -1: ("swing", -40, 20, 30)}, legs={1: (14, 10, 0), -1: (-6, 18, 0)},
              lean=-6.0)
    fig = figure(spec, ps, FW + 16, FH)
    fig.putalpha(fig.getchannel("A").point(lambda v: 255 if v >= 250 else 0))
    tilted = fig.rotate(24, resample=Image.NEAREST, center=(fig.width // 2, FH - 4))
    save(tilted, "sprites", f"{name}.png")
    return tilted


def seated_frame(spec, name, flip=False):
    """Single 64x96 frame of a character sitting on a chair in profile (facing right; flipped to face left), forearms
    forward as if resting on a table. The seat itself is painted into the room."""
    from PIL import ImageOps
    ps = pose(90, legs={1: (88, 92, 0), -1: (86, 90, 0)}, arms={1: ("swing", 36, 4, 70), -1: ("swing", 30, 4, 74)})
    img = figure(spec, ps, FW, FH)
    if flip:
        img = ImageOps.mirror(img)
    save(img, "sprites", f"{name}.png")
    return img


def desk_frame(spec, name, cut=0.5):
    """Head and shoulders of a character facing the camera, cut off at a fraction of the frame height: sitting behind
    a desk that hides the rest."""
    img = figure(spec, pose(16, arms=_arms("fold")), FW, FH)
    img = img.crop((0, 0, FW, int(FH * cut)))
    save(img, "sprites", f"{name}.png")
    return img

def kneel_frame(spec, name):
    """Wide articulated hands-and-knees pose sharing the action strips' planted ankle."""
    img, head = action_figure(dict(spec, h=spec["h"] * SCALE), KNEEL)
    action_strip(name, [(img, head)], [1])
    return img, head


def aim_frame(spec, name):
    """Single 96x96 frame of a character in profile facing right, revolver raised at shoulder height in a two-handed
    grip, arms out straight so the gun stands clear of the body."""
    ps = pose(90, arms={1: ("swing", 98, 2, 0), -1: ("swing", 94, -12, 4)}, gun=1,
              legs={1: (8, 4, 0), -1: (-8, 6, -4)}, lean=-2.0)
    img = figure(spec, ps, FW + 32, FH)
    action_strip(name, [(img, (FW / 2 + 16, 18))], [1], anchor=((FW + 32) / 2, FH - 3))
    return img


# Hip, shoulder, head, near knee/ankle, elbow/hand, before grounding into the wide action frame.
REST = [(66, 83), (43, 81), (29, 79), (84, 86), (104, 91), (51, 89), (66, 91)]
SIT = [(64, 83), (57, 58), (54, 43), (84, 81), (99, 91), (47, 75), (42, 91)]
CROUCH = [(64, 70), (59, 47), (57, 32), (82, 75), (84, 91), (70, 63), (78, 75)]
HALF_UP = [(64, 62), (64, 36), (64, 21), (75, 76), (78, 91), (74, 53), (77, 65)]
UPRIGHT = [(64, 56), (64, 33), (64, 18), (65, 74), (66, 91), (67, 46), (69, 59)]
KNEEL = [(60, 81), (79, 79), (85, 68), (62, 90), (41, 91), (82, 85), (88, 91)]
FALL = [UPRIGHT,
        [(64, 59), (60, 35), (57, 20), (70, 74), (74, 91), (69, 44), (78, 39)],
        [(64, 67), (53, 45), (47, 30), (75, 78), (79, 91), (48, 59), (44, 72)],
        [(65, 76), (47, 58), (37, 44), (80, 82), (90, 91), (44, 73), (40, 89)],
        [(66, 82), (44, 71), (31, 60), (83, 85), (99, 91), (42, 84), (51, 91)], REST]


def action_strip(name, frames, seconds, anchor=(96, 93)):
    """PNG plus explicit per-frame contact/head/bounds metadata shared with runtime playback."""
    import numpy as np
    images, heads = zip(*frames)
    fw, fh = images[0].size
    save(sheet([images], fw, fh), "sprites", f"{name}.png")
    data = []
    for img, head, duration in zip(images, heads, seconds, strict=True):
        ys, xs = np.nonzero(np.array(img.getchannel("A")) >= 250)
        data.append(dict(anchor=list(anchor), head=list(head), seconds=duration,
                         bounds=[int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1),
                                 int(ys.max() - ys.min() + 1)]))
    Path(common.ART, "sprites", f"{name}.json").write_text(
        json.dumps(dict(width=fw, height=fh, frames=data), indent=2) + "\n", encoding="utf-8")


def action_sequences(spec, name):
    from PIL import Image
    scaled = dict(spec, h=spec["h"] * SCALE)
    stand = Image.new("RGBA", (192, FH))
    stand.alpha_composite(figure(spec, pose(PLAYER_IDLE_YAW), FW, FH), (64, 0))
    standing = (stand, (96, 18))
    def between(a, b):
        return [tuple((x + y) / 2 for x, y in zip(p, q)) for p, q in zip(a, b)]

    def sequence(keys, end, timing):
        frames, times = [], []
        for i, (a, b) in enumerate(zip(keys, keys[1:])):
            frames.append(standing if i == 0 and keys is FALL else action_figure(scaled, a))
            frames.append(action_figure(scaled, between(a, b)))
            times += [timing[i] / 2] * 2
        return frames + [end], times + [timing[-1]]

    falling, times = sequence(FALL, action_figure(scaled, REST), [0.12, 0.12, 0.12, 0.12, 0.12, 0.22])
    action_strip(f"{name}_collapse", falling, times)
    if name == "micah":
        recovery, times = sequence([REST, SIT, CROUCH, HALF_UP, UPRIGHT], standing,
                                   [0.28, 0.3, 0.28, 0.22, 0.12])
        action_strip("micah_recover", recovery, times)
        # Retain the planted hands/feet while lifting the bowed spine, then bring one knee underneath the body.
        lifting = [(61, 73), (73, 54), (79, 44), (68, 87), (48, 91), (79, 71), (87, 88)]
        keys = [KNEEL, lifting, CROUCH, HALF_UP, UPRIGHT]
        rise, times = sequence(keys, standing, [0.22, 0.28, 0.28, 0.22, 0.12])
        action_strip("micah_kneel_rise", rise, times)


def build_drinking():
    for kind in ("cup", "drink"):
        ps = pose(90, arms={1: (kind, 0, 0, 0), -1: ("side", 0, 0, 0)}, cup=1)
        image = figure(MICAH, ps, FW, FH)
        action_strip(f"micah_{kind}", [(image, (FW / 2, 18))], [1], anchor=(FW / 2, FH - 3))


def build():
    player_sheet(MICAH, "micah")
    player_sheet(DANIEL, "daniel")
    player_sheet(MICAH_DRESSING, "micah_dressing")
    kneel_frame(MICAH, "micah_kneel")
    player_sheet(MICAH_MASKED, "micah_masked")
    supine_frame(MICAH, "micah_supine")
    aim_frame(MICAH, "micah_aim")
    action_sequences(MICAH, "micah")
    action_sequences(MICAH_MASKED, "micah_masked")
    build_drinking()
    for name, spec, arms, *extra in NPCS:
        npc_strip(spec, name, arms, **(extra[0] if extra else {}))
    build_act3()


def build_act3():
    supine_frame(SAL, "sal_supine")
    supine_frame(BARTENDER, "bartender_shot", wound=0.74)
    falling_frame(HARRINGTON_GOWN, "harrington_falling")
    supine_frame(HARRINGTON_GOWN, "harrington_shot", wound=0.44)
    desk_frame(MICAH, "micah_desk")
    seated_frame(MICAH_INMATE, "micah_inmate_seated")
    seated_frame(ELEANOR, "eleanor_seated", flip=True)
    seated_frame(CALEB, "caleb_seated", flip=True)
