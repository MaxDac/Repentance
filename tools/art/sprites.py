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
import math
from pathlib import Path
from . import common
from .figure import figure as _figure, pose, walk_pose, sheet, action_figure, grounded_joints, _walk_leg


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


# black hair, so the brown fedora stands out against it
MICAH_HEAD = dict(skin="d09670", hair="141010", hair_style="cropped", brow="100c0c", stubble="8e6c52",
                  face_w=0.050, jaw_w=0.048, chin_w=0.03, front_gaze=True, deep_eyes=True, eye_white="d4c6b2",
                  clean_jaw=True)
MICAH = dict(MICAH_HEAD, h=66, sw=0.142, hat="fedora", hat_col="6e4a30", band="1a120e",
             brim_w=0.102, brim_y=0.36, crown_h=0.04, crown_pinch=0.35,
             torso="ae8848", collar="e3d7bf", coat=dict(col="ae8848", top=0.40, hem=0.745, flare=0.035),
             pants="4a433b", shoes="2b1b14",
             decals=_vee(0.335, 0.036, "e3d7bf", "7b1f2a") + [("knot", 0.205, "7b1f2a", "a8384a"),
                                                                ("belt", 0.415, "6a4e26"), ("line", 0.44, 0.74)])
# Micah after the mansion's alarm bell, his tie left knotted round its hammer: the same coat and hat, the shirt collar
# open at the throat with the top button undone.
MICAH_NO_TIE = dict(MICAH, open_collar=True, decals=_vee(0.335, 0.036, "e3d7bf") + [("strip", 0.205, 0.27, 0.022, 0.0, "c88c66"),
                                                                  ("belt", 0.415, "6a4e26"), ("line", 0.44, 0.74)])
# Micah in the storm-dark office after the alley: his fedora left on the desk, the whiskey bottle in his hand.
MICAH_HATLESS = dict(MICAH, hat=None)
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
# Eleanor's head as first drawn: long wavy brown hair and her soft face. Every Eleanor shares it and her slender
# figure: narrow sloping shoulders, slim arms, a bust and a small waist curving out to the hips and seat. Her mane is
# trimmed at the back (its front edge beside the neck kept) and falls past her shoulder blades.
ELEANOR_HEAD = dict(skin="ecc4a2", face_w=0.056, jaw_w=0.044, hair_vol=1.6, hair_side=0.85, hair_back_width=1.0,
                    hair_back_trim=0.82, hair_back=0.40, hair_unified=True, hair_loose=True,
                    fringe=0.3, front_gaze=True, full_jaw=True, small_lips=True, eye_white="f4eee6", chin_cut=1, level_eyes=True,
                    hair="4a2a1c", hair_style="long", soft_face=True, lips="a8504a", eye="2a1810", brow="2e1a12")
# In profile her torso is slim and flat: a near-straight back from nape to waist, the front straight down from the
# neck to a small bust, a thin neck column rising a little forward. Levels: (y, half-width, back z, front z).
ELEANOR_FIGURE = dict(h=62, sw=0.1, hw=0.044, waist=0.054, hipw=0.09, leg_r=0.78, foot=0.056, arm_r=0.64, cap_r=0.6,
                      cap_y=0.258, shoulder_y=0.262, bust=0.062, bust_y=0.295, waist_z=0.038,
                      bust_peak=((-1, 0), (0, 1), (1, 1), (2, 0)),  # a one-pixel swell blending into the chest line
                      rear=(0.035, 0.058, 0.52), fitted=True, neck_r=0.022, neck_lean=0.005, talk_nod=0.0,
                      profile=[(0.19, 0.03, -0.02, 0.016), (0.212, 0.055, -0.029, 0.029), (0.232, 0.085, -0.036, 0.04),
                               (0.25, 0.1, -0.048, 0.059), (0.31, 0.095, -0.052, 0.07), (0.40, 0.054, -0.048, 0.059),
                               (0.47, 0.09, -0.07, 0.046), (0.53, 0.0774, -0.06, 0.044)], flat_front=True)
# A 1920s widow's black: the high-necked, long-sleeved black bodice of her portrait, a dropped waist with a sash at
# the hip, a pleated skirt to mid-calf, sheer dark stockings, black heels and a short strand of white pearls.
# Her outfits keep these curves; the black dress, of heavier cloth, softens bust and seat a little.
_CURVES = dict(bust_hi=0, bust=ELEANOR_FIGURE["bust"], rear=ELEANOR_FIGURE["rear"])
ELEANOR = {**ELEANOR_FIGURE, **ELEANOR_HEAD, "bust": 0.052, "bust_hi": 2, "rear": (0.035, 0.044, 0.52), "torso": "1c1a20",
           "high_neck": 0.19, "coat": dict(col="1c1a20", top=0.46, hem=0.79, flare=0.034), "stockings": "5e4a46", "shoes": "120e10",
           "decals": [("belt", 0.465, "4a3c48"), ("ribbon", 0.05, 0.465, 0.56, 0.008, "4a3c48"), ("pleats", 0.53),
                      ("strand", 0.212, 0.25, 0.036, "f2eee4", "b8b0a4", 0.058)]}
# Rose, as in her close-up: long wavy blonde hair over the shoulders, blue-green eyes, a cream knit cardigan open
# over a white collared blouse, and her navy skirt.
ROSE = dict(h=60, sw=0.108, hw=0.044, waist=0.07, hipw=0.088, leg_r=0.8, foot=0.058, skin="ecc4a4", hair="c89c4a",
            face_w=0.056, jaw_w=0.044, chin_cut=1, hair_style="long", hair_vol=1.6, hair_side=0.85, hair_back_width=0.85,
            hair_front=0.22, soft_face=True, eye="2e6a70", brow="7a5a34", lips="b06a64",
            torso="d8d0bc", sleeves="d8d0bc", abdomen="d8d0bc", pelvis="34465e",
            coat=dict(col="34465e", top=0.40, hem=0.80, flare=0.012), stockings="c49c84", shoes="3a2620",
            decals=[("strip", 0.205, 0.40, 0.026, 0.018, "f2eee4"), ("strip", 0.205, 0.235, 0.036, 0.03, "fbf8f0"),
                    ("ribbon", 0.024, 0.25, 0.40, 0.005, "a8a090"), ("ribbon", -0.024, 0.25, 0.40, 0.005, "a8a090")])
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
           decals=[("strip", 0.205, 0.285, 0.05, 0.072, "e8e4dc", "flat"),
                   ("strip", 0.285, 0.315, 0.072, 0.03, "e8e4dc", "flat"),
                   ("belt", 0.415, "16141a"), ("rosary", 0.045, 0.43, 0.62, "6a4a34", "c8b070")])
# The old librarian: thin and a little stooped, bald on top with grey at the sides, round wire spectacles, a
# grey-brown buttoned cardigan over a white shirt with a small burgundy bow tie.
LIBRARIAN = dict(h=63, sw=0.118, hw=0.044, waist=0.07, hipw=0.082, skin="dcb496", hair="b4b0a8", hair_style="bald",
                 old=True, specs="c8b070", eye="3a3a44", brow="a8a49c", torso="6e6252", sleeves="6e6252",
                 cuff="6e6252", collar="ece8de", coat=dict(col="6e6252", top=0.40, hem=0.53, flare=0.0),
                 pants="3e3a38", shoes="2a1e18",
                 decals=_vee(0.33, 0.034, "ece8de") + [("bow", 0.205, "7a2030"),
                                                       ("buttons", 0.34, 0.51, 3, "3a3228")])
# The motel night clerk: fifty and soft round the middle, a few mousy strands combed over a bald crown under a
# green celluloid eyeshade, a sweat-yellowed shirt with sleeve garters, an open brown vest and a loosened tie.
CLERK = dict(h=63, sw=0.13, waist=0.104, hipw=0.104, skin="d2a684", hair="6e604e", hair_style="bald",
             combover="6e604e", old=True, eye="2e2a22", brow="5e5040", hat="visor", hat_col="4e9a62",
             band="2a3a2c", torso="5c4a32", sleeves="d6cca6", cuff="d6cca6", collar="d6cca6", garter="8a2a2a",
             pants="4a4642", shoes="2a1e16",
             decals=[("strip", 0.205, 0.45, 0.034, 0.05, "d6cca6"), ("strip", 0.205, 0.235, 0.044, 0.03, "e2dabc"),
                     ("ribbon", 0.012, 0.222, 0.40, 0.007, "6a2c22"), ("patch", 0.03, 0.33, "b8a87c"),
                     ("belt", 0.45, "2a2018")])
# Micah getting dressed: no hat or coat, an open white shirt with the tie hanging loose round the collar, braces
# unclipped and hanging in loops at the hips.
MICAH_DRESSING = dict(MICAH_HEAD, h=66, sw=0.142, torso="e4ddcc", sleeves="e4ddcc",
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
# The club's members on the night of the rite: a white Venetian Bauta half-mask (heavy brow, eye holes and a long
# nose; the mouth and chin bare and overshadowed) in the shadow of a deep black cowl, the cowl
# falling into a long cloak closed over the arms down to the ankles.
MASKED_MAN = dict(h=66, sw=0.142, skin="d8a480", hair="2a1d16", hat="cowl", hat_col="16141a", mask=("bauta", "ece6d4"),
                  torso="16141a", collar="16141a", sleeves="16141a", cloak=dict(col="16141a", hem=0.96),
                  pants="16141a", shoes="0e0c10", decals=[])
MICAH_MASKED = dict(MASKED_MAN, decals=[("strip", 0.24, 0.27, 0.012, 0.012, "7b1f2a")])
# The inner circle and some of the members wear carved beasts' faces instead of the white mask, after the animals
# of Celtic folklore: aged wood and bone, antler-grey and ochre against the black cowl. The stag, horned like
# Cernunnos, leads the rite; the boar and the wolf stand with him. Bear, raven and hare walk among the guests.
MASKED_STAG = dict(MASKED_MAN, mask=("animal", "stag", "c4a676", "d4cab4"))
MASKED_BOAR = dict(MASKED_MAN, h=65, sw=0.152, waist=0.1, hipw=0.104, mask=("animal", "boar", "8a6440", "4e3624"))
MASKED_WOLF = dict(MASKED_MAN, h=67, sw=0.138, mask=("animal", "wolf", "a29a8a", "4a423c"))
MASKED_BEAR = dict(MASKED_MAN, h=68, sw=0.158, hw=0.058, waist=0.104, hipw=0.106, mask=("animal", "bear", "9a7048", "3a2a20"))
MASKED_RAVEN = dict(MASKED_MAN, h=65, mask=("animal", "raven", "b0a898", "6a5e58"))
MASKED_HARE = dict(MASKED_MAN, h=64, sw=0.134, mask=("animal", "hare", "ccae7e", "8a6448"))
# Act 3: the stag unmasks. Harrington senior's own old face, the cowl pushed back onto his shoulders and the stag's
# carved face held against his chest.
LEADER_UNMASKED = dict(MASKED_STAG, skin=HARRINGTON["skin"], hair=HARRINGTON["hair"], hair_style="bald", old=True,
                       eye=HARRINGTON["eye"], brow=HARRINGTON["brow"], mask=None, hat="cowl_down",
                       held_mask=(1, "c4a676", "d4cab4"))
# The women of the club: short, strapless black-fringed dresses above the knee, bare shoulders and arms, sheer
# stockings and a black domino mask.
MASKED_WOMAN = dict(h=61, sw=0.11, hw=0.045, waist=0.066, hipw=0.088, leg_r=0.84, foot=0.056, skin="ecc6a6",
                    hair="1e1610", hair_style="bob", soft_face=True, lips="a8303a", eye="2a1a14", mask=("half", "121014"),
                    torso="1a1820", sleeves="ecc6a6", neckline=0.262, coat=dict(col="1a1820", top=0.40, hem=0.66, flare=0.03),
                    stockings="c8a088", shoes="141014",
                    decals=[("pearls", 0.226, "e8e2d4"), ("belt", 0.46, "6a5a70")])
MASKED_WOMAN_B = dict(MASKED_WOMAN, hair="7a3a22", skin="e2b494", sleeves="e2b494", lips="b0384a")
# Eleanor on stage: retain the dressed variant for players who opt out of nudity, in the close-up panel's red dress.
# Both variants wear her hair the same way: long, with thin locks falling in front over her chest, as in the close-up.
_STAGE_HEAD = dict(full_jaw=True, hair="4a2a1c", hair_style="long", lips="a83e3c", eye="3a2416", brow="2e1a12", mask=None)
_STAGE_HAIR = dict(hair_front=0.34, hair_bulge=0.0, hair_front_w=0.7,
                   hair_front_root=0.07,  # the lock joins the hair behind the neck in profile
                   hair_back=0.40, hair_back_width=1.12, hair_back_trim=0.72, hair_unified=True)
ELEANOR_STAGE_CLOTHED = {**MASKED_WOMAN, **ELEANOR_FIGURE, **_STAGE_HEAD, **_STAGE_HAIR, "h": MASKED_WOMAN["h"],
                         "skin": "ecc4a2", "sleeves": "ecc4a2", "torso": "781f27",
                         "coat": dict(MASKED_WOMAN["coat"], col="781f27"),
                         "decals": [("pearls", 0.226, "e8e2d4"), ("belt", 0.46, "4a1016")]}
# The implied-nude variant: the locks lie flat over the chest, one hand lowered over her lap, the other arm hanging
# at her side.
_SKIN = "e4b898"
ELEANOR_STAGE = {**MASKED_WOMAN, **ELEANOR_FIGURE, **_STAGE_HEAD, **_STAGE_HAIR, "h": MASKED_WOMAN["h"], "skin": _SKIN,
                 "sleeves": _SKIN, "torso": _SKIN, "pelvis": _SKIN, "neckline": None,
                 "coat": None, "stockings": _SKIN, "shoes": "c89a7c",
                 "front_line": (0.36, 0.53), "seamless": ("torso", "leg1", "leg-1"), "decals": []}
# Act 3. Harrington senior at home, late: a burgundy silk dressing gown with a darker shawl collar and a gold sash.
HARRINGTON_GOWN = dict(HARRINGTON, torso="5a1e26", sleeves="5a1e26", cuff="5a1e26", collar="f2eee4",
                       coat=dict(col="5a1e26", top=0.40, hem=0.86, flare=0.02), pants="2a1a1e",
                       decals=[("strip", 0.21, 0.36, 0.05, 0.004, "3a1018"), ("belt", 0.42, "d8b860")])
# Sitting up in bed (mansion and motel) she keeps her earlier upper body: a longer bare neck and the fuller bust.
SHEET_BODY = dict(bust_hi=0, profile=None, neck_r=0.029, neck_lean=0.0, neck_drop=0.026, bust=0.078, bust_y=0.33, rear=(0.035, 0.058, 0.52))
# Eleanor out of Harrington's bed, wrapped in the white sheet from the armpits down, bare shoulders and arms.
ELEANOR_SHEET = dict(ELEANOR, **_CURVES, torso="e8e4dc", sleeves=ELEANOR["skin"], neckline=0.262, collar=None,
                     coat=dict(col="e8e4dc", top=0.40, hem=0.97, flare=0.03), stockings="e8e4dc", shoes="ecc4a2",
                     decals=[("strip", 0.30, 0.95, 0.01, 0.01, "c8c4bc")])
# Micah in Joliet: a faded tan prison coverall buttoned to the throat.
MICAH_INMATE = dict(MICAH_HEAD, h=66, sw=0.142, torso="b8743a", collar="b8743a", sleeves="b8743a",
                    cuff="b8743a", pants="b8743a", shoes="2b1b14",
                    decals=[("buttons", 0.24, 0.42, 4, "6a4020", True), ("belt", 0.43, "9a5e2c")])
# Eleanor at the club before she goes on: a short pink silk gown above the knee, bare shoulders, her pearls. The silk
# lies a little flatter over the seat than her bare curves.
ELEANOR_GOWN = dict(ELEANOR, **dict(_CURVES, rear=(0.035, 0.051, 0.52)), torso="e08ca4", sleeves=ELEANOR["skin"], neckline=0.262, collar=None,
                    far_arm_behind=True,
                    coat=dict(col="e08ca4", top=0.40, hem=0.66, flare=0.03, hem_legs=True, hem_pad=0.025),
                    stockings="e4c4ae", shoes="7a3448",
                    decals=[("pearls", 0.226, "e8e2d4"), ("belt", 0.42, "b85a78")])
# Eleanor in Joliet: a grey prison jumpsuit buttoned to the throat, cut like Micah's coverall.
ELEANOR_INMATE = dict(ELEANOR, **_CURVES, high_neck=None, torso="8a8c90", collar="8a8c90", sleeves="8a8c90", cuff="8a8c90", pants="8a8c90",
                      coat=None, stockings=None, shoes="2a2a2e",
                      decals=[("buttons", 0.24, 0.42, 4, "4a4c50", True), ("belt", 0.42, "6e7074")])


# Eleanor's night things at the convent, from her duffle: pale ivory cotton pyjamas, long sleeves and trousers, buttons
# and cuffs piped dark, bare feet, her hair down.
PYJAMA = "e8e0cc"
ELEANOR_PYJAMA = dict(ELEANOR, **_CURVES, high_neck=None, torso=PYJAMA, collar=None, sleeves=PYJAMA, cuff="3a3040",
                      pants=PYJAMA, coat=None, stockings=None, shoes=ELEANOR["skin"],
                      # loose cotton: a one-pixel swell spread over more rows, set a little higher; the open neck
                      # shows her throat; the waist curves in and out to fuller hips and seat
                      bust_peak=((-3, 0), (-2, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 0), (4, 0)), bust_y=0.278,
                      neckline=0.23, hipw=0.1,
                      profile=ELEANOR_FIGURE["profile"][:5] + [(0.40, 0.05, -0.036, 0.048), (0.47, 0.098, -0.09, 0.05),
                                                               (0.53, 0.086, -0.082, 0.046)],
                      decals=_vee(0.29, 0.03, ELEANOR["skin"], top=0.22) + [("buttons", 0.30, 0.45, 3, "3a3040", True)])


def _fuller(spec, k=1.1):
    """Eleanor in her NPC, action and seated strips: hips, seat and stance a tenth fuller, and any skirt following
    her legs to the hem rather than hanging from the hip width. Her player sheets keep the base specs."""
    rear = spec["rear"]
    out = dict(spec, hw=spec["hw"] * k, hipw=spec["hipw"] * k, rear=(rear[0] * k, rear[1] * k) + tuple(rear[2:]),
               profile=[(y, w * (k if y > 0.45 else 1), zb, zf) for y, w, zb, zf in spec["profile"]])
    if spec.get("coat"):
        out["coat"] = dict(spec["coat"], hem_legs=True, hem_pad=0.025)
    return out


ELEANOR_NPC, ELEANOR_SHEET_NPC, ELEANOR_GOWN_NPC, ELEANOR_INMATE_NPC, ELEANOR_PYJAMA_NPC = map(
    _fuller, (ELEANOR, ELEANOR_SHEET, ELEANOR_GOWN, ELEANOR_INMATE, ELEANOR_PYJAMA))
# A second Order heavy: the bouncer's build in a brown suit, ginger-haired and fairer.
GOON = dict(BRUTE, skin="dcae90", hair="8a4a24", torso="4a3a2c", coat=dict(BRUTE["coat"], col="4a3a2c"),
            pants="4a3a2c", shoes="1a1410", decals=_vee(0.31, 0.03, "e2dccc", "1e3450"))


def _arms(kind_r, kind_l=None):
    def one(k):
        return {"down": ("swing", 3, 6, 10), "hip": ("hip", 0, 0, 0), "pocket": ("pocket", 0, 0, 0),
                "fold": ("fold", 0, 0, 0), "cover": ("cover", 0, 0, 0), "side": ("side", 0, 0, 0),
                "clutch": ("clutch", 0, 0, 0)}[k]
    return {1: one(kind_r), -1: one(kind_l or kind_r)}


def player_sheet(spec, name, arms=None, props=None):
    """arms: arms held still in every frame (e.g. both hands clutching a sheet) instead of the walk's swing.
    props: pose keys added to every frame (e.g. a bottle carried in one hand)."""
    def held(ps):
        if arms:
            ps["arms"] = {k: (ps["arms"][k] if arms[k][0] == "swing" else arms[k]) for k in (1, -1)}
        ps.update(props or {})
        return ps
    nod = spec.get("talk_nod", 0.004)  # how far the head dips on a talk frame
    side = [figure(spec, held(pose(PLAYER_IDLE_YAW)), FW, FH)]
    side += [figure(spec, held(walk_pose(90, i)), FW, FH) for i in range(STRIDE_FRAMES)]
    side += [figure(spec, held(pose(PLAYER_IDLE_YAW, mouth=1, nod=nod)), FW, FH)]
    front = [figure(spec, held(pose(16)), FW, FH)]
    front += [figure(spec, held(walk_pose(16, i * 8 / 6, amp=0.8)), FW, FH) for i in range(6)]
    # talking only moves the mouth and nods the head; the arms stay where they are
    front += [figure(spec, held(pose(16, mouth=1)), FW, FH), figure(spec, held(pose(16, mouth=2, nod=nod)), FW, FH)]
    back = [figure(spec, held(pose(164)), FW, FH)]
    back += [figure(spec, held(walk_pose(164, i * 8 / 6, amp=0.8)), FW, FH) for i in range(6)]
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
              figure(spec, pose(phi, arms=arms, mouth=2, nod=nod + spec.get("talk_nod", 0.004), **extra), NPC_W, FH)]
    frames += [figure(spec, npc_walk_pose(arms, i, nod=nod, **extra), NPC_W, FH) for i in range(STRIDE_FRAMES)]
    img = sheet([frames], NPC_W, FH)
    save(img, "sprites", f"{name}.png")
    return img


NPCS = (("teddy", TEDDY, _arms("down")), ("concierge", CONCIERGE, _arms("fold")),
        ("bellboy", BELLBOY, _arms("down")), ("sal", SAL, _arms("pocket")),
        ("bartender", BARTENDER, _arms("down")), ("eleanor", ELEANOR_NPC, _arms("down")),
        ("rose", ROSE, _arms("fold")), ("caleb", CALEB, _arms("fold")),
        ("harrington", HARRINGTON, _arms("down", "pocket")), ("nun", NUN, _arms("fold")),
        ("librarian", LIBRARIAN, _arms("fold"), dict(lean=9.0, nod=0.006)),
        ("moc", MOC, _arms("fold")), ("brute", BRUTE, _arms("fold")), ("watchman", WATCHMAN, _arms("down", "pocket")),
        ("masked_man", MASKED_MAN, _arms("fold")), ("masked_woman", MASKED_WOMAN, _arms("hip", "down")),
        ("masked_stag", MASKED_STAG, _arms("fold")), ("masked_boar", MASKED_BOAR, _arms("fold")),
        ("masked_wolf", MASKED_WOLF, _arms("fold")), ("masked_bear", MASKED_BEAR, _arms("fold")),
        ("masked_raven", MASKED_RAVEN, _arms("fold")), ("masked_hare", MASKED_HARE, _arms("fold")),
        ("leader_unmasked", LEADER_UNMASKED, _arms("fold")),
        ("masked_woman_b", MASKED_WOMAN_B, _arms("down")), ("eleanor_stage", ELEANOR_STAGE, _arms("cover", "side")),
        ("eleanor_stage_clothed", ELEANOR_STAGE_CLOTHED, _arms("down")),
        ("harrington_gown", HARRINGTON_GOWN, _arms("down", "pocket")), ("eleanor_sheet", ELEANOR_SHEET_NPC, _arms("clutch")),
        ("goon", GOON, _arms("fold")), ("clerk", CLERK, _arms("down"), dict(lean=4.0, nod=0.004)))


def supine_frame(spec, name, wound=None):
    """Single frame of a character lying on his back on the ground, head to the left; as tall as a walk frame but wider,
    with the body resting on the row the standing figure's soles touch. wound: where along the body (0 = head, 1 = feet)
    a gunshot has soaked the clothes, with a pool of blood on the ground beneath it."""
    img, head = action_figure(dict(spec, h=spec["h"] * SCALE), REST)
    from PIL import Image, ImageDraw, ImageChops
    if wound is not None:
        stain = Image.new("RGBA", img.size)
        sd = ImageDraw.Draw(stain)
        bx = round(head[0] + (98 - head[0]) * wound)
        sd.ellipse([bx - 5, 79, bx + 5, 86], fill=(138, 18, 22, 255))
        stain.putalpha(ImageChops.multiply(stain.getchannel("A"), img.getchannel("A")))
        img.alpha_composite(stain)
    action_strip(name, [(img, head)], [1])
    return img


def door_strip(spec, name, yaw):
    """Reach for a knob, pull, and settle. The near arm (screen-right) does the work; facing left flips it."""
    fw = FW + 28
    poses = (
        pose(yaw),
        pose(yaw, arms={-1: ("swing", 78, 6, 4), 1: ("swing", 6, 6, 14)}, lean=5.0),
        pose(yaw, arms={-1: ("swing", 34, 2, 36), 1: ("swing", 4, 6, 16)}, lean=8.0, shift=0.01),
        pose(yaw),
    )
    frames = [(figure(spec, ps, fw, FH), (fw / 2, 18)) for ps in poses]
    action_strip(name, frames, [0.16, 0.22, 0.28, 0.16], anchor=(fw / 2, FH - 3))
    return frames


def npc_standing(spec, arms):
    """An NPC's idle strip frame centred in a wide action frame, so an action strip starts without a pose jump."""
    from PIL import Image
    standing = Image.new("RGBA", (192, FH))
    standing.alpha_composite(figure(spec, pose(35, arms=arms), NPC_W, FH), ((192 - NPC_W) // 2, 0))
    return standing, (96, 18)


def fall_strip(spec, name, final_name, arms, wound=False):
    """Drop onto both knees, pitch forward, and settle face-down; the last frame is also saved alone as final_name,
    the texture held afterwards, so there's no jump at the end. wound: shot in the stomach, the clothes soaked from
    the first kneeling frame on and a pool of blood spreading on the ground under the body at the end."""
    from PIL import Image, ImageDraw, ImageChops
    scaled = dict(spec, h=spec["h"] * SCALE)
    frames = [npc_standing(spec, arms)]
    for i, joints in enumerate(KNEES_PRONE):
        img, head = action_figure(scaled, joints)
        if wound:
            hip, shoulder = grounded_joints(joints)[:2]
            wx, wy = hip + (shoulder - hip) * 0.45
            r = (3, 4.5, 5.5)[min(i, 2)]
            stain = Image.new("RGBA", img.size)
            sd = ImageDraw.Draw(stain)
            sd.ellipse([wx - r, wy - r * 0.9, wx + r, wy + r * 0.9], fill=(138, 18, 22, 255))
            if i == len(KNEES_PRONE) - 1:
                # face-down, the soaked patch runs down the sheet and straight into the pool on the floor
                sd.polygon([(wx - r, wy), (wx + r, wy), (wx + r + 3, 93), (wx - r - 4, 93)], fill=(138, 18, 22, 255))
            stain.putalpha(ImageChops.multiply(stain.getchannel("A"), img.getchannel("A")))
            img.alpha_composite(stain)
        frames.append((img, head))
    if wound:
        down, head = frames[-1]
        hip, shoulder = grounded_joints(KNEES_PRONE[-1])[:2]
        wx = (hip + (shoulder - hip) * 0.45)[0]
        pool = Image.new("RGBA", down.size)
        ImageDraw.Draw(pool).ellipse([wx - 11, 87, wx + 10, 93], fill=(104, 12, 16, 255))
        pool.alpha_composite(down)
        # seeping out from under the hem onto the floor, so it shows even where a sheet hangs to the ground
        seep = Image.new("RGBA", down.size)
        ImageDraw.Draw(seep).ellipse([wx - 10, 90, wx + 9, 94], fill=(104, 12, 16, 255))
        pool.alpha_composite(seep)
        frames[-1] = (pool, head)
    action_strip(name, frames, [0.12, 0.35, 0.18, 0.3])
    action_strip(final_name, [frames[-1]], [1])
    return frames


def shoulder_shot_strip(spec, name, final_name, arms):
    """Shot in the near shoulder while facing right: the hit snaps him back with both hands clutching it, the legs
    give way straight down under him, he sits down hard and goes over onto his back. Blood soaks the shoulder from the
    hit on, and pools on the ground under it once he's down. The last frame is saved alone as final_name."""
    from PIL import Image, ImageDraw, ImageChops
    scaled = dict(spec, h=spec["h"] * SCALE)
    frames = [npc_standing(spec, arms)]
    for joints in SHOULDER_SHOT:
        img, head = action_figure(scaled, joints)
        hip, shoulder = grounded_joints(joints)[:2]
        # the wound sits just below the shoulder joint, towards the hip
        wx, wy = shoulder + (hip - shoulder) * 0.1
        stain = Image.new("RGBA", img.size)
        ImageDraw.Draw(stain).ellipse([wx - 3, wy - 3, wx + 3, wy + 3], fill=(138, 18, 22, 255))
        stain.putalpha(ImageChops.multiply(stain.getchannel("A"), img.getchannel("A")))
        img.alpha_composite(stain)
        frames.append((img, head))
    down, head = frames[-1]
    pool = Image.new("RGBA", down.size)
    wx = grounded_joints(SHOULDER_SHOT[-1])[1][0] + 2
    ImageDraw.Draw(pool).ellipse([wx - 8, 88, wx + 7, 93], fill=(104, 12, 16, 255))
    pool.alpha_composite(down)
    frames[-1] = (pool, head)
    action_strip(name, frames, [0.1, 0.24, 0.16, 0.2, 0.3])
    action_strip(final_name, [frames[-1]], [1])
    return frames


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


def kneel_frame(spec, name):
    """Wide articulated hands-and-knees pose sharing the action strips' planted ankle."""
    img, head = kneeling_figure(dict(spec, h=spec["h"] * SCALE), KNEEL)
    action_strip(name, [(img, head)], [1])
    return img, head


def kneeling_figure(spec, joints):
    """Action figure whose shirt front and tie are tucked out of sight while the trunk is bent over the floor, so they
    don't read as a red streak along the side of the coat."""
    hip, shoulder = joints[0], joints[1]
    dx, dy = shoulder[0] - hip[0], shoulder[1] - hip[1]
    down = -dy < 0.55 * math.hypot(dx, dy)
    return action_figure(spec, joints, chest_down=down, toes_tucked=down)


# Sal's kick, standing behind a kneeling man and half turned to the screen, facing right (the alley flips him so the
# kicking leg is his right): (yaw, legs, lean) after his idle frame. He draws the leg back, drives the toe forward and
# down into the man's belly (the man's body hides the foot), then lets the leg drop back. Hands stay in his pockets.
SAL_KICK = [
    (30, {1: (2, 4, 0), -1: (-28, 50, -20)}, 4.0),
    (30, {1: (4, 6, 0), -1: (50, 22, 4)}, -8.0),
    (30, {1: (4, 6, 0), -1: (14, 30, -4)}, -3.0),
]
# Micah on his knees taking the kick: the back hunches up, the head tucks in and the near hand comes off the cobbles
# to clutch his stomach, then he sags back down onto his forearms.
KICKED = [
    [(57, 66), (76, 66), (81, 77), (61, 88), (41, 85), (77, 79), (70, 82)],
    [(59, 70), (80, 73), (89, 75), (61, 88), (41, 85), (82, 87), (90, 90)],
]


def kick_strip(spec, name, arms):
    """An NPC's kick, from and back to the idle frame (so the strip starts and ends without a pose jump). The frame
    after the idle one is the wind-up and the next is the strike; the scene times the victim's reaction to it."""
    from PIL import Image
    standing = npc_standing(spec, arms)
    frames = [standing]
    for phi, legs, lean in SAL_KICK:
        img = Image.new("RGBA", (192, FH))
        img.alpha_composite(figure(spec, pose(phi, arms=arms, legs=legs, lean=lean), 96, FH), (48, 0))
        frames.append((img, (96, 18)))
    frames.append(standing)
    action_strip(name, frames, [0.2, 0.25, 0.25, 0.2, 0.2])
    return frames


def kicked_strip(spec, name):
    """Micah on his hands and knees doubling up under a kick, ending back on the kneeling frame."""
    scaled = dict(spec, h=spec["h"] * SCALE)
    frames = [kneeling_figure(scaled, joints) for joints in KICKED] + [kneeling_figure(scaled, KNEEL)]
    action_strip(name, frames, [0.3, 0.3, 0.2])
    return frames


def aim_frame(spec, name):
    """Single 96x96 frame of a character in profile facing right, revolver held out one-handed the old-picture way:
    upper arm tucked against the side, forearm level at the target, the free hand hanging."""
    img = figure(spec, _aim_angle_pose(AIM_LEVELS[0]), FW + 32, FH)
    action_strip(name, [(img, (FW / 2 + 16, 18))], [1], anchor=((FW + 32) / 2, FH - 3))
    return img


# The stance shared by the aim and the draw, and the hanging free arm.
AIM_LEGS = {1: (8, 4, 0), -1: (-8, 6, -4)}
AIM_OFF_ARM = ("swing", -2, 4, 12)


def _aim_pose(upper, elbow):
    return pose(90, arms={1: ("swing", upper, 2, elbow), -1: AIM_OFF_ARM}, gun=1, legs=AIM_LEGS, lean=-2.0)


# Forearm angles from straight down (0) to level (90): the aim tips the muzzle a little up, the last level hangs.
AIM_LEVELS = [94, 80, 66, 52, 38, 24, 8]
AIM_BACK_FRAMES = 8
AIM_UPPER = 16  # how far forward of the side the upper arm sits while aiming


def _aim_angle_pose(a, legs=None):
    # the elbow comes away from the side only as far as the forearm is raised
    upper = AIM_UPPER * (a - AIM_LEVELS[-1]) / (AIM_LEVELS[0] - AIM_LEVELS[-1])
    ps = _aim_pose(upper, a - upper)
    if legs is not None:
        ps = dict(ps, legs=legs)
    return ps


def _aim_level_pose(i, legs=None):
    return _aim_angle_pose(AIM_LEVELS[i], legs)


def aim_lower_strip(spec, name):
    """The aim, lowered a little at a time until the revolver hangs at the side: frame 0 matches aim_frame, and the
    story steps through the rest (one frame per verse of the prayer), so each frame is held, not played."""
    fw = FW + 32
    frames = [(figure(spec, _aim_level_pose(i), fw, FH), (FW / 2 + 16, 18)) for i in range(len(AIM_LEVELS))]
    action_strip(name, frames, [1] * len(frames), anchor=(fw / 2, FH - 3))
    return frames


def aim_back_strip(spec, name):
    """One step backwards for each verse of the prayer, still facing right, lowering the gun on the way: run i (frames
    i * AIM_BACK_FRAMES onward) takes the arm from aim_lower_strip's level i - 1 down to level i a little each frame.
    Frame 0 of each run is level i - 1's held aim; the rest play the walk cycle in reverse, short (the legs swing
    about as far as the aim stance's), so the feet travel back under him over the ~18px he retreats per verse. Run 0
    holds level 0 throughout."""
    fw = FW + 32
    frames = []
    for i in range(len(AIM_LEVELS)):
        a0, a1 = AIM_LEVELS[max(i - 1, 0)], AIM_LEVELS[i]
        frames.append((figure(spec, _aim_angle_pose(a0), fw, FH), (FW / 2 + 16, 18)))
        for k in range(1, AIM_BACK_FRAMES):
            phase = (AIM_BACK_FRAMES - k) * 8 / AIM_BACK_FRAMES
            legs = {}
            for s, offset in ((1, 0), (-1, 4)):
                thigh, knee, foot = _walk_leg(phase + offset)
                legs[s] = (thigh * 0.32, knee * 0.7, foot * 0.5)
            a = a0 + (a1 - a0) * k / (AIM_BACK_FRAMES - 1)
            frames.append((figure(spec, _aim_angle_pose(a, legs), fw, FH), (FW / 2 + 16, 18)))
    action_strip(name, frames, [1] * len(frames), anchor=(fw / 2, FH - 3))
    return frames


def aim_self_frame(spec, name):
    """Single frame in profile facing right: the revolver held to his own temple, elbow up and out in front."""
    ps = pose(90, arms={1: ("temple", 0, 0, 0), -1: ("swing", 2, 6, 8)}, gun=1,
              legs={1: (4, 3, 0), -1: (-4, 6, -4)}, nod=0.008)
    img = figure(spec, ps, FW + 32, FH)
    action_strip(name, [(img, (FW / 2 + 16, 18))], [1], anchor=((FW + 32) / 2, FH - 3))
    return img


def draw_strip(spec, name):
    """Drawing the revolver from a shoulder holster under the coat, in profile facing right: the near hand comes up,
    the elbow lifts in front of the chest as the hand goes in under the far lapel, the gun comes out at chest height
    muzzle down, swings forward past the belt, and the last frame is aim_frame's held aim."""
    fw = FW + 32

    def stance(arm, **kw):
        return pose(90, arms={1: arm, -1: AIM_OFF_ARM}, legs=AIM_LEGS, lean=-2.0, **kw)
    poses = [
        stance(("swing", 4, 6, 10)),
        stance(("pts", (0.15, 0.36, 0.11), (0.06, 0.31, 0.13), (0.02, 0.29, 0.11))),
        stance(("pts", (0.13, 0.31, 0.17), (0.02, 0.28, 0.10), (-0.04, 0.27, 0.05)), hand_in_coat=1),
        stance(("pts", (0.12, 0.34, 0.15), (0.04, 0.31, 0.11), (0.03, 0.31, 0.135)), gun=1, gun_dir=(0, 0.9, 0.5)),
        stance(("pts", (0.14, 0.38, 0.09), (0.07, 0.37, 0.16), (0.06, 0.37, 0.19)), gun=1, gun_dir=(0, 0.5, 1)),
        _aim_angle_pose(AIM_LEVELS[0]),
    ]
    frames = [(figure(spec, ps, fw, FH), (FW / 2 + 16, 18)) for ps in poses]
    action_strip(name, frames, [0.15, 0.08, 0.2, 0.1, 0.08, 0.3], anchor=(fw / 2, FH - 3))
    return frames


# Hip, shoulder, head, near knee/ankle, elbow/hand, before grounding into the wide action frame.
REST = [(66, 83), (43, 83), (29, 83), (84, 83), (104, 83), (51, 91), (66, 91)]
HARRINGTON_PRONE = [(78, 83), (101, 83), (115, 83), (60, 83), (42, 83), (100, 91), (114, 91)]
# Struck down facing right: onto both knees, pitching forward, then face-down with the head to the right.
KNEES_PRONE = [
    [(65, 67), (75, 43), (80, 29), (68, 88), (42, 91), (84, 63), (87, 76)],
    [(67, 76), (88, 62), (103, 58), (60, 88), (42, 91), (98, 78), (110, 90)],
    HARRINGTON_PRONE,
]
# Shot in the shoulder facing right: thrown back with the hands clutching the wound, knees folding straight down,
# sitting down hard, then flat on his back (head to the left, like REST) with the hands still on the shoulder.
SHOULDER_SHOT = [
    [(64, 57), (61, 34), (58, 19), (66, 74), (66, 91), (70, 44), (62, 37)],
    [(64, 68), (60, 46), (56, 32), (80, 76), (78, 91), (69, 55), (61, 49)],
    [(64, 82), (58, 58), (54, 44), (82, 80), (97, 91), (66, 68), (58, 61)],
    [(66, 83), (43, 83), (29, 83), (84, 83), (104, 83), (54, 75), (45, 78)],
]
SIT = [(64, 83), (57, 58), (54, 43), (84, 81), (99, 91), (47, 75), (42, 91)]
CROUCH = [(64, 70), (59, 47), (57, 32), (82, 75), (84, 91), (70, 63), (78, 75)]
HALF_UP = [(64, 62), (64, 36), (64, 21), (75, 76), (78, 91), (74, 53), (77, 65)]
UPRIGHT = [(64, 56), (64, 33), (64, 18), (65, 74), (66, 91), (67, 46), (69, 59)]
# Beaten down on his knees and forearms: hips over the knees, the shins rising a little behind to feet upright on
# tucked toes, the back sloping a little down to shoulders propped on the elbows, the forearms flat on the cobbles reaching
# forward, and the head lifted clear of them.
KNEEL = [(60, 72), (82, 76), (92, 72), (61, 88), (41, 85), (82, 90), (96, 90)]
# Hiding behind something, facing right, down on one knee: the far knee and shin flat on the floor with the toe tucked
# under, the near leg bent with its foot flat, the trunk a little forward but upright, the head up to listen and the
# near hand resting on the knee. The four extra points are the far leg's knee, ankle, heel and toe.
HALF_KNEEL = [(60, 65), (64, 42), (67, 27), (73, 75), (66, 91), (68, 54), (73, 65),
              (55, 81), (42, 87), (42, 84), (38, 91)]
HIDE_KNEEL = [(55, 72), (60, 50), (64, 36), (71, 74), (66, 91), (64, 62), (72, 71),
              (54, 90), (37, 90), (37, 87), (32, 92)]
# Getting up off his knees after the beating, facing right, from KNEEL. The near foot stays planted on its tucked toes
# (the strip's contact point), so the body comes back over it rather than sliding: he pushes up onto straight arms,
# sits back towards his heels with the trunk upright and the hands on his thighs, brings the far knee up with its foot
# flat in front and the near hand on it, then pushes off that knee leaning forward, the near heel coming down as he
# straightens. The four extra points are the far leg's knee, ankle, heel and toe.
KNEEL_PUSH = [(58, 71), (77, 65), (87, 59), (61, 88), (41, 85), (78, 77), (80, 90)]
KNEEL_BACK = [(46, 79), (51, 57), (54, 42), (61, 88), (41, 85), (55, 69), (61, 78)]
KNEE_UP = [(47, 77), (54, 55), (58, 40), (61, 88), (41, 85), (59, 66), (64, 70),
           (63, 70), (65, 88), (63, 90), (70, 91)]
PUSH_OFF = [(46, 66), (57, 44), (63, 30), (54, 79), (41, 87), (60, 56), (63, 69),
            (60, 72), (65, 88), (63, 90), (70, 91)]
NEARLY_UP = [(42, 58), (46, 35), (49, 20), (44, 74), (41, 91), (48, 47), (51, 58),
             (50, 74), (55, 88), (53, 90), (60, 91)]


def with_far_leg(joints):
    """A 7-joint pose with the far leg's knee, ankle, heel and toe made explicit (shadowing the near leg)."""
    knee, ankle = joints[3], joints[4]
    fk, fa = (knee[0] - 3, knee[1] - 2), (ankle[0] - 3, ankle[1] - 2)
    return list(joints) + [fk, fa, (fa[0] - 2, fa[1] - 1), (fa[0] + 5, fa[1])]
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

    def sequence(keys, end, timing, paint=action_figure):
        frames, times = [], []
        for i, (a, b) in enumerate(zip(keys, keys[1:])):
            frames.append(standing if i == 0 and keys is FALL else paint(scaled, a))
            frames.append(paint(scaled, between(a, b)))
            times += [timing[i] / 2] * 2
        return frames + [end], times + [timing[-1]]

    if name == "micah_masked":
        falling, times = sequence(FALL, action_figure(scaled, REST), [0.12, 0.12, 0.12, 0.12, 0.12, 0.22])
        action_strip(f"{name}_collapse", falling, times)
    if name == "micah":
        recovery, times = sequence([REST, SIT, CROUCH, HALF_UP, UPRIGHT], standing,
                                   [0.28, 0.3, 0.28, 0.22, 0.12])
        action_strip("micah_recover", recovery, times)
        kneel_rise_strip(spec, scaled, standing)
        crouch_strips(spec, scaled, standing)
    if name == "micah_no_tie":
        crouch_strips(spec, scaled, standing, name)


def profile_head(spec):
    """The right-facing head and neck of the walk sheet's profile frame, cut off above the shirt collar, and the
    point at the bottom of its neck. The crouch reuses it so the face is pixel-for-pixel the walking one."""
    from PIL import Image
    img = figure(spec, walk_pose(90, 0), FW, FH)
    px = img.load()
    opaque = lambda x, y: px[x, y][3] == 255
    collar = next(y for y in range(FH) for x in range(FW)
                  if opaque(x, y) and px[x, y][0] >= 0xe0 and px[x, y][2] >= 0xb0)
    below = {px[x, y][:3] for y in (collar, collar + 1) for x in range(FW) if opaque(x, y)}
    head = Image.new("RGBA", (FW, collar))
    hp = head.load()
    for y in range(collar):
        for x in range(FW):
            if opaque(x, y) and px[x, y][:3] not in below:
                hp[x, y] = px[x, y]
    neck = [x for x in range(FW) if hp[x, collar - 1][3]]
    return head, ((min(neck) + max(neck) + 1) / 2, collar)


def kneel_rise_strip(spec, scaled, standing):
    """Micah getting up off his hands and knees after the beating (micah_kneel_rise), from the held micah_kneel frame
    to the idle sheet frame, by way of the walk sheet's profile frame so he turns to the idle pose standing up."""
    from PIL import Image
    def between(a, b):
        return [tuple((x + y) / 2 for x, y in zip(p, q)) for p, q in zip(a, b)]

    def paint(joints):
        hip, shoulder = joints[0], joints[1]
        if -(shoulder[1] - hip[1]) < 0.55 * math.dist(hip, shoulder):
            return kneeling_figure(scaled, joints)
        # upright, the shirt front faces the way he looks, so only the coat shows side-on, hanging with gravity
        return action_figure(scaled, joints, plain_chest=True, coat_drape=True, toes_tucked=joints[4][1] < 91)
    turning = Image.new("RGBA", (192, FH))
    turning.alpha_composite(figure(spec, pose((90 + PLAYER_IDLE_YAW) / 2), FW, FH), (64, 0))
    keys = [KNEEL, between(KNEEL, KNEEL_PUSH), KNEEL_PUSH, between(KNEEL_PUSH, KNEEL_BACK), KNEEL_BACK, KNEE_UP,
            PUSH_OFF, NEARLY_UP]
    frames = [paint(k) for k in keys] + [(turning, (96, 18)), standing]
    action_strip("micah_kneel_rise", frames, [0.13, 0.07, 0.1, 0.08, 0.12, 0.15, 0.12, 0.1, 0.11, 0.12])


def crouch_strips(spec, scaled, standing, name="micah"):
    """Micah ducking down out of sight behind something onto one knee (micah_crouch), the kneel he holds there
    (micah_crouched), and standing back up (micah_crouch_rise: the same frames reversed). All face right; the coat
    hangs with gravity and the chest shows only coat, seen low and side-on, under the walk sheet's profile head."""
    def between(a, b):
        return [tuple((x + y) / 2 for x, y in zip(p, q)) for p, q in zip(a, b)]
    upright = with_far_leg(UPRIGHT)
    keys = [upright, between(upright, HALF_KNEEL), HALF_KNEEL, between(HALF_KNEEL, HIDE_KNEEL), HIDE_KNEEL]
    head = profile_head(spec)
    frames = [standing] + [action_figure(scaled, k, coat_drape=True, plain_chest=True, head_sprite=head) for k in keys]
    action_strip(f"{name}_crouch", frames, [0.08, 0.07, 0.07, 0.08, 0.09, 0.14])
    action_strip(f"{name}_crouched", frames[-1:], [1])
    action_strip(f"{name}_crouch_rise", frames[::-1], [0.12, 0.09, 0.08, 0.07, 0.07, 0.1])


def build_drinking():
    for kind in ("cup", "drink"):
        ps = pose(90, arms={1: (kind, 0, 0, 0), -1: ("side", 0, 0, 0)}, cup=1)
        image = figure(MICAH, ps, FW, FH)
        action_strip(f"micah_{kind}", [(image, (FW / 2, 18))], [1], anchor=(FW / 2, FH - 3))


# Micah takes Tony's bathtub gin from the bar, facing right: (hand height, reach forward, tip, gin left, seconds). He picks the glass up off the counter, raises it, tips it back at his lips, and sets the empty glass down.
GIN_KEYS = [
    (0.21, 0.25, 0.0, True, 0.3),
    (0.2, 0.18, 0.0, True, 0.16),
    (0.185, 0.12, 0.4, True, 0.14),
    (0.17, 0.1, 1.0, True, 1.1),
    (0.185, 0.12, 0.4, False, 0.16),
    (0.2, 0.18, 0.0, False, 0.16),
    (0.21, 0.25, 0.0, False, 0.35),
]
# Eleanor's drink keeps the pick-up height that matches her dressing-table glass.
ELEANOR_GIN_KEYS = [
    (0.27, 0.25, 0.0, True, 0.3),
    (0.26, 0.18, 0.0, True, 0.16),
    (0.2, 0.12, 0.4, True, 0.14),
    (0.17, 0.1, 1.0, True, 1.1),
    (0.2, 0.12, 0.4, False, 0.16),
    (0.26, 0.18, 0.0, False, 0.16),
    (0.27, 0.25, 0.0, False, 0.35),
]


def build_gin():
    frames, seconds = [], []
    for height, reach, tip, full, duration in GIN_KEYS:
        ps = pose(90, arms={1: ("hold", height, reach, tip), -1: ("side", 0, 0, 0)}, cup=1, glass="gin", full=full)
        frames.append((figure(MICAH, ps, FW, FH), (FW / 2, 18)))
        seconds.append(duration)
    action_strip("micah_gin", frames, seconds, anchor=(FW / 2, FH - 3))


# Micah shows the bellboy Eleanor's photograph, facing right: the near hand goes inside his coat, comes out with the
# card and holds it up, elbow still bent, halfway between him and the bellboy for the bellboy to look at. (near arm,
# hand inside the coat, card shown, seconds); micah_pocket_photo plays the same keys back the other way.
_P_SIDE = ("side", 0, 0, 0)
_P_POCKET = ("pts", (0.16, 0.38, 0.04), (0.08, 0.31, 0.08), (0.03, 0.29, 0.09))
_P_DRAWN = ("pts", (0.16, 0.38, 0.05), (0.09, 0.32, 0.11), (0.06, 0.3, 0.13))
_P_RISING = ("pts", (0.16, 0.37, 0.08), (0.1, 0.31, 0.15), (0.08, 0.29, 0.17))
_P_SHOWN = ("pts", (0.15, 0.35, 0.1), (0.1, 0.28, 0.18), (0.09, 0.265, 0.21))
SHOW_PHOTO_KEYS = [
    (_P_SIDE, False, False, 0.2),
    (_P_POCKET, True, False, 0.3),
    (_P_DRAWN, False, True, 0.2),
    (_P_RISING, False, True, 0.15),
    (_P_SHOWN, False, True, 0.6),
]
PHOTO_CARD = ((236, 226, 196, 255), (184, 168, 132, 255), (122, 92, 62, 255), (62, 44, 32, 255))


def _photo_card(img, hand):
    """The photograph held up in the fingers: a cream mount round a little sepia face under dark hair."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    x, y = (math.floor(v) for v in hand)
    d.rectangle([x - 1, y - 5, x + 2, y], fill=PHOTO_CARD[0])
    d.line([(x + 2, y - 5), (x + 2, y)], fill=PHOTO_CARD[1])
    d.rectangle([x, y - 4, x + 1, y - 2], fill=PHOTO_CARD[2])
    d.line([(x, y - 4), (x + 1, y - 4)], fill=PHOTO_CARD[3])
    return img


def build_show_photo():
    frames, seconds = [], []
    for arm, in_coat, shown, duration in SHOW_PHOTO_KEYS:
        marks = {}
        ps = pose(90, arms={1: arm, -1: _P_SIDE}, marks=marks, **({"hand_in_coat": 1} if in_coat else {}))
        img = figure(MICAH, ps, FW, FH)
        frames.append((_photo_card(img, marks["hand1"]) if shown else img, (FW / 2, 18)))
        seconds.append(duration)
    action_strip("micah_show_photo", frames, seconds, anchor=(FW / 2, FH - 3))
    back = frames[::-1]
    action_strip("micah_pocket_photo", back, [0.15, 0.15, 0.2, 0.3, 0.2], anchor=(FW / 2, FH - 3))


# The same gesture seen from behind, for the motel clerk across his counter: the near hand goes inside the coat, then
# the arm comes up in front of him with the elbow bent out to the side. His back hides the hand and the photograph, so
# only the flexing arm shows. (near arm or None for the back idle frame, hand inside the coat, seconds);
# micah_pocket_photo_back plays the same frames back the other way.
SHOW_PHOTO_BACK_KEYS = [
    (None, False, 0.2),
    (((0.16, 0.39, 0.05), (0.06, 0.34, 0.1), (0.01, 0.31, 0.1)), True, 0.3),
    (((0.18, 0.37, 0.09), (0.05, 0.32, 0.2), (0.01, 0.31, 0.23)), False, 0.2),
    (((0.19, 0.34, 0.12), (0.04, 0.3, 0.25), (0.0, 0.29, 0.28)), False, 0.15),
    (((0.2, 0.33, 0.13), (0.03, 0.29, 0.26), (-0.01, 0.28, 0.29)), False, 0.6),
]


def build_show_photo_back():
    frames, seconds = [], []
    for pts, in_coat, duration in SHOW_PHOTO_BACK_KEYS:
        kw = {}
        if pts:
            arms = {1: ("pts",) + tuple(list(p) for p in pts), -1: pose(164)["arms"][-1]}
            kw = dict(arms=arms, behind_arms=(1,), **({"hand_in_coat": 1} if in_coat else {}))
        frames.append((figure(MICAH, pose(164, **kw), FW, FH), (FW / 2, 18)))
        seconds.append(duration)
    action_strip("micah_show_photo_back", frames, seconds, anchor=(FW / 2, FH - 3))
    action_strip("micah_pocket_photo_back", frames[::-1], [0.15, 0.15, 0.2, 0.3, 0.2], anchor=(FW / 2, FH - 3))


# Act 2, back at the motel desk: Micah, facing right across the counter, reaches for the clerk's tie, closes his fist
# on it and hauls it down to the desktop. (near arm (elbow, wrist, hand), lean, seconds); the last frame is held.
TIE_REACH = ("pts", (0.17, 0.31, 0.13), (0.07, 0.24, 0.28), (0.05, 0.225, 0.32))
TIE_GRAB = ("pts", (0.17, 0.31, 0.12), (0.07, 0.235, 0.27), (0.05, 0.22, 0.305))
TIE_YANK = ("pts", (0.17, 0.38, 0.03), (0.07, 0.32, 0.17), (0.05, 0.305, 0.205))
TIE_PULL_KEYS = [
    (("swing", 4, 6, 10), 0.0, 0.1),
    (TIE_REACH, 5.0, 0.1),
    (TIE_GRAB, 5.0, 0.12),
    (TIE_YANK, -4.0, 0.2),
]
# The clerk, facing right (the lobby flips him to face Micah): yanked forward by the tie and down onto the desktop,
# face first, his hands slapping down either side. The counter hides him from the hips down, so those frames are cut
# off below the desktop (CLERK_CUT rows above the feet) and the lobby draws him over it while he's down there.
CLERK_YANKED = [(64, 56), (77, 38), (87, 27), (65, 74), (66, 91), (76, 47), (86, 50)]
CLERK_DOWN = [(64, 56), (79, 52), (90, 55), (65, 74), (66, 91), (78, 60), (88, 60)]
CLERK_CUT = 34


def tie_pull_strips():
    from PIL import Image
    frames, seconds = [], []
    for i, (arm, lean, duration) in enumerate(TIE_PULL_KEYS):
        marks = {}
        ps = pose(90, arms={1: arm, -1: ("side", 0, 0, 0)}, lean=lean, front_arms=(1,) if arm[0] == "pts" else (),
                  marks=marks)
        img = figure(MICAH, ps, FW, FH)
        if i >= 2:  # the clerk's tie, balled in his fist and pulled taut towards the clerk
            hx_, hy_ = (math.floor(v) for v in marks["hand1"])
            for dx in range(1, min(6, img.width - 1 - hx_)):
                img.putpixel((hx_ + dx, hy_ - (dx > 3)), (106, 44, 34, 255) if dx % 3 else (138, 64, 48, 255))
        frames.append((img, (FW / 2, 18)))
        seconds.append(duration)
    action_strip("micah_tie_pull", frames, seconds, anchor=(FW / 2, FH - 3))

    scaled = dict(CLERK, h=CLERK["h"] * SCALE)
    stand = Image.new("RGBA", (192, FH))
    stand.alpha_composite(figure(CLERK, pose(90, arms=_arms("down"), lean=4.0), FW, FH), (64, 0))
    clip = []
    face = profile_head(CLERK)
    bent = [action_figure(scaled, k, head_sprite=face) for k in (CLERK_YANKED, CLERK_DOWN)]
    for img, head in [(stand, (96, 18))] + bent:
        img = img.copy()
        px = img.load()
        for y in range(FH - 3 - CLERK_CUT, FH):
            for x in range(img.width):
                px[x, y] = (0, 0, 0, 0)
        clip.append((img, head))
    action_strip("clerk_tie_pulled", clip, [0.08, 0.07, 0.2], anchor=(96, FH - 3))


# Eleanor at the dressing table, facing right: she drinks the gin like Micah does at the bar, sets the glass down,
# then dips her fingers in the compact and lifts a pinch of powder to her nose: (hand height, reach, powder, nod, s).
POWDER_KEYS = [
    (0.29, 0.24, False, 0.0, 0.3),
    (0.22, 0.14, True, 0.0, 0.14),
    (0.185, 0.075, True, 0.004, 0.5),
    (0.19, 0.08, False, 0.009, 0.35),
]


SMOKE_YAW = 30
# Micah lights up in the wind, turned three-quarters to the viewer: (near arm, far arm, cigarette, lighter, nod, puff,
# seconds). Arms are explicit (elbow, wrist, hand) body-frame points; the near (right) hand carries the cigarette, the
# far one the lighter, and for the light both hands close round the flame in front of his face, his head bowed into it.
# cigarette: None, "hand" (unlit, in the fingers), "lips" (unlit), "lit" (lit, in the lips), "held" (lit, lowered) or
# "drag" (lit, at the lips, the ember glowing as he draws on it).
# lighter: None, "shut", "flame"/"gust" (lid flipped, the flame up or bent by the wind) or "light" (flame drawn into
# the cigarette's tip). puff: how far a breath of smoke has drifted from his mouth (0 = none).
_SIDE = ("side", 0, 0, 0)
_TO_LIPS = ("pts", (0.17, 0.33, 0.1), (0.075, 0.2, 0.12), (0.03, 0.165, 0.11))
_AT_LIPS = ("pts", (0.17, 0.34, 0.1), (0.07, 0.2, 0.11), (0.025, 0.16, 0.1))
_CUP = ("pts", (-0.15, 0.33, 0.12), (-0.04, 0.19, 0.17), (-0.01, 0.165, 0.16))
_CUP_NEAR = ("pts", (0.16, 0.33, 0.1), (0.07, 0.19, 0.16), (0.035, 0.165, 0.15))
_LIFT = ("pts", (-0.15, 0.38, 0.08), (-0.08, 0.3, 0.14), (-0.05, 0.27, 0.14))
_LOWER = ("pts", (0.16, 0.38, 0.08), (0.1, 0.32, 0.15), (0.075, 0.3, 0.17))
_HOLD = ("pts", (0.15, 0.40, 0.05), (0.1, 0.39, 0.15), (0.085, 0.37, 0.18))
_RAISE = ("pts", (0.17, 0.36, 0.08), (0.09, 0.26, 0.14), (0.05, 0.21, 0.14))
_BOW = 0.007
SMOKE_KEYS = [
    (_SIDE, _SIDE, None, None, 0, 0, 0.3),
    (_TO_LIPS, _SIDE, "hand", None, 0, 0, 0.22),
    (_AT_LIPS, _LIFT, "lips", "shut", 0, 0, 0.22),
    (_CUP_NEAR, _CUP, "lips", "shut", _BOW, 0, 0.2),
    (_CUP_NEAR, _CUP, "lips", "gust", _BOW, 0, 0.22),
    (_CUP_NEAR, _CUP, "lips", "flame", _BOW, 0, 0.3),
    (_CUP_NEAR, _CUP, "lit", "light", _BOW, 0, 0.45),
    (_AT_LIPS, _LIFT, "lit", "shut", 0, 0, 0.22),
    (_LOWER, _SIDE, "held", None, 0, 1, 0.24),
    (_HOLD, _SIDE, "held", None, 0, 2, 0.4),
    (_HOLD, _SIDE, "held", None, 0, 0, 0.8),
]
# A drag on it, every few seconds while he talks: hand to the lips, the ember flaring, the hand down, the smoke out.
SMOKE_DRAG_KEYS = [
    (_LOWER, _SIDE, "held", None, 0, 0, 0.14),
    (_RAISE, _SIDE, "held", None, 0, 0, 0.12),
    (_AT_LIPS, _SIDE, "drag", None, 0, 0, 0.6),
    (_AT_LIPS, _SIDE, "lit", None, 0, 0, 0.18),
    (_RAISE, _SIDE, "held", None, 0, 0, 0.12),
    (_LOWER, _SIDE, "held", None, 0, 1, 0.24),
    (_HOLD, _SIDE, "held", None, 0, 2, 0.36),
    (_HOLD, _SIDE, "held", None, 0, 3, 0.4),
    (_HOLD, _SIDE, "held", None, 0, 0, 0.2),
]
EMBER = ((255, 244, 190, 255), (255, 150, 50, 255), (196, 54, 28, 255))
PAPER = ((240, 236, 222, 255), (196, 188, 170, 255))
BRASS = ((224, 184, 96, 255), (168, 124, 52, 255))
FIRE = (255, 196, 96)


def _glow(img, cx, cy, radius, strength):
    """Warm firelight on whatever the figure has round (cx, cy) - cupped hands, the face bent over them - and a
    faint halo in the air, so the flame reads at a distance."""
    px = img.load()
    for y in range(max(0, cy - radius), min(img.height, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(img.width, cx + radius + 1)):
            f = 1 - math.hypot(x - cx, y - cy) / (radius + 0.5)
            if f <= 0:
                continue
            r, g, b, a = px[x, y]
            k = strength * f
            if a:
                px[x, y] = (round(r + (FIRE[0] - r) * k), round(g + (FIRE[1] - g) * k), round(b + (FIRE[2] - b) * k), a)
            else:
                px[x, y] = FIRE + (round(110 * k * f),)


def _puff(img, x, y, drift, t):
    """A breath of smoke out of the corner of his mouth, a soft cloud that rises and spreads as it drifts off to the
    viewer's right, thinning as it goes."""
    px = img.load()
    cx, cy = x + 2 + drift * 3, y - drift * 3
    alpha = (0, 200, 160, 110)[drift]
    blobs = [(cx, cy, 1.4 + drift * 1.2), (cx - 1 - drift * 0.6, cy + 1, 1 + drift * 0.7),
             (cx + 1 + drift * 0.8, cy - 0.5 - drift * 0.4, 1 + drift * 0.8)]
    for yy in range(math.floor(cy - 6), math.ceil(cy + 6)):
        for xx in range(math.floor(cx - 8), math.ceil(cx + 9)):
            if not (0 <= xx < img.width and 0 <= yy < img.height):
                continue
            d = min(math.hypot(xx - bx, (yy - by) * 1.25) / r for bx, by, r in blobs)
            if d > 1:
                continue
            a = round(alpha * (1 - 0.5 * d))
            shade = (222, 224, 228) if yy < cy - 0.5 else (182, 186, 196)
            r, g, b, a0 = px[xx, yy]
            if a0:  # thin smoke over the coat or the face
                k = a / 255 * 0.75
                px[xx, yy] = tuple(round(c + (sv - c) * k) for c, sv in zip((r, g, b), shade)) + (a0,)
            else:
                px[xx, yy] = shade + (a,)


def _smoke_props(img, marks, cig, lighter, puff, t):
    """The cigarette, the lighter and its flame, the ember and the smoke, painted over the figure at the marked hands
    (hand1: the cigarette hand, hand-1: the lighter hand) and mouth."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    mx, my = (math.floor(v) for v in marks["mouth"])
    tip = None
    if cig in ("lips", "lit", "drag"):  # out of the corner of the mouth, drooping down and out towards the viewer's right
        for i, (dx, dy) in enumerate(((1, 0), (2, 0), (3, 1))):
            d.point((mx + dx, my + dy), fill=PAPER[0] if i < 2 else PAPER[1])
        tip = (mx + 4, my + 1)
    elif cig in ("hand", "held"):  # between the fingers, tipped up and out
        hx_, hy_ = (math.floor(v) for v in marks["hand1"])
        for i, (dx, dy) in enumerate(((1, 0), (2, -1), (3, -1))):
            d.point((hx_ + dx, hy_ + dy), fill=PAPER[0] if i else PAPER[1])
        tip = (hx_ + 4, hy_ - 2)
    if cig == "drag":  # the ember flares as he draws on it
        _glow(img, tip[0], tip[1], 3, 0.45)
        d.point(tip, fill=EMBER[0])
        d.point((tip[0] + 1, tip[1]), fill=EMBER[1])
    elif cig in ("lit", "held"):
        d.point(tip, fill=EMBER[1])
    if lighter:  # the lighter's brass case in the far hand, the lid flipped open when it's lit
        lx, ly = (math.floor(v) for v in marks["hand-1"])
        if lighter == "shut" or not tip:
            d.rectangle([lx, ly - 1, lx + 1, ly + 1], fill=BRASS[1])
            d.point((lx, ly - 1), fill=BRASS[0])
        else:  # cupped hands: the case shows just under the cigarette's tip, the flame between the palms
            fx, fy = tip[0] - 1, tip[1] + 2
            d.rectangle([fx - 1, fy + 1, fx, fy + 2], fill=BRASS[1])
            d.point((fx - 1, fy + 1), fill=BRASS[0])
            _glow(img, fx, fy - 1, 8 if lighter == "light" else 7, 0.8 if lighter == "flame" else 0.65)
            # (dx, dy, hot core): a tall flame, one the wind bends over, one drawn into the tip
            flame = {"gust": ((0, 0, 0), (1, 0, 1), (1, -1, 1), (2, -1, 0), (3, -1, 0)),
                     "flame": ((0, 0, 0), (1, 0, 0), (0, -1, 1), (1, -1, 1), (0, -2, 1), (1, -3, 0)),
                     "light": ((0, 0, 0), (1, 0, 1), (1, -1, 1), (2, -2, 0))}[lighter]
            for dx, dy, hot in flame:
                d.point((fx + dx, fy + dy), fill=EMBER[0] if hot else EMBER[1])
            if lighter == "light":
                d.point(tip, fill=EMBER[0])
    if cig in ("lit", "held"):  # a thin wisp curling up off the ember, half-transparent so it reads as smoke
        x, y = tip
        for k in range(1, 9 if cig == "held" else 5):
            x += (0, 1, 1, 0, -1, -1, 0, 1)[(k + t) % 8]
            if 0 <= y - k < img.height and 0 <= x < img.width:
                img.putpixel((x, y - k), (226, 224, 220, max(70, 210 - k * 18)))
    if puff:
        _puff(img, mx + 1, my, puff, t)
    return img


def _smoke_strip(name, keys):
    frames, seconds = [], []
    # the wisp's phase is counted back from the last frame, so every strip ends on the same held pose
    for i, (near, far, cig, lighter, nod, puff, duration) in enumerate(keys, len(SMOKE_KEYS) - len(keys)):
        marks = {}
        front = tuple(s for s, a in ((1, near), (-1, far)) if a[0] == "pts" and a[3][1] < 0.24)
        ps = pose(SMOKE_YAW, arms={1: near, -1: far}, front_arms=front, marks=marks, nod=nod)
        img = _smoke_props(figure(MICAH, ps, FW, FH), marks, cig, lighter, puff, i)
        frames.append((img, (FW / 2, 18)))
        seconds.append(duration)
    action_strip(name, frames, seconds, anchor=(FW / 2, FH - 3))


def build_smoke():
    _smoke_strip("micah_smoke", SMOKE_KEYS)
    _smoke_strip("micah_smoke_drag", SMOKE_DRAG_KEYS)


# Teddy pays Micah his first day in the office, three-quarters to the viewer like his idle frame: the near hand goes
# inside his jacket for the wallet, both hands open it at his chest, the far one peels off the notes, the wallet goes
# back and he's left holding out the money. (near arm, far arm, wallet: (hand, "shut"/"open") or None, notes: where
# they are - "wallet", a hand mark or None -, seconds)
_T_POCKET = ("pts", (0.15, 0.34, 0.05), (0.02, 0.26, 0.08), (-0.03, 0.23, 0.07))
_T_CHEST_NEAR = ("pts", (0.17, 0.38, 0.06), (0.08, 0.31, 0.14), (0.045, 0.29, 0.16))
_T_CHEST_FAR = ("pts", (-0.16, 0.38, 0.06), (-0.07, 0.31, 0.14), (-0.03, 0.29, 0.16))
_T_OFFER = ("pts", (0.16, 0.37, 0.08), (0.11, 0.33, 0.18), (0.1, 0.31, 0.22))
_T_SIDE = ("swing", 3, 6, 10)
TEDDY_WALLET_KEYS = [
    (_T_SIDE, _T_SIDE, None, None, 0.12),
    (_T_POCKET, _T_SIDE, None, None, 0.14),
    (_T_CHEST_NEAR, _T_CHEST_FAR, ("hand1", "shut"), None, 0.14),
    (_T_CHEST_NEAR, _T_CHEST_FAR, ("hand1", "open"), "wallet", 0.22),
    (_T_CHEST_NEAR, _T_CHEST_FAR, ("hand1", "open"), "hand-1", 0.2),
    (_T_POCKET, _T_CHEST_FAR, None, "hand-1", 0.14),
    (_T_OFFER, _T_SIDE, None, "hand1", 0.2),
]
# At the corner of the desk, facing right: he leans in, lays the notes down by the lamp and takes his hand back empty
# (the room shows the money on the desk from then on). (hand height, reach, notes in hand, lean, seconds)
TEDDY_NOTES_KEYS = [
    (0.31, 0.12, True, 0.0, 0.12),
    (0.35, 0.2, True, 3.0, 0.12),
    (0.42, 0.27, True, 7.0, 0.18),
    (0.42, 0.27, False, 7.0, 0.1),
]
WALLET = ((58, 36, 20, 255), (110, 74, 44, 255), (150, 118, 84, 255))
NOTE = ((168, 192, 152, 255), (106, 138, 90, 255))


def _cash_props(img, marks, wallet, notes):
    """The wallet (shut, or open with its pale lining showing) and the green fan of notes, at the marked hands."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    spot = None
    if wallet:
        hand, state = wallet
        x, y = (math.floor(v) for v in marks[hand])
        if state == "shut":
            d.rectangle([x - 1, y - 1, x + 2, y + 1], fill=WALLET[0])
            d.line([(x - 1, y - 1), (x + 2, y - 1)], fill=WALLET[1])
        else:
            mx = math.floor((marks["hand1"][0] + marks["hand-1"][0]) / 2)
            d.rectangle([mx - 3, y - 1, mx + 2, y + 1], fill=WALLET[0])
            d.rectangle([mx - 2, y - 1, mx + 1, y], fill=WALLET[2])
            d.point((mx - 1, y - 1), fill=WALLET[1])
            spot = (mx - 1, y - 2)
    if notes:
        x, y = spot if notes == "wallet" else (math.floor(v) for v in marks[notes])
        for dx, dy, c in ((0, -1, 0), (1, -1, 1), (2, -1, 0), (0, -2, 0), (1, -2, 0), (2, -2, 1), (3, -2, 0)):
            d.point((x + dx, y + dy), fill=NOTE[c])
    return img


def teddy_cash_strips():
    frames, seconds = [], []
    for near, far, wallet, notes, duration in TEDDY_WALLET_KEYS:
        marks = {}
        front = tuple(s for s, a in ((1, near), (-1, far)) if a[0] == "pts" and a[3][2] > 0.1)
        ps = pose(35, arms={1: near, -1: far}, front_arms=front, marks=marks)
        frames.append((_cash_props(figure(TEDDY, ps, FW, FH), marks, wallet, notes), (FW / 2, 18)))
        seconds.append(duration)
    action_strip("teddy_wallet", frames, seconds, anchor=(FW / 2, FH - 3))
    frames, seconds = [], []
    for height, reach, held, lean, duration in TEDDY_NOTES_KEYS:
        marks = {}
        ps = pose(90, arms={1: ("hold", height, reach, 0), -1: _T_SIDE}, lean=lean, marks=marks)
        frames.append((_cash_props(figure(TEDDY, ps, FW, FH), marks, None, "hand1" if held else None), (FW / 2, 18)))
        seconds.append(duration)
    action_strip("teddy_leave_notes", frames, seconds, anchor=(FW / 2, FH - 3))


def eleanor_drink_strip():
    frames, seconds = [(figure(ELEANOR_GOWN_NPC, pose(90), FW, FH), (FW / 2, 18))], [0.3]
    for height, reach, tip, full, duration in ELEANOR_GIN_KEYS:
        ps = pose(90, arms={1: ("hold", height, reach, tip), -1: ("side", 0, 0, 0)}, cup=1, glass="gin", full=full)
        frames.append((figure(ELEANOR_GOWN_NPC, ps, FW, FH), (FW / 2, 18)))
        seconds.append(duration)
    for height, reach, powder, nod, duration in POWDER_KEYS:
        ps = pose(90, arms={1: ("hold", height, reach, 0), -1: ("side", 0, 0, 0)}, nod=nod,
                  **({"powder": 1} if powder else {}))
        frames.append((figure(ELEANOR_GOWN_NPC, ps, FW, FH), (FW / 2, 18)))
        seconds.append(duration)
    frames.append(frames[0])
    seconds.append(0.4)
    action_strip("eleanor_drink", frames, seconds, anchor=(FW / 2, FH - 3))


def _phone_stand(y, z):
    return ("pts", (-0.1, 0.36, 0.0), (-0.03, y + 0.02, z - 0.03), (-0.02, y, z))


# Eleanor in the First Interlude lifts the candlestick off the vanity in her far hand, takes the receiver off the hook
# with the near one and holds it to her ear; the last frame is held through the call. (near arm, receiver held, s)
PHONE_KEYS = [
    (_phone_stand(0.44, 0.22), ("side", 0, 0, 0), False, 0.25),
    (_phone_stand(0.3, 0.2), ("side", 0, 0, 0), False, 0.25),
    (_phone_stand(0.25, 0.19), ("pts", (0.12, 0.38, 0.06), (0.06, 0.3, 0.12), (0.04, 0.27, 0.15)), True, 0.25),
    (_phone_stand(0.25, 0.19), ("pts", (0.12, 0.29, 0.06), (0.1, 0.21, 0.07), (0.06, 0.14, 0.0)), True, 0.3),
]


def eleanor_phone_strips():
    """eleanor_phone picks the telephone up and ends with the receiver at her ear; eleanor_phone_down hangs it up
    and ends holding the candlestick out over the vanity, where the room's own telephone takes over again."""
    idle = (figure(ELEANOR_NPC, pose(90), FW, FH), (FW / 2, 18))
    keys = []
    for stand, near, held, duration in PHONE_KEYS:
        ps = pose(90, arms={-1: stand, 1: near}, telephone=(-1, 1 if held else None),
                  **({"front_arms": (1,)} if held else {}))
        keys.append(((figure(ELEANOR_NPC, ps, FW, FH), (FW / 2, 18)), duration))
    action_strip("eleanor_phone", [idle] + [f for f, _ in keys], [0.2] + [s for _, s in keys],
                 anchor=(FW / 2, FH - 3))
    back = keys[::-1]
    action_strip("eleanor_phone_down", [f for f, _ in back], [0.3] + [s for _, s in back[1:]],
                 anchor=(FW / 2, FH - 3))


# Eleanor's duffle in the First Interlude. She sets it down at her near (right) side, in front of her feet, before
# every conversation and takes it back after; the floor sprite takes over from the strip's last frame at her feet.
BAG_AT = ("floor", (0.065, 0.15))  # where it stands, in her yaw-55 idle frame
BAG_Z = 2.5  # the bag on the floor is in front of her legs and hanging arm
# (lean, legs, hand target or None, still in her hand, seconds): she dips, lowers it until it all but touches the
# floor, lets it settle with her hand still on the handles, and straightens up.
_BAG_FLOOR_Y = 1.0 - 0.095 * 1.92 - 0.03
BAG_DOWN_KEYS = [
    (4, {1: (12, 16, 0), -1: (4, 12, -4)}, (0.07, 0.62, 0.08), True, 0.12),
    (8, {1: (26, 40, 0), -1: (12, 32, -6)}, (0.065, _BAG_FLOOR_Y - 0.05, 0.15), True, 0.14),
    (10, {1: (45, 75, 0), -1: (24, 60, -8)}, (0.065, _BAG_FLOOR_Y - 0.08, 0.15), False, 0.16),
    (6, {1: (18, 28, 0), -1: (8, 22, -6)}, None, False, 0.14),
]


def _bag_frame(spec, lean, legs, target, carried, opened=False):
    arm = ("reach", target, 0, 0) if target else ("swing", 14, 6, 18)
    ps = pose(PLAYER_IDLE_YAW, lean=lean, legs=legs, arms={1: arm, -1: ("swing", 4, 6, 10)}, front_arms=(1,))
    if carried:
        ps["duffle"] = (1,)
    else:
        ps["duffle"] = BAG_AT + ((1,) if target else ())
        ps["duffle_z"] = BAG_Z
    ps["duffle_open"] = opened
    return figure(spec, ps, FW, FH)


def _bag_idle(spec, opened=False):
    return figure(spec, pose(PLAYER_IDLE_YAW, duffle=BAG_AT, duffle_z=BAG_Z, duffle_open=opened), FW, FH)


# Lifting it off the floor (eleanor_bag_up only): (lean, legs, hand target, pixels the bag has risen). Her reach stops
# short of the floor, so the bag is the one on the floor in the hand-on-the-handles frame, raised, hidden above her
# hand and with her hand drawn back over it.
BAG_LIFT_KEYS = [
    BAG_DOWN_KEYS[2][:3] + (2,),
    (9, {1: (38, 62, 0), -1: (20, 50, -7)}, (0.065, _BAG_FLOOR_Y - 0.07, 0.15), 5),
    (8.5, {1: (32, 50, 0), -1: (16, 40, -6)}, (0.065, _BAG_FLOOR_Y - 0.06, 0.15), 8),
]


def _bag_lift_frames(spec):
    import numpy as np
    from PIL import Image
    lean, legs, target = BAG_DOWN_KEYS[2][:3]
    floor = np.asarray(_bag_frame(spec, lean, legs, target, False)).astype(int)

    def body(lean, legs, target):  # the same pose with no bag at all
        ps = pose(PLAYER_IDLE_YAW, lean=lean, legs=legs, arms={1: ("reach", target, 0, 0), -1: ("swing", 4, 6, 10)},
                  front_arms=(1,))
        return np.asarray(figure(spec, ps, FW, FH)).astype(int)

    bag = (np.abs(floor - body(lean, legs, target)).sum(axis=2) > 0) & (floor[..., 3] == 255)
    out = []
    for lean, legs, target, dy in BAG_LIFT_KEYS:
        b = body(lean, legs, target)
        skin = (b[..., 3] == 255) & (b[..., 0] - b[..., 2] > 40) & (b[..., 0] > 150)
        hand = np.nonzero(skin[55:])[0].max() + 55  # the bottom of her hand on the handles
        f = b.copy()
        for y, x in zip(*np.nonzero(bag)):
            if y - dy >= hand - 1:
                f[y - dy, x] = floor[y, x]
        skin[:hand - 5] = False
        f[skin] = b[skin]
        out.append(Image.fromarray(f.astype(np.uint8), "RGBA"))
    return out


def bag_floor_sprites():
    """duffle_bag(_open): the bag alone where her strips leave it, in a full 64x96 frame placed at her feet."""
    import numpy as np
    from PIL import Image
    plain = np.asarray(figure(ELEANOR, pose(PLAYER_IDLE_YAW), FW, FH)).astype(int)
    out = {}
    for opened, name in ((False, "duffle_bag"), (True, "duffle_bag_open")):
        withbag = np.asarray(_bag_idle(ELEANOR, opened)).astype(int)
        mask = np.abs(withbag - plain).sum(axis=2) > 0
        rgba = withbag.astype(np.uint8).copy()
        rgba[..., 3] = np.where(mask, rgba[..., 3], 0)
        out[name] = Image.fromarray(rgba, "RGBA")
        save(out[name], "sprites", f"{name}.png")
    return out


# Combing her hair in the cell: (comb hand height, seconds). She faces us with the mirror held up in her left hand.
COMB_STROKES = [(0.3, 0.3), (0.08, 0.35), (0.16, 0.3), (0.24, 0.3), (0.08, 0.35), (0.16, 0.3), (0.24, 0.3),
                (0.1, 0.5)]
COMB_STEP = 11  # pixels she steps to her left of the bag to stand and comb


def _comb_pose(y):
    return pose(16, arms={-1: ("pts", (-0.12, 0.36, 0.08), (-0.10, 0.25, 0.16), (-0.095, 0.23, 0.17)),
                          1: ("pts", (0.16, 0.22, -0.02), (0.1, y + 0.025, 0.0), (0.085, y, 0.0))},
                front_arms=(1, -1), comb=1, hand_mirror=-1)


BAG_PAD = 4  # transparent rows under her strips: the bag on the floor stands lower than her feet


def _padded(frames):
    from PIL import Image
    out = []
    for img, head in frames:
        tall = Image.new("RGBA", (img.width, img.height + BAG_PAD))
        tall.alpha_composite(img)
        out.append((tall, head))
    return out


def eleanor_bag_strips():
    """eleanor_bag_down sets the duffle down, eleanor_bag_up (the same frames backwards) takes it again;
    eleanor_comb bends to the bag, opens it, and stands combing her hair in the little mirror, the last stroke held."""
    from PIL import Image
    head = (FW / 2, 18)
    spec = ELEANOR  # the player's own figure: her skirt stays one piece as she bends
    carry = figure(spec, pose(PLAYER_IDLE_YAW, arms={1: ("carry", 0, 0, 0), -1: ("swing", -2, 6, 12)}, duffle=(1,)),
                   FW, FH)
    frames, seconds = [(carry, head)], [0.1]
    for lean, legs, target, carried, duration in BAG_DOWN_KEYS:
        frames.append((_bag_frame(spec, lean, legs, target, carried), head))
        seconds.append(duration)
    frames.append((_bag_idle(spec), head))
    seconds.append(0.12)
    frames = _padded(frames)
    action_strip("eleanor_bag_down", frames, seconds, anchor=(FW / 2, FH - 3))
    # taking it back is the same frames backwards, with three more where the bag leaves the floor: she grips it, it
    # comes up off the floor, then to her shin, before the knee-height frame
    up, up_seconds = frames[::-1], seconds[::-1]
    lifts = _padded([(img, head) for img in _bag_lift_frames(spec)])
    action_strip("eleanor_bag_up", up[:3] + lifts + up[3:], up_seconds[:3] + [0.14, 0.12, 0.12] + up_seconds[3:],
                 anchor=(FW / 2, FH - 3))

    bag_open = bag_floor_sprites()["duffle_bag_open"]
    frames, seconds = [(_bag_idle(spec), head)], [0.2]
    reach = [(8, BAG_DOWN_KEYS[1][1], BAG_DOWN_KEYS[1][2], 0.2),  # bends to it, opens it, reaches in
             (10, BAG_DOWN_KEYS[2][1], (0.065, _BAG_FLOOR_Y - 0.04, 0.15), 0.45),
             (8, BAG_DOWN_KEYS[1][1], BAG_DOWN_KEYS[1][2], 0.2)]
    for lean, legs, target, duration in reach:
        frames.append((_bag_frame(spec, lean, legs, target, False, opened=True), head))
        seconds.append(duration)
    for y, duration in COMB_STROKES:  # standing a step to the side of the open bag, facing us
        img = Image.new("RGBA", (FW, FH))
        img.alpha_composite(figure(spec, _comb_pose(y), FW, FH), (-COMB_STEP, 0))
        img.alpha_composite(bag_open)
        frames.append((img, (FW / 2 - COMB_STEP, 18)))
        seconds.append(duration)
    action_strip("eleanor_comb", _padded(frames), seconds, anchor=(FW / 2, FH - 3))


def eleanor_bag_sheets():
    player_sheet(ELEANOR, "eleanor_bag_play", arms={1: ("carry", 0, 0, 0), -1: ("swing", 0, 0, 0)},
                 props=dict(duffle=(1,)))
    player_sheet(ELEANOR_PYJAMA, "eleanor_pyjama_play")
    eleanor_bag_strips()


# Eleanor in the sheet takes the candlestick off the nightstand and brings it down on the back of Harrington's head,
# facing right. The near (right) arm swings; the far one keeps the sheet clutched to her. (arm, candle way, lean, legs)
STRIKE_STANCE = {1: (12, 8, 0), -1: (-12, 10, -6)}
STRIKE_KEYS = [
    (("clutch", 0, 0, 0), None, 0.0, None, 0.35),
    (("swing", 48, 4, 26), (0, 1, 0.15), 7.0, None, 0.3),
    (("swing", 92, 4, 70), (0, 1, 0.3), 2.0, STRIKE_STANCE, 0.22),
    (("swing", 128, 6, 56), None, -6.0, STRIKE_STANCE, 0.35),
    (("swing", 100, 4, 2), None, 9.0, STRIKE_STANCE, 0.07),
    (("swing", 28, 4, 8), None, 13.0, STRIKE_STANCE, 0.45),
]


def eleanor_strike_strip():
    fw = FW + 32
    frames, seconds = [], []
    for arm, way, lean, legs, duration in STRIKE_KEYS:
        kw = dict(arms={1: arm, -1: ("clutch", 0, 0, 0)}, lean=lean)
        if legs:
            kw["legs"] = legs
        if arm[0] != "clutch":
            kw["candlestick"] = (1, way) if way else 1
        frames.append((figure(ELEANOR_SHEET_NPC, pose(90, **kw), fw, FH), (fw / 2, 18)))
        seconds.append(duration)
    action_strip("eleanor_strike", frames, seconds, anchor=(fw / 2, FH - 3))


# On the motel fire escape, after the First Interlude: Micah, stopped facing right KISS_GAP pixels short of Eleanor (in black,
# facing left), steps in, turns side-on with his near arm round her waist and kisses her, while she turns to him, lifts
# her face and reaches her near arm round his back. One strip, played on the player with the Eleanor actor hidden:
# frame 0 is both idle sprites exactly where they stood, her feet KISS_RISE pixels higher (further back on the landing).
# (Micah step in, his yaw, lean, nod, near arm (elbow, wrist, hand) or None, her yaw, lean, nod, her near arm or None,
# seconds)
KISS_GAP, KISS_RISE, KISS_W = 22, 2, 128
KISS_KEYS = [
    (0, PLAYER_IDLE_YAW, 0.0, 0.0, None, 35, 0.0, 0.0, None, 0.25),
    (3, 72, 3.0, 0.008, ((0.15, 0.38, 0.05), (0.12, 0.44, 0.13), (0.1, 0.45, 0.16)), 60, -1.0, -0.002,
     ((0.15, 0.40, 0.05), (0.13, 0.43, 0.15), (0.11, 0.43, 0.18)), 0.3),
    (6, 85, 6.0, 0.018, ((0.15, 0.38, 0.06), (0.12, 0.43, 0.16), (0.09, 0.44, 0.19)), 80, -2.0, -0.004,
     ((0.15, 0.36, 0.07), (0.12, 0.29, 0.19), (0.09, 0.27, 0.23)), 0.35),
    (8, 90, 8.0, 0.025, ((0.15, 0.38, 0.06), (0.12, 0.43, 0.16), (0.09, 0.44, 0.19)), 90, -3.0, -0.005,
     ((0.15, 0.345, 0.06), (0.12, 0.22, 0.155), (0.09, 0.195, 0.185)), 1.0),
]


def kiss_strip():
    from PIL import Image
    mx0 = 20
    anchor_x = mx0 + FW // 2
    ex = anchor_x + KISS_GAP - NPC_W // 2
    frames, seconds = [], []
    flip = Image.Transpose.FLIP_LEFT_RIGHT
    for i, (step, yaw, lean, nod, arm, her_yaw, her_lean, her_nod, her_arm, duration) in enumerate(KISS_KEYS):
        img = Image.new("RGBA", (KISS_W, FH))
        lips_met = i == len(KISS_KEYS) - 1  # eyes closed in the kiss
        her_spec = dict(ELEANOR_NPC, asleep=True) if lips_met else ELEANOR_NPC
        his_spec = dict(MICAH, asleep=True) if lips_met else MICAH

        def eleanor(near):
            arms = _arms("down")
            if near:
                arms[1] = near
            return figure(her_spec, pose(her_yaw, arms=arms, lean=her_lean, nod=her_nod), NPC_W, FH).transpose(flip)

        her = eleanor(her_arm and ("pts",) + her_arm)
        img.alpha_composite(her, (ex, -KISS_RISE))
        ps = pose(yaw, lean=lean, nod=nod)
        if arm:
            ps["arms"] = {1: ("pts",) + arm, -1: ("side", 0, 0, 0)}
        him = figure(his_spec, ps, FW, FH)
        img.alpha_composite(him, (mx0 + step, 0))

        def outside(fig, bare):  # the reaching arm, where it leaves the figure's own outline
            layer = Image.new("RGBA", fig.size)
            layer.paste(fig, mask=Image.eval(bare.getchannel("A"), lambda a: 255 if a == 0 else 0))
            return layer

        if her_arm:  # her reaching arm goes round his back in front of him ...
            img.alpha_composite(outside(her, eleanor(("side", 0, 0, 0))), (ex, -KISS_RISE))
        if arm:  # ... and his, round her waist, stays on top of hers where they cross
            ps["arms"][1] = ("side", 0, 0, 0)
            img.alpha_composite(outside(him, figure(his_spec, ps, FW, FH)), (mx0 + step, 0))
        frames.append((img, (anchor_x + step, 18)))
        seconds.append(duration)
    action_strip("micah_kiss", frames, seconds, anchor=(anchor_x, FH - 3))


# In the library, Micah grabs the librarian by the collar and drags him in: stopped facing right COLLAR_GAP pixels short
# of him (the librarian's WalkTo, his feet COLLAR_RISE pixels higher), he steps in, takes a fistful of shirt collar
# under the bow tie with his near hand and yanks him close, leaning back into the pull; the librarian, both feet still
# on the floor, stumbles a step towards him, pitched forward off balance with his hands up. micah_collar ends on the
# held grab (kept through the dialogue); micah_collar_release lets go and steps back while the librarian straightens
# and steps back, ending on both idle sprites exactly where they stood. Played on the player with the librarian actor
# hidden.
# (Micah step in, his yaw, lean, near arm (elbow, wrist, hand) or None, librarian yaw, lean, pull (pixels he is dragged
# towards Micah), his arms or None, seconds)
COLLAR_GAP, COLLAR_RISE, COLLAR_W = 46, 2, 136
_LIB_IDLE = dict(arms=_arms("fold"), lean=9.0, nod=0.006)
_GRIP_REACH = ((0.13, 0.31, 0.13), (0.1, 0.25, 0.25), (0.075, 0.235, 0.285))
_GRIP_PULL = ((0.12, 0.35, 0.06), (0.09, 0.27, 0.17), (0.065, 0.25, 0.2))
_GRIP = ((0.12, 0.37, 0.03), (0.09, 0.28, 0.13), (0.065, 0.26, 0.16))
_HANDS_UP = ((0.17, 0.36, 0.02), (0.18, 0.25, 0.06), (0.175, 0.22, 0.07))
_HANDS_HALF = ((0.16, 0.38, 0.04), (0.13, 0.32, 0.1), (0.12, 0.3, 0.11))
COLLAR_KEYS = [
    (0, PLAYER_IDLE_YAW, 0.0, None, 35, 9.0, 0, None, 0.2),
    (8, 80, 6.0, _GRIP_REACH, 50, 6.0, 0, _HANDS_HALF, 0.15),
    (10, 90, 0.0, _GRIP_PULL, 70, 12.0, 6, _HANDS_UP, 0.12),
    (10, 90, -3.0, _GRIP, 75, 14.0, 10, _HANDS_UP, 0.6),
]
COLLAR_RELEASE_KEYS = [
    (10, 90, -3.0, _GRIP, 75, 14.0, 10, _HANDS_UP, 0.2),
    (8, 80, 0.0, None, 60, 8.0, 5, _HANDS_HALF, 0.2),
    (4, 70, 0.0, None, 45, 7.0, 2, None, 0.25),
    (0, PLAYER_IDLE_YAW, 0.0, None, 35, 9.0, 0, None, 0.2),
]


def collar_frame(step, yaw, lean, arm, lib_yaw, lib_lean, pull, lib_arms):
    from PIL import Image
    mx0 = 20
    anchor_x = mx0 + FW // 2
    lx = anchor_x + COLLAR_GAP - NPC_W // 2 - pull
    img = Image.new("RGBA", (COLLAR_W, FH))
    if lib_arms is None:
        lib_pose = pose(lib_yaw, **dict(_LIB_IDLE, lean=lib_lean))
    else:
        near, far = ("pts",) + lib_arms, ("pts",) + tuple((-x, y, z) for x, y, z in lib_arms)
        # dragged off balance: a stumbling step towards Micah, both soles flat on the floor
        stride = min(pull, 10)
        legs = {1: (stride, 3, 0), -1: (-stride * 0.6, 5, 0)}
        lib_pose = pose(lib_yaw, arms={1: near, -1: far}, lean=lib_lean, nod=-0.004, legs=legs)
    lib = figure(LIBRARIAN, lib_pose, NPC_W, FH).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    img.alpha_composite(lib, (lx, -COLLAR_RISE))
    ps = pose(yaw, lean=lean)
    if arm:
        ps["arms"] = {1: ("pts",) + arm, -1: ("side", 0, 0, 0)}
    img.alpha_composite(figure(MICAH, ps, FW, FH), (mx0 + step, 0))
    return img, (anchor_x + step, 18)


def collar_strips():
    anchor = (20 + FW // 2, FH - 3)
    for name, keys in (("micah_collar", COLLAR_KEYS), ("micah_collar_release", COLLAR_RELEASE_KEYS)):
        frames = [collar_frame(*k[:-1]) for k in keys]
        action_strip(name, frames, [k[-1] for k in keys], anchor=anchor)


def inmate_seated_strip(spec, name):
    """seated_frame's pose (facing right, the same seat as micah_inmate_seated) with action-strip metadata."""
    ps = pose(90, legs={1: (88, 92, 0), -1: (86, 90, 0)}, arms={1: ("swing", 36, 4, 70), -1: ("swing", 30, 4, 74)})
    action_strip(name, [(figure(spec, ps, FW, FH), (FW / 2, 18))], [1], anchor=(FW / 2, FH - 3))


# Struck on the back of the head from behind, facing right: the head snaps forward and the hands fly up, he drops onto
# his knees, pitches forward and lies face-down with his arms flung out past his head. No wound.
STRUCK = [
    [(64, 57), (67, 34), (74, 23), (66, 74), (66, 91), (72, 45), (78, 54)],
    KNEES_PRONE[0],
    KNEES_PRONE[1],
    [(78, 83), (101, 83), (115, 83), (60, 83), (42, 83), (110, 90), (124, 91)],
]


BLOOD = ((86, 8, 12, 255), (116, 16, 20, 255), (146, 28, 28, 255))  # deep shadow, blood, wet highlight


def _head_wound(img, joints, head, i, last):
    """The candlestick's wound on the back of the bald head, blood running from it down the back of the neck, more
    as he goes down; on the floor (last) a small dark pool spreads under the head."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageChops
    shoulder, head = np.array(grounded_joints(joints)[1], float), np.array(head, float)
    up = (head - shoulder) / np.linalg.norm(head - shoulder)
    fwd = np.array([-up[1], up[0]])  # facing right: the face is on this side of the skull
    w = head - fwd * 3.6 - up * 1.2
    r = (1.4, 1.8, 2.2, 2.5)[min(i, 3)]
    blood = Image.new("RGBA", img.size)
    d = ImageDraw.Draw(blood)
    reach = (0.4, 0.6, 0.8, 0.95)[min(i, 3)]
    end = w + (shoulder - fwd * 1.5 - w) * reach
    d.line([tuple(w), tuple(end)], fill=BLOOD[1], width=2 if i >= 2 else 1)
    d.line([tuple(w - fwd * 0.6), tuple(w + (end - w) * 0.6 - fwd * 0.6)], fill=BLOOD[0], width=1)
    d.ellipse([w[0] - r, w[1] - r, w[0] + r, w[1] + r], fill=BLOOD[0])
    d.ellipse([w[0] - r * 0.55, w[1] - r * 0.55, w[0] + r * 0.45, w[1] + r * 0.45], fill=BLOOD[1])
    d.point((round(w[0] - 0.5), round(w[1] - 1)), fill=BLOOD[2])
    if last:  # running off the side of the head to the floor
        d.line([(w[0] + 1, w[1] + 1), (w[0] + 2, 92)], fill=BLOOD[1], width=1)
    blood.putalpha(ImageChops.multiply(blood.getchannel("A"), img.getchannel("A")))
    img.alpha_composite(blood)
    if not last:
        return img
    hx = head[0]
    pool = Image.new("RGBA", img.size)
    pd = ImageDraw.Draw(pool)
    pd.ellipse([hx - 10, 88, hx + 9, 94], fill=BLOOD[0])
    pool.alpha_composite(img)
    seep = Image.new("RGBA", img.size)
    sd = ImageDraw.Draw(seep)
    sd.ellipse([hx - 8, 91, hx + 10, 94], fill=BLOOD[0])
    sd.ellipse([hx - 4, 91, hx + 5, 93], fill=BLOOD[1])
    sd.point((round(hx + 1), 92), fill=BLOOD[2])
    pool.alpha_composite(seep)
    return pool


def struck_strip(spec, name, final_name, arms):
    """Hit on the back of the head: he staggers, drops to his knees and falls forward face-down. The wound bleeds
    from the hit on, and a small pool spreads under his head once he's down."""
    scaled = dict(spec, h=spec["h"] * SCALE)
    frames = [npc_standing(spec, arms)]
    for i, joints in enumerate(STRUCK):
        img, head = action_figure(scaled, joints)
        frames.append((_head_wound(img, joints, head, i, i == len(STRUCK) - 1), head))
    action_strip(name, frames, [0.1, 0.12, 0.3, 0.18, 0.3])
    action_strip(final_name, [frames[-1]], [1])
    return frames


def build():
    player_sheet(MICAH, "micah")
    player_sheet(DANIEL, "daniel")
    player_sheet(MICAH_DRESSING, "micah_dressing")
    kneel_frame(MICAH, "micah_kneel")
    kicked_strip(MICAH, "micah_kicked")
    kick_strip(SAL, "sal_kick", _arms("pocket"))
    player_sheet(MICAH_MASKED, "micah_masked")
    supine_frame(MICAH, "micah_supine")
    aim_frame(MICAH, "micah_aim")
    aim_lower_strip(MICAH, "micah_aim_lower")
    aim_back_strip(MICAH, "micah_aim_back")
    aim_self_frame(MICAH, "micah_aim_self")
    draw_strip(MICAH, "micah_draw")
    action_sequences(MICAH, "micah")
    action_sequences(MICAH_MASKED, "micah_masked")
    door_strip(MICAH, "micah_open_door", PLAYER_IDLE_YAW)
    build_no_tie()
    door_strip(TEDDY, "teddy_open_door", 35)
    teddy_cash_strips()
    door_strip(ROSE, "rose_open_door", 20)
    build_drinking()
    build_gin()
    build_show_photo()
    build_show_photo_back()
    tie_pull_strips()
    build_smoke()
    for name, spec, arms, *extra in NPCS:
        npc_strip(spec, name, arms, **(extra[0] if extra else {}))
    # Rose on her doorstep, square to the camera once the door is open
    npc_strip(ROSE, "rose_front", _arms("fold"), phi=0)
    player_sheet(ELEANOR, "eleanor_play")
    player_sheet(ELEANOR_GOWN, "eleanor_gown_play")
    player_sheet(ELEANOR_SHEET, "eleanor_sheet_play", arms=_arms("clutch"))
    eleanor_drink_strip()
    eleanor_phone_strips()
    eleanor_bag_sheets()
    kiss_strip()
    collar_strips()
    build_act3()
    build_storm()


# The poses Micah strikes after he leaves his tie on the mansion's alarm bell; Player loads these instead of the
# shared micah_* strips while he wears the micah_no_tie sheet.
NO_TIE_POSES = ("crouch", "crouched", "crouch_rise", "aim", "aim_lower", "aim_back", "aim_self", "draw")


def build_no_tie():
    player_sheet(MICAH_NO_TIE, "micah_no_tie")
    aim_frame(MICAH_NO_TIE, "micah_no_tie_aim")
    aim_lower_strip(MICAH_NO_TIE, "micah_no_tie_aim_lower")
    aim_back_strip(MICAH_NO_TIE, "micah_no_tie_aim_back")
    aim_self_frame(MICAH_NO_TIE, "micah_no_tie_aim_self")
    draw_strip(MICAH_NO_TIE, "micah_no_tie_draw")
    action_sequences(MICAH_NO_TIE, "micah_no_tie")


def build_act3():
    fall_strip(SAL, "sal_knockout", "sal_out", _arms("pocket"))
    shoulder_shot_strip(BARTENDER, "bartender_fall", "bartender_shot", _arms("down"))
    fall_strip(HARRINGTON_GOWN, "harrington_fall", "harrington_shot", _arms("down", "pocket"))
    fall_strip(dict(ELEANOR_SHEET_NPC, drape=dict(col=ELEANOR_SHEET["torso"])), "eleanor_fall", "eleanor_shot", _arms("clutch"),
               wound=True)
    struck_strip(HARRINGTON_GOWN, "harrington_struck", "harrington_struck_down", _arms("down", "pocket"))
    eleanor_strike_strip()
    seated_frame(MICAH_INMATE, "micah_inmate_seated")
    inmate_seated_strip(ELEANOR_INMATE_NPC, "eleanor_inmate_seated")
    seated_frame(ELEANOR_NPC, "eleanor_seated", flip=True)
    seated_frame(CALEB, "caleb_seated", flip=True)
    seated_frame(ROSE, "rose_seated", flip=True)


# ---------------------------------------------------------------------------------------------------------------------
# The storm in the office after the alley: hatless Micah with the whiskey bottle, drinking at the window, setting the
# bottle down on the desk, then putting his hat back on. Seen from behind (facing the window and the desk).
# ---------------------------------------------------------------------------------------------------------------------
STORM_BOTTLE_ARM = -1  # the bottle hand
STORM_HAT_ARM = 1      # the hand that takes the fedora
STORM_PHI = 164        # the back view of the player sheet


def _storm_pose(arm_pts=None, hat_pts=None, bottle=None, hat=None, grip=0.0, **kw):
    """A back-view frame; arm_pts/hat_pts: (elbow, wrist, hand) in the body frame for the bottle/hat arm (x is
    mirrored to the arm's side), else that arm hangs down. bottle: the bottle's direction, or True along the forearm."""
    arms, behind = {1: ("swing", 3, 6, 10), -1: ("swing", 3, 6, 10)}, []
    for s, pts in ((STORM_BOTTLE_ARM, arm_pts), (STORM_HAT_ARM, hat_pts)):
        if pts:
            arms[s] = ("pts",) + tuple([s * x, y, z] for x, y, z in pts)
            behind.append(s)
    ps = pose(STORM_PHI, arms=arms, behind_arms=tuple(behind), **kw)
    if bottle is not None:
        ps["bottle"] = (STORM_BOTTLE_ARM, None if bottle is True else bottle)
        if arm_pts:
            ps["bottle_z"] = 1.4
    if hat is not None:
        ps["held_hat"] = (STORM_HAT_ARM, hat)
        # over the arm (its hand hidden under the hat); in front of the head only once it's raised over it
        ps["hat_z"] = 1.6 if hat_pts[2][1] > 0.1 else 2.95
        ps["hat_hand_behind"] = True
        ps["hat_grip"] = grip
    return ps


# Seen from behind, the raised arms are drawn behind the back: only the elbows and what sticks out past him show.
AT_SIDE = ((0.2, 0.39, 0.04), (0.09, 0.32, 0.12), (0.06, 0.3, 0.14))
AT_MOUTH = ((0.22, 0.22, 0.06), (0.1, 0.17, 0.1), (0.06, 0.16, 0.1))
ON_DESK = ((0.2, 0.37, 0.08), (0.15, 0.31, 0.22), (0.13, 0.3, 0.26))
HAT_SIDE = ((0.2, 0.39, 0.04), (0.09, 0.31, 0.1), (0.06, 0.28, 0.12))
HAT_UP = ((0.21, 0.17, 0.0), (0.13, 0.06, 0.0), (0.1, 0.03, 0.0))
HAT_BRIM = ((0.21, 0.22, 0.02), (0.09, 0.11, 0.03), (0.06, 0.08, 0.02))


def build_storm():
    player_sheet(MICAH_HATLESS, "micah_hatless_bottle", props=dict(bottle=STORM_BOTTLE_ARM))
    head = (FW / 2, 18)

    def strip(name, keys):
        frames = [(figure(spec, ps, FW, FH), head) for spec, ps, _ in keys]
        action_strip(name, frames, [t for *_, t in keys], anchor=(FW / 2, FH - 3))

    hanging = _storm_pose(bottle=True)
    chest = _storm_pose(AT_SIDE, bottle=(0.1, 1, 0))
    # the neck at his lips, the bottle tipped up over his shoulder past the back of his head
    mouth = _storm_pose(AT_MOUTH, bottle=(STORM_BOTTLE_ARM * 0.8, -0.6, 0.1), nod=-0.01)
    strip("micah_hatless_bottle_drink", [(MICAH_HATLESS, hanging, 0.25), (MICAH_HATLESS, chest, 0.18),
                                         (MICAH_HATLESS, mouth, 1.3), (MICAH_HATLESS, chest, 0.2),
                                         (MICAH_HATLESS, hanging, 0.3)])
    strip("micah_hatless_bottle_set", [(MICAH_HATLESS, hanging, 0.2), (MICAH_HATLESS, chest, 0.16),
                                       (MICAH_HATLESS, _storm_pose(ON_DESK, bottle=(0, 1, 0)), 0.45),
                                       (MICAH_HATLESS, _storm_pose(ON_DESK), 0.25),
                                       (MICAH_HATLESS, _storm_pose(), 0.3)])
    strip("micah_hatless_hat_on", [(MICAH_HATLESS, _storm_pose(hat_pts=ON_DESK, hat=(-0.01, 0.0)), 0.35),
                                   (MICAH_HATLESS, _storm_pose(hat_pts=HAT_SIDE, hat=(-0.01, 0.0)), 0.2),
                                   (MICAH_HATLESS, _storm_pose(hat_pts=HAT_UP, hat=(-0.01, 0.0), grip=0.09), 0.3),
                                   (MICAH, _storm_pose(hat_pts=HAT_BRIM), 0.35),
                                   (MICAH, pose(STORM_PHI), 0.3)])
