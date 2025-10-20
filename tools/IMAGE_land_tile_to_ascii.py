"""
UO IMAGE ANALYZER - LAND TILES & STATIC ITEMS

analyze exported images to determine average color and closest hue ID from ultima online font palette 
used with UI_ascii_display.py to display each entry as gump lable ascii character colorized by the limited font colors

FEATURES:
- Supports both LAND TILES and STATIC ITEMS (toggle via GUI)
- Calculates average RGB color (excludes translucent/dark pixels)
- Matches to closest UO hue ID using  game hue data (the 906 base "dyeable" hues)
- Exports compact dict format: 10 entries per row for readability ( this is what we paste into UI_ascii_display.py )

MODES:
1. LAND TILES - Analyzes terrain/ground tiles
   - Input: D:\\ULTIMA\\MODS\\UOFiddler\\EXPORTS\\LANDTILES
   - Output: land_tile_hues_compact_*.txt
   - Example: "Landtile 0x000A.png"

2. STATIC ITEMS - Analyzes item/object images
   - Input: D:\\ULTIMA\\MODS\\UOFiddler\\EXPORTS\\ART_Unchained
   - Output: static_item_hues_compact_*.txt
   - Example: "Item 0x26BC.png" or "0x26BC.png"

OUTPUT FORMAT:
- this output is used by scripts like UI_ascii_display.py 
LAND_TILE_HUES = {
    0x0000: 2, 0x0001: 88, 0x0002: 68, ... (10 per row)
}

STATIC_ITEM_HUES = {
    0x0001: 42, 0x0002: 156, 0x0003: 88, ... (10 per row)
}

VERSION: 20251018
"""

import os
import json
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import colorsys
import math
from collections import Counter

DEFAULT_LANDTILES_DIR = r"D:\ULTIMA\MODS\UOFiddler\EXPORTS\LANDTILES"
DEFAULT_STATICS_DIR = r"D:\ULTIMA\MODS\UOFiddler\EXPORTS\ART_S"
DEFAULT_OUTPUT_DIR = r"D:\ULTIMA\SCRIPTS\RazorEnhanced_Python\data"

# Image analysis settings
MIN_BRIGHTNESS = 5  # Exclude pixels with brightness below this (0-255)
MIN_ALPHA = 128     # Exclude pixels with alpha below this (0-255)

# Dark mode color scheme
DARK_BG = '#2b2b2b'          # Dark gray background
DARK_FG = '#ffffff'          # White text
DARK_ENTRY_BG = '#3c3c3c'    # Slightly lighter for input fields
DARK_BUTTON_BG = '#404040'   # Button background
DARK_FRAME_BG = '#333333'    # Frame background
DARK_HIGHLIGHT = '#505050'   # Highlight color

# ASCII character suggestions based on visual patterns
# currently not used , only some character are specifically overitten , but we should use more of these 
ASCII_PATTERN_CHARS = {
    "smooth": [".", ",", "'", "`"],
    "textured": [":", ";", "~", "≈"],
    "rough": ["#", "*", "+", "x"],
    "sparse": [".", "°", "·", "˙"],
    "dense": ["█", "▓", "▒", "░"],
    "wavy": ["~", "≈", "∼", "≋"],
    "diagonal": ["/", "\\", "╱", "╲"],
    "cross": ["+", "×", "✕", "✖"],
}

# ============================================================================
# UO HUE PALETTE SYSTEM 
# using the base dye palette 2-906 , roughly repeating hue each 100 , becoming more desaturated and brighter each set
# Format: hue_id: (r, g, b)
ULTIMA_ONLINE_HUE_ID_PALETTE = {
    1:(0,0,8),2:(0,0,184),3:(0,0,232),4:(48,48,232),5:(96,96,240),6:(144,144,240),7:(56,0,184),8:(72,0,232),9:(104,48,232),10:(144,96,240),
    11:(176,144,240),12:(104,0,184),13:(136,0,232),14:(160,48,232),15:(176,96,240),16:(200,144,240),17:(160,0,184),18:(208,0,232),19:(216,48,232),20:(224,96,240),
    21:(232,144,240),22:(184,0,144),23:(232,0,184),24:(232,48,192),25:(240,96,208),26:(240,144,216),27:(184,0,88),28:(232,0,112),29:(232,48,144),30:(240,96,168),
    31:(240,144,192),32:(184,0,40),33:(232,0,48),34:(232,48,88),35:(240,96,128),36:(240,144,168),37:(184,16,0),38:(232,24,0),39:(232,72,48),40:(240,112,96),
    41:(240,160,144),42:(184,72,0),43:(232,96,0),44:(232,128,48),45:(240,152,96),46:(240,184,144),47:(184,128,0),48:(232,160,0),49:(232,176,48),50:(240,192,96),
    51:(240,208,144),52:(184,184,0),53:(232,232,0),54:(232,232,48),55:(240,240,96),56:(240,240,144),57:(128,184,0),58:(160,232,0),59:(176,232,48),60:(192,240,96),
    61:(208,240,144),62:(72,184,0),63:(96,232,0),64:(128,232,48),65:(152,240,96),66:(184,240,144),67:(16,184,0),68:(24,232,0),69:(72,232,48),70:(112,240,96),
    71:(160,240,144),72:(0,184,40),73:(0,232,48),74:(48,232,88),75:(96,240,128),76:(144,240,168),77:(0,184,88),78:(0,232,120),79:(48,232,144),80:(96,240,168),
    81:(144,240,192),82:(0,184,144),83:(0,232,184),84:(48,232,192),85:(96,240,208),86:(144,240,216),87:(0,160,184),88:(0,208,232),89:(48,216,232),90:(96,224,240),
    91:(144,232,240),92:(0,104,184),93:(0,136,232),94:(48,160,232),95:(96,176,240),96:(144,200,240),97:(0,56,184),98:(0,72,232),99:(48,104,232),100:(96,144,240),
    101:(144,176,240),102:(8,8,176),103:(16,16,216),104:(56,56,224),105:(104,104,232),106:(152,152,232),107:(64,8,176),108:(80,16,216),109:(112,56,224),110:(144,104,232),
    111:(176,152,232),112:(104,8,176),113:(136,16,216),114:(160,56,224),115:(176,104,232),116:(200,152,232),117:(152,8,176),118:(192,16,216),119:(208,56,224),120:(216,104,232),
    121:(224,152,232),122:(176,8,136),123:(216,16,176),124:(224,56,184),125:(232,104,200),126:(232,152,216),127:(176,8,88),128:(216,16,112),129:(224,56,144),130:(232,104,168),
    131:(232,152,192),132:(176,8,48),133:(216,16,56),134:(224,56,96),135:(232,104,136),136:(232,152,168),137:(176,24,8),138:(216,40,16),139:(224,80,56),140:(232,120,104),
    141:(232,160,152),142:(176,72,8),143:(216,96,16),144:(224,128,56),145:(232,160,104),146:(232,184,152),147:(176,120,8),148:(216,152,16),149:(224,168,56),150:(232,192,104),
    151:(232,208,152),152:(176,176,8),153:(216,216,16),154:(224,224,56),155:(232,232,104),156:(232,232,152),157:(120,176,8),158:(152,216,16),159:(168,224,56),160:(192,232,104),
    161:(208,232,152),162:(72,176,8),163:(96,216,16),164:(128,224,56),165:(160,232,104),166:(184,232,152),167:(24,176,8),168:(40,216,16),169:(80,224,56),170:(120,232,104),
    171:(160,232,152),172:(8,176,48),173:(16,216,56),174:(56,224,96),175:(104,232,136),176:(152,232,168),177:(8,176,88),178:(16,216,120),179:(56,224,144),180:(104,232,168),
    181:(152,232,192),182:(8,176,136),183:(16,216,176),184:(56,224,184),185:(104,232,200),186:(152,232,216),187:(8,152,176),188:(16,192,216),189:(56,208,224),190:(104,216,232),
    191:(152,224,232),192:(8,104,176),193:(16,136,216),194:(56,160,224),195:(104,176,232),196:(152,200,232),197:(8,64,176),198:(16,80,216),199:(56,112,224),200:(104,144,232),
    201:(152,176,232),202:(16,16,160),203:(24,24,208),204:(72,72,216),205:(112,112,224),206:(160,160,232),207:(64,16,160),208:(80,24,208),209:(112,72,216),210:(144,112,224),
    211:(176,160,232),212:(104,16,160),213:(136,24,208),214:(152,72,216),215:(176,112,224),216:(200,160,224),217:(144,16,160),218:(184,24,208),219:(200,72,216),220:(208,112,224),
    221:(224,160,232),222:(160,16,128),223:(208,24,168),224:(216,72,184),225:(224,112,200),226:(232,160,216),227:(160,16,88),228:(208,24,112),229:(216,72,144),230:(224,112,168),
    231:(232,160,192),232:(160,16,48),233:(208,24,64),234:(216,72,104),235:(224,112,136),236:(232,160,176),237:(160,32,16),238:(208,48,24),239:(216,88,72),240:(224,128,112),
    241:(232,168,160),242:(160,80,16),243:(208,96,24),244:(216,128,72),245:(224,160,112),246:(232,184,160),247:(160,120,16),248:(208,152,24),249:(216,168,72),250:(224,184,112),
    251:(232,208,160),252:(160,160,16),253:(208,208,24),254:(216,216,72),255:(224,224,112),256:(232,232,160),257:(120,160,16),258:(152,208,24),259:(168,216,72),260:(184,224,112),
    261:(208,232,160),262:(80,160,16),263:(96,208,24),264:(128,216,72),265:(160,224,112),266:(184,232,160),267:(32,160,16),268:(48,208,24),269:(88,216,72),270:(128,224,112),
    271:(168,232,160),272:(16,160,48),273:(24,208,64),274:(72,216,104),275:(112,224,136),276:(160,232,176),277:(16,160,88),278:(24,208,120),279:(72,216,144),280:(112,224,168),
    281:(160,232,192),282:(16,160,128),283:(24,208,168),284:(72,216,184),285:(112,224,200),286:(160,232,216),287:(16,144,160),288:(24,184,208),289:(72,200,216),290:(112,208,224),
    291:(160,224,232),292:(16,104,160),293:(24,136,208),294:(72,152,216),295:(112,176,224),296:(160,200,232),297:(16,64,160),298:(24,80,208),299:(72,112,216),300:(112,144,224),
    301:(160,176,232),302:(32,32,152),303:(40,40,192),304:(80,80,200),305:(120,120,216),306:(168,168,224),307:(72,32,152),308:(88,40,192),309:(120,80,200),310:(152,120,216),
    311:(184,168,224),312:(104,32,152),313:(128,40,192),314:(152,80,200),315:(176,120,216),316:(200,168,224),317:(136,32,152),318:(176,40,192),319:(192,80,200),320:(200,120,216),
    321:(216,168,224),322:(152,32,128),323:(192,40,160),324:(200,80,176),325:(216,120,192),326:(224,168,208),327:(152,32,88),328:(192,40,112),329:(200,80,144),330:(216,120,168),
    331:(224,168,192),332:(152,32,56),333:(192,40,72),334:(200,80,104),335:(216,120,144),336:(224,168,176),337:(152,40,32),338:(192,56,40),339:(200,96,80),340:(216,128,120),
    341:(224,168,160),342:(152,80,32),343:(192,104,40),344:(200,128,80),345:(216,160,120),346:(224,184,160),347:(152,112,32),348:(192,144,40),349:(200,160,80),350:(216,184,120),
    351:(224,208,160),352:(152,152,32),353:(192,192,40),354:(200,200,80),355:(216,216,120),356:(224,224,160),357:(112,152,32),358:(144,192,40),359:(168,200,80),360:(184,216,120),
    361:(208,224,160),362:(80,152,32),363:(104,192,40),364:(128,200,80),365:(160,216,120),366:(184,224,160),367:(40,152,32),368:(56,192,40),369:(96,200,80),370:(128,216,120),
    371:(168,224,160),372:(32,152,56),373:(40,192,72),374:(80,200,104),375:(120,216,144),376:(160,224,176),377:(32,152,88),378:(40,192,120),379:(80,200,144),380:(120,216,168),
    381:(160,224,192),382:(32,152,128),383:(40,192,160),384:(80,200,176),385:(120,216,192),386:(160,224,208),387:(32,136,152),388:(40,176,192),389:(80,192,200),390:(120,200,216),
    391:(160,216,224),392:(32,104,152),393:(40,128,192),394:(80,152,200),395:(120,176,216),396:(160,200,224),397:(32,64,152),398:(40,88,192),399:(80,120,200),400:(120,152,216),
    401:(160,184,224),402:(40,40,144),403:(48,48,184),404:(88,88,192),405:(128,128,208),406:(168,168,216),407:(72,40,144),408:(96,48,184),409:(120,88,192),410:(152,128,208),
    411:(184,168,216),412:(96,40,144),413:(128,48,184),414:(152,88,192),415:(176,128,208),416:(200,168,216),417:(128,40,144),418:(168,48,184),419:(184,88,192),420:(200,128,208),
    421:(216,168,216),422:(144,40,120),423:(184,48,152),424:(192,88,168),425:(208,128,192),426:(216,168,208),427:(144,40,88),428:(184,48,112),429:(192,88,144),430:(208,128,168),
    431:(216,168,192),432:(144,40,64),433:(184,48,80),434:(192,88,120),435:(208,128,152),436:(216,168,184),437:(144,48,40),438:(184,64,48),439:(192,104,88),440:(208,136,128),
    441:(216,176,168),442:(144,80,40),443:(184,104,48),444:(192,136,88),445:(208,160,128),446:(216,192,168),447:(144,112,40),448:(184,136,48),449:(192,160,88),450:(208,184,128),
    451:(216,200,168),452:(144,144,40),453:(176,184,48),454:(192,192,88),455:(208,208,128),456:(216,216,168),457:(112,144,40),458:(136,184,48),459:(160,192,88),460:(184,208,128),
    461:(200,216,168),462:(80,144,40),463:(104,184,48),464:(136,192,88),465:(160,208,128),466:(192,216,168),467:(48,144,40),468:(64,184,48),469:(104,192,88),470:(136,208,128),
    471:(176,216,168),472:(40,144,64),473:(48,184,80),474:(88,192,112),475:(128,208,144),476:(168,216,176),477:(40,144,88),478:(48,184,120),479:(88,192,144),480:(128,208,168),
    481:(168,216,192),482:(40,144,120),483:(48,184,152),484:(88,192,168),485:(128,208,192),486:(168,216,208),487:(40,128,144),488:(48,168,184),489:(88,184,192),490:(128,200,208),
    491:(168,216,216),492:(40,96,144),493:(48,128,184),494:(88,152,192),495:(128,176,208),496:(168,200,216),497:(40,72,144),498:(48,96,184),499:(88,120,192),500:(128,152,208),
    501:(168,184,216),502:(48,48,128),503:(64,64,168),504:(104,104,184),505:(136,136,200),506:(176,176,216),507:(72,48,128),508:(96,64,168),509:(128,104,184),510:(152,136,200),
    511:(184,176,216),512:(96,48,128),513:(128,64,168),514:(152,104,184),515:(176,136,200),516:(200,176,216),517:(120,48,128),518:(152,64,168),519:(176,104,184),520:(192,136,200),
    521:(208,176,216),522:(128,48,112),523:(168,64,144),524:(184,104,168),525:(200,136,184),526:(216,176,208),527:(128,48,88),528:(168,64,112),529:(184,104,144),530:(200,136,168),
    531:(216,176,192),532:(128,48,64),533:(168,64,88),534:(184,104,120),535:(200,136,152),536:(216,176,184),537:(128,56,48),538:(168,80,64),539:(184,112,104),540:(200,144,136),
    541:(216,176,176),542:(128,80,48),543:(168,104,64),544:(184,136,104),545:(200,160,136),546:(216,192,176),547:(128,104,48),548:(168,136,64),549:(184,160,104),550:(200,176,136),
    551:(216,200,176),552:(128,128,48),553:(168,168,64),554:(184,184,104),555:(200,200,136),556:(216,216,176),557:(104,128,48),558:(136,168,64),559:(160,184,104),560:(176,200,136),
    561:(200,216,176),562:(80,128,48),563:(104,168,64),564:(136,184,104),565:(160,200,136),566:(192,216,176),567:(56,128,48),568:(80,168,64),569:(112,184,104),570:(144,200,136),
    571:(176,216,176),572:(48,128,64),573:(64,168,88),574:(104,184,120),575:(136,200,152),576:(176,216,184),577:(48,128,88),578:(64,168,120),579:(104,184,144),580:(136,200,168),
    581:(176,216,192),582:(48,128,112),583:(64,168,144),584:(104,184,168),585:(136,200,184),586:(176,216,208),587:(48,112,128),588:(64,152,168),589:(104,176,184),590:(136,192,200),
    591:(176,208,216),592:(48,96,128),593:(64,128,168),594:(104,152,184),595:(136,176,200),596:(176,200,216),597:(48,80,128),598:(64,104,168),599:(104,136,184),600:(136,152,200),
    601:(176,184,216),602:(56,56,120),603:(80,80,152),604:(112,112,176),605:(144,144,192),606:(176,176,208),607:(80,56,120),608:(104,80,152),609:(128,112,176),610:(160,144,192),
    611:(184,176,208),612:(96,56,120),613:(120,80,152),614:(144,112,176),615:(168,144,192),616:(192,176,208),617:(112,56,120),618:(144,80,152),619:(168,112,176),620:(184,144,192),
    621:(208,176,208),622:(120,56,104),623:(152,80,136),624:(176,112,160),625:(192,144,184),626:(208,176,200),627:(120,56,88),628:(152,80,112),629:(176,112,144),630:(192,144,168),
    631:(208,176,192),632:(120,56,72),633:(152,80,96),634:(176,112,128),635:(192,144,152),636:(208,176,184),637:(120,64,56),638:(152,88,80),639:(176,120,112),640:(192,152,144),
    641:(208,184,176),642:(120,88,56),643:(152,112,80),644:(176,136,112),645:(192,160,144),646:(208,192,176),647:(120,104,56),648:(152,128,80),649:(176,152,112),650:(192,176,144),
    651:(208,200,176),652:(120,120,56),653:(152,152,80),654:(176,176,112),655:(192,192,144),656:(208,208,176),657:(104,120,56),658:(128,152,80),659:(152,176,112),660:(176,192,144),
    661:(200,208,176),662:(88,120,56),663:(112,152,80),664:(136,176,112),665:(160,192,144),666:(192,208,176),667:(64,120,56),668:(88,152,80),669:(120,176,112),670:(152,192,144),
    671:(184,208,176),672:(56,120,72),673:(80,152,96),674:(112,176,128),675:(144,192,152),676:(176,208,184),677:(56,120,88),678:(80,152,120),679:(112,176,144),680:(144,192,168),
    681:(176,208,192),682:(56,120,104),683:(80,152,136),684:(112,176,160),685:(144,192,184),686:(176,208,200),687:(56,112,120),688:(80,144,152),689:(112,168,176),690:(144,184,192),
    691:(176,208,208),692:(56,96,120),693:(80,120,152),694:(112,144,176),695:(144,168,192),696:(176,192,208),697:(56,80,120),698:(80,104,152),699:(112,136,176),700:(144,160,192),
    701:(176,184,208),702:(72,72,112),703:(88,88,144),704:(120,120,160),705:(152,152,184),706:(184,184,200),707:(80,72,112),708:(104,88,144),709:(136,120,160),710:(160,152,184),
    711:(192,184,200),712:(96,72,112),713:(120,88,144),714:(144,120,160),715:(168,152,184),717:(104,72,112),718:(136,88,144),719:(160,120,160),720:(176,152,184),721:(200,184,200),
    722:(112,72,104),723:(144,88,128),724:(160,120,152),725:(184,152,176),727:(112,72,88),728:(144,88,112),729:(160,120,144),730:(184,152,168),731:(200,184,192),732:(112,72,80),
    733:(144,88,104),734:(160,120,128),735:(184,152,160),736:(200,184,184),737:(112,72,72),738:(144,96,88),739:(160,128,120),740:(184,152,152),742:(112,88,72),743:(144,112,88),
    744:(160,136,120),745:(184,168,152),746:(200,192,184),747:(112,96,72),748:(144,128,88),749:(160,152,120),750:(184,176,152),751:(200,200,184),752:(112,112,72),753:(144,144,88),
    754:(160,160,120),755:(184,184,152),757:(96,112,72),758:(128,144,88),759:(152,160,120),760:(176,184,152),762:(88,112,72),763:(112,144,88),764:(136,160,120),765:(168,184,152),
    766:(192,200,184),767:(72,112,72),768:(96,144,88),769:(128,160,120),770:(152,184,152),771:(184,200,184),772:(72,112,80),773:(88,144,104),774:(120,160,128),775:(152,184,160),
    777:(72,112,88),778:(88,144,120),779:(120,160,144),780:(152,184,168),781:(184,200,192),782:(72,112,104),783:(88,144,128),784:(120,160,152),785:(152,184,176),786:(184,200,200),
    787:(72,104,112),788:(88,136,144),789:(120,160,160),790:(152,176,184),792:(72,96,112),793:(88,120,144),794:(120,144,160),795:(152,168,184),796:(184,192,200),797:(72,80,112),
    798:(88,104,144),799:(120,136,160),800:(152,160,184),802:(80,80,104),803:(104,104,128),804:(128,128,152),805:(160,160,176),807:(88,80,104),808:(112,104,128),809:(136,128,152),
    810:(168,160,176),812:(96,80,104),813:(120,104,128),814:(144,128,152),818:(128,104,128),819:(152,128,152),820:(176,160,176),822:(104,80,96),823:(128,104,120),824:(152,128,144),
    825:(176,160,168),827:(104,80,88),828:(128,104,112),834:(152,128,136),835:(176,160,160),837:(104,80,80),838:(128,104,104),839:(152,136,128),842:(104,88,80),843:(128,112,104),
    845:(176,168,160),847:(104,96,80),848:(128,120,104),849:(152,144,128),852:(104,104,80),853:(128,128,104),854:(152,152,128),855:(176,176,160),857:(96,104,80),858:(120,128,104),
    859:(144,152,128),860:(168,176,160),862:(88,104,80),863:(112,128,104),864:(136,152,128),867:(80,104,80),868:(104,128,104),870:(160,176,160),872:(80,104,88),873:(104,128,112),
    874:(128,152,136),878:(104,128,120),879:(128,152,144),880:(160,176,168),882:(80,104,96),887:(80,96,104),888:(104,128,128),889:(128,152,152),890:(160,176,176),893:(104,120,128),
    894:(128,144,152),895:(160,168,176),897:(80,88,104),898:(104,112,128),899:(128,136,152),902:(88,88,88),903:(120,120,120),904:(144,144,144),905:(168,168,168),906:(192,192,192),
}

def generate_uo_hue_color_accurate(hue_id):
    """
    Get ACTUAL RGB color for UO hue ID from game data.
    Uses  hue values extracted from Ultima Online (hues 1-906).
    """
    # Return actual hue if it exists
    if hue_id in ULTIMA_ONLINE_HUE_ID_PALETTE:
        return ULTIMA_ONLINE_HUE_ID_PALETTE[hue_id]
    
    # Fallback for invalid hue IDs
    return (128, 128, 128)

def generate_uo_hue_name(hue_id):
    """Generate descriptive name for a hue based on its properties."""
    family_index = (hue_id - 1) // 5
    brightness_level = (hue_id - 1) % 5
    hue_angle = (240 + (family_index * 9)) % 360
    
    if hue_angle < 15 or hue_angle >= 345:
        base_color = "Red"
    elif hue_angle < 45:
        base_color = "Orange"
    elif hue_angle < 75:
        base_color = "Yellow"
    elif hue_angle < 105:
        base_color = "Lime"
    elif hue_angle < 135:
        base_color = "Green"
    elif hue_angle < 165:
        base_color = "Teal"
    elif hue_angle < 195:
        base_color = "Cyan"
    elif hue_angle < 225:
        base_color = "Blue"
    elif hue_angle < 255:
        base_color = "Indigo"
    elif hue_angle < 285:
        base_color = "Violet"
    elif hue_angle < 315:
        base_color = "Magenta"
    else:
        base_color = "Pink"
    
    brightness_names = ["Dark", "Bright", "Light", "Pale", "Mint"]
    modifier = brightness_names[brightness_level]
    
    return f"{modifier} {base_color}"

def calculate_color_distance(rgb1, rgb2):
    """Calculate Euclidean distance between two RGB colors."""
    return math.sqrt(
        (rgb1[0] - rgb2[0]) ** 2 +
        (rgb1[1] - rgb2[1]) ** 2 +
        (rgb1[2] - rgb2[2]) ** 2
    )

# Full palette cache 
UO_HUE_PALETTE = {}

def get_uo_hue_data(hue_id):
    """
    Get UO hue data with lazy loading.
    Uses  game hue data for accurate color matching.
    """
    if hue_id not in UO_HUE_PALETTE:
        UO_HUE_PALETTE[hue_id] = {
            'rgb': generate_uo_hue_color_accurate(hue_id),
            'name': generate_uo_hue_name(hue_id)
        }
    return UO_HUE_PALETTE[hue_id]


# ============================================================================
# COLOR ANALYSIS
# ============================================================================

def rgb_to_hsv(r, g, b):
    """Convert RGB (0-255) to HSV (0-1)"""
    return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

def get_brightness(r, g, b):
    """Calculate perceived brightness (0-255)"""
    return int(0.299 * r + 0.587 * g + 0.114 * b)

def rgb_to_uo_hue(r, g, b):
    """
    Find closest matching UO hue ID for given RGB color.
    Searches through all 906 base dyeable game hues.
    NO extrapolation - only matches to known available hues.
    EXCLUDES hue 1 (dark blue/black) as it's not useful for land tiles.
    """
    target_rgb = (r, g, b)
    
    # Find best match in actual hue data (2-906, excluding hue 1)
    best_hue = 2  # Start with hue 2 instead of 1
    min_distance = float('inf')
    
    for hue_id, hue_rgb in ULTIMA_ONLINE_HUE_ID_PALETTE.items():
        # Skip hue 1 - it's (0,0,8) dark blue/black, not useful for land tiles
        if hue_id == 1:
            continue
            
        distance = calculate_color_distance(target_rgb, hue_rgb)
        if distance < min_distance:
            min_distance = distance
            best_hue = hue_id
    
    return best_hue

def get_color_name(hue):
    """Get color name from UO hue number"""
    hue_data = get_uo_hue_data(hue)
    if hue_data:
        return hue_data['name']
    return f"Hue {hue}"

# ============================================================================
# IMAGE ANALYSIS
# ============================================================================

def analyze_image_colors(image_path, min_brightness=MIN_BRIGHTNESS, min_alpha=MIN_ALPHA):
    """Analyze image and return average color (excluding dark/transparent pixels)"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGBA')
        
        pixels = img.getdata()
        valid_pixels = []
        
        for pixel in pixels:
            r, g, b, a = pixel
            brightness = get_brightness(r, g, b)
            
            # Filter out translucent and dark pixels
            if a >= min_alpha and brightness >= min_brightness:
                valid_pixels.append((r, g, b))
        
        if not valid_pixels:
            return None
        
        # Calculate average color
        avg_r = sum(p[0] for p in valid_pixels) // len(valid_pixels)
        avg_g = sum(p[1] for p in valid_pixels) // len(valid_pixels)
        avg_b = sum(p[2] for p in valid_pixels) // len(valid_pixels)
        
        return {
            "rgb": (avg_r, avg_g, avg_b),
            "hex": f"#{avg_r:02X}{avg_g:02X}{avg_b:02X}",
            "brightness": get_brightness(avg_r, avg_g, avg_b),
            "valid_pixel_count": len(valid_pixels),
            "total_pixel_count": len(pixels),
            "coverage_percent": (len(valid_pixels) / len(pixels)) * 100
        }
    except Exception as e:
        return None

def analyze_image_pattern(image_path, min_brightness=MIN_BRIGHTNESS, min_alpha=MIN_ALPHA):
    """Analyze image texture and pattern characteristics"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGBA')
        width, height = img.size
        
        pixels = img.getdata()
        valid_pixels = []
        brightness_values = []
        
        for pixel in pixels:
            r, g, b, a = pixel
            brightness = get_brightness(r, g, b)
            
            if a >= min_alpha and brightness >= min_brightness:
                valid_pixels.append((r, g, b, brightness))
                brightness_values.append(brightness)
        
        if not valid_pixels:
            return None
        
        # Calculate variance (texture roughness)
        avg_brightness = sum(brightness_values) / len(brightness_values)
        variance = sum((b - avg_brightness) ** 2 for b in brightness_values) / len(brightness_values)
        std_dev = math.sqrt(variance)
        
        # Determine pattern type
        pattern_type = "smooth"
        if std_dev < 10:
            pattern_type = "smooth"
        elif std_dev < 25:
            pattern_type = "textured"
        elif std_dev < 50:
            pattern_type = "rough"
        else:
            pattern_type = "dense"
        
        # Check for specific patterns
        if avg_brightness < 80:
            pattern_type = "dense"
        elif avg_brightness > 200:
            pattern_type = "sparse"
        
        return {
            "pattern_type": pattern_type,
            "variance": variance,
            "std_dev": std_dev,
            "avg_brightness": avg_brightness,
            "suggested_chars": ASCII_PATTERN_CHARS.get(pattern_type, ["."])
        }
    except Exception as e:
        return None

def extract_land_id_from_filename(filename):
    """Extract land tile ID from filename (e.g., '0x0003.png' or 'Landtile 0x0003.png')"""
    # Remove extension
    name = os.path.splitext(filename)[0]
    
    # Try to find hex pattern
    import re
    hex_match = re.search(r'0x([0-9A-Fa-f]+)', name)
    if hex_match:
        hex_str = hex_match.group(1)
        return int(hex_str, 16)
    
    # Try decimal pattern
    dec_match = re.search(r'(\d+)', name)
    if dec_match:
        return int(dec_match.group(1))
    
    return None

def extract_item_id_from_filename(filename):
    """Extract item ID from filename (e.g., '0x26BC.png' or 'Item 0x26BC.png')"""  
    # Remove extension
    name = os.path.splitext(filename)[0]
    
    # Try to find hex pattern
    import re
    hex_match = re.search(r'0x([0-9A-Fa-f]+)', name)
    if hex_match:
        hex_str = hex_match.group(1)
        return int(hex_str, 16)
    
    # Try decimal pattern
    dec_match = re.search(r'(\d+)', name)
    if dec_match:
        return int(dec_match.group(1))
    
    return None

# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_land_tiles(image_dir, log_callback=None):
    """Process all land tile images in directory"""
    results = []
    
    if not os.path.exists(image_dir):
        if log_callback:
            log_callback(f"ERROR: Directory not found: {image_dir}")
        return results
    
    # Get all image files
    image_files = []
    for ext in ['*.png', '*.bmp', '*.jpg', '*.jpeg', '*.tif', '*.tiff']:
        import glob
        image_files.extend(glob.glob(os.path.join(image_dir, ext)))
        image_files.extend(glob.glob(os.path.join(image_dir, ext.upper())))
    
    if not image_files:
        if log_callback:
            log_callback(f"No image files found in: {image_dir}")
        return results
    
    if log_callback:
        log_callback(f"Found {len(image_files)} image files")
        log_callback("Processing...\n")
    
    for i, image_path in enumerate(image_files, 1):
        filename = os.path.basename(image_path)
        land_id = extract_land_id_from_filename(filename)
        
        if land_id is None:
            if log_callback:
                log_callback(f"[{i}/{len(image_files)}] Skipping {filename} - could not extract ID")
            continue
        
        # Analyze colors
        color_data = analyze_image_colors(image_path)
        if not color_data:
            if log_callback:
                log_callback(f"[{i}/{len(image_files)}] Skipping {filename} - no valid pixels")
            continue
        
        # Analyze patterns
        pattern_data = analyze_image_pattern(image_path)
        
        # Get UO hue approximation
        r, g, b = color_data["rgb"]
        uo_hue = rgb_to_uo_hue(r, g, b)
        color_name = get_color_name(uo_hue)
        
        # Suggest ASCII character
        suggested_char = "."
        if pattern_data:
            suggested_chars = pattern_data["suggested_chars"]
            suggested_char = suggested_chars[0] if suggested_chars else "."
        
        result = {
            "land_id_decimal": land_id,
            "land_id_hex": f"0x{land_id:04X}",
            "filename": filename,
            "rgb": color_data["rgb"],
            "hex_color": color_data["hex"],
            "brightness": color_data["brightness"],
            "uo_hue": uo_hue,
            "color_name": color_name,
            "pattern_type": pattern_data["pattern_type"] if pattern_data else "unknown",
            "suggested_char": suggested_char,
            "suggested_chars_alt": pattern_data["suggested_chars"] if pattern_data else [],
            "coverage_percent": round(color_data["coverage_percent"], 2),
            "texture_variance": round(pattern_data["variance"], 2) if pattern_data else 0,
        }
        
        results.append(result)
        
        if log_callback and i % 10 == 0:
            log_callback(f"Processed {i}/{len(image_files)} images...")
    
    if log_callback:
        log_callback(f"\nCompleted! Processed {len(results)} land tiles")
    
    return results

def process_static_items(image_dir, log_callback=None):
    """Process all static item images in directory"""
    results = []
    
    if not os.path.exists(image_dir):
        if log_callback:
            log_callback(f"ERROR: Directory not found: {image_dir}")
        return results
    
    # Get all image files
    image_files = []
    for ext in ['*.png', '*.bmp', '*.jpg', '*.jpeg', '*.tif', '*.tiff']:
        import glob
        image_files.extend(glob.glob(os.path.join(image_dir, ext)))
        image_files.extend(glob.glob(os.path.join(image_dir, ext.upper())))
    
    if not image_files:
        if log_callback:
            log_callback(f"No image files found in: {image_dir}")
        return results
    
    if log_callback:
        log_callback(f"Found {len(image_files)} image files")
        log_callback("Processing...\n")
    
    for i, image_path in enumerate(image_files, 1):
        filename = os.path.basename(image_path)
        item_id = extract_item_id_from_filename(filename)
        
        if item_id is None:
            if log_callback:
                log_callback(f"[{i}/{len(image_files)}] Skipping {filename} - could not extract ID")
            continue
        
        # Analyze colors
        color_data = analyze_image_colors(image_path)
        if not color_data:
            if log_callback:
                log_callback(f"[{i}/{len(image_files)}] Skipping {filename} - no valid pixels")
            continue
        
        # Analyze patterns
        pattern_data = analyze_image_pattern(image_path)
        
        # Get UO hue approximation
        r, g, b = color_data["rgb"]
        uo_hue = rgb_to_uo_hue(r, g, b)
        color_name = get_color_name(uo_hue)
        
        # Suggest ASCII character
        suggested_char = "."
        if pattern_data:
            suggested_chars = pattern_data["suggested_chars"]
            suggested_char = suggested_chars[0] if suggested_chars else "."
        
        result = {
            "item_id_decimal": item_id,
            "item_id_hex": f"0x{item_id:04X}",
            "filename": filename,
            "rgb": color_data["rgb"],
            "hex_color": color_data["hex"],
            "brightness": color_data["brightness"],
            "uo_hue": uo_hue,
            "color_name": color_name,
            "pattern_type": pattern_data["pattern_type"] if pattern_data else "unknown",
            "suggested_char": suggested_char,
            "suggested_chars_alt": pattern_data["suggested_chars"] if pattern_data else [],
            "coverage_percent": round(color_data["coverage_percent"], 2),
            "texture_variance": round(pattern_data["variance"], 2) if pattern_data else 0,
        }
        
        results.append(result)
        
        if log_callback and i % 50 == 0:
            log_callback(f"Processed {i}/{len(image_files)} images...")
    
    if log_callback:
        log_callback(f"\nCompleted! Processed {len(results)} static items")
    
    return results

def export_results_to_json(results, output_path, result_type="land_tiles"):
    """Export results to JSON file"""
    try:
        # Prepare export structure
        id_key = "item_id_decimal" if result_type == "static_items" else "land_id_decimal"
        export_data = {
            "export_info": {
                "tool": "IMAGE_land_tile_to_ascii.py",
                "version": "20251017",
                "type": result_type,
                "total_items": len(results),
                "uo_hue_palette_size": len(UO_HUE_PALETTE)
            },
            "analysis_settings": {
                "min_brightness": MIN_BRIGHTNESS,
                "min_alpha": MIN_ALPHA
            },
            result_type: results,
            "python_dict_format": {}
        }
        
        # Generate Python dictionary format for easy copy-paste
        python_dict = {}
        for result in results:
            item_id = result.get("item_id_decimal") or result.get("land_id_decimal")
            char = result["suggested_char"]
            hue = result["uo_hue"]
            python_dict[f"0x{item_id:04X}"] = f'("{char}", {hue})  # {result["color_name"]} - {result["pattern_type"]}'
        
        export_data["python_dict_format"] = python_dict
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return True
    except Exception as e:
        return False

def generate_python_code(results, result_type="land_tiles"):
    """Generate Python code snippet for ASCII dictionary"""
    dict_name = "STATIC_ITEM_HUES" if result_type == "static_items" else "LAND_ASCII"
    id_key = "item_id_decimal" if result_type == "static_items" else "land_id_decimal"
    
    lines = [f"# Generated {dict_name} mappings\n", f"{dict_name} = {{\n"]
    
    for result in sorted(results, key=lambda x: x[id_key]):
        item_id = result[id_key]
        char = result["suggested_char"]
        hue = result["uo_hue"]
        color_name = result["color_name"]
        pattern = result["pattern_type"]
        
        lines.append(f"    0x{item_id:04X}: (\"{char}\", {hue}),  # {color_name} - {pattern}\n")
    
    lines.append("}\n")
    return "".join(lines)

def generate_minimal_dict(results, result_type="land_tiles"):
    """Generate minimal Python dict with just id and hex_color"""
    dict_name = "STATIC_ITEM_COLORS" if result_type == "static_items" else "LAND_COLORS"
    id_key = "item_id_decimal" if result_type == "static_items" else "land_id_decimal"
    comment = "item_id" if result_type == "static_items" else "land_id"
    
    lines = [f"# Minimal color mapping ({comment}: hex_color)\n", f"{dict_name} = {{\n"]
    
    for result in sorted(results, key=lambda x: x[id_key]):
        item_id = result[id_key]
        hex_color = result["hex_color"]
        lines.append(f"    0x{item_id:04X}: \"{hex_color}\",\n")
    
    lines.append("}\n")
    return "".join(lines)

def generate_compact_hue_dict(results, result_type="land_tiles"):
    """Generate compact Python dict with just id: hue_id, 10 per row"""
    dict_name = "STATIC_ITEM_HUES" if result_type == "static_items" else "LAND_TILE_HUES"
    id_key = "item_id_decimal" if result_type == "static_items" else "land_id_decimal"
    comment = "item_id" if result_type == "static_items" else "land_id"
    
    lines = [f"# {dict_name.replace('_', ' ').title()} mapping ({comment}: hue_id)\n"]
    lines.append("# Format: 10 entries per row for compact viewing\n")
    lines.append(f"{dict_name} = {{\n")
    
    sorted_results = sorted(results, key=lambda x: x[id_key])
    
    for i in range(0, len(sorted_results), 10):
        chunk = sorted_results[i:i+10]
        line_parts = []
        
        for result in chunk:
            item_id = result[id_key]
            hue = result["uo_hue"]
            line_parts.append(f"0x{item_id:04X}: {hue}")
        
        # Join with commas and add trailing comma
        lines.append(f"    {', '.join(line_parts)},\n")
    
    lines.append("}\n")
    return "".join(lines)

def export_minimal_txt(results, output_path, result_type="land_tiles"):
    """Export minimal text file with id and hex_color only"""
    try:
        minimal_dict = generate_minimal_dict(results, result_type)
        with open(output_path, 'w') as f:
            f.write(minimal_dict)
        return True
    except Exception as e:
        return False

def export_compact_hue_txt(results, output_path, result_type="land_tiles"):
    """Export compact text file with id: hue_id, 10 per row"""
    try:
        compact_dict = generate_compact_hue_dict(results, result_type)
        with open(output_path, 'w') as f:
            f.write(compact_dict)
        return True
    except Exception as e:
        return False

# ============================================================================
# GUI APPLICATION
# ============================================================================

class LandTileAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Source Art to ASCII font hue id ")
        self.root.geometry("900x700")
        
        # Apply dark mode
        self.root.configure(bg=DARK_BG)
        self.setup_dark_mode_style()
        
        self.results = []
        self.current_mode = "land_tiles"  # or "static_items"
        
        # Create UI
        self.create_widgets()
    
    def setup_dark_mode_style(self):
        """Configure ttk styles for dark mode"""
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base for customization
        
        # Configure colors for all widgets
        style.configure('TFrame', background=DARK_BG)
        style.configure('TLabel', background=DARK_BG, foreground=DARK_FG)
        style.configure('TLabelFrame', background=DARK_BG, foreground=DARK_FG)
        style.configure('TLabelFrame.Label', background=DARK_BG, foreground=DARK_FG)
        style.configure('TButton', background=DARK_BUTTON_BG, foreground=DARK_FG, borderwidth=1)
        style.map('TButton', background=[('active', DARK_HIGHLIGHT)])
        style.configure('TEntry', fieldbackground=DARK_ENTRY_BG, foreground=DARK_FG, insertcolor=DARK_FG)
        style.configure('TSpinbox', fieldbackground=DARK_ENTRY_BG, foreground=DARK_FG, insertcolor=DARK_FG, arrowcolor=DARK_FG)
        style.configure('Horizontal.TProgressbar', background='#4CAF50', troughcolor=DARK_ENTRY_BG)
        
    def create_widgets(self):
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="UO Image Analyzer", font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Analyzes UOFiddler exports (Land Tiles & Static Items) and suggests hue mappings").pack()
        
        # Mode selection
        mode_frame = ttk.LabelFrame(self.root, text="Analysis Mode", padding="10")
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="land_tiles")
        ttk.Radiobutton(mode_frame, text="Land Tiles", variable=self.mode_var, value="land_tiles", 
                       command=self.on_mode_change).pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(mode_frame, text="Static Items", variable=self.mode_var, value="static_items",
                       command=self.on_mode_change).pack(side=tk.LEFT, padx=20)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(self.root, text="Directories", padding="10")
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Image directory
        ttk.Label(dir_frame, text="Image Directory:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.image_dir_var = tk.StringVar(value=DEFAULT_LANDTILES_DIR)
        ttk.Entry(dir_frame, textvariable=self.image_dir_var, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_image_dir).grid(row=0, column=2)
        
        # Output directory
        ttk.Label(dir_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_dir_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=60).grid(row=1, column=1, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_output_dir).grid(row=1, column=2)
        
        # Settings
        settings_frame = ttk.LabelFrame(self.root, text="Analysis Settings", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(settings_frame, text="Min Brightness (0-255):").grid(row=0, column=0, sticky=tk.W)
        self.brightness_var = tk.IntVar(value=MIN_BRIGHTNESS)
        ttk.Spinbox(settings_frame, from_=0, to=255, textvariable=self.brightness_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Min Alpha (0-255):").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.alpha_var = tk.IntVar(value=MIN_ALPHA)
        ttk.Spinbox(settings_frame, from_=0, to=255, textvariable=self.alpha_var, width=10).grid(row=0, column=3, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Analyze Images", command=self.analyze_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Show Color Preview", command=self.show_color_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export to JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Compact Hues", command=self.export_compact_hues).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy Compact Code", command=self.copy_compact_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # Log area
        log_frame = ttk.LabelFrame(self.root, text="Log Output", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD, 
                                                   bg=DARK_ENTRY_BG, fg=DARK_FG, 
                                                   insertbackground=DARK_FG, 
                                                   selectbackground=DARK_HIGHLIGHT,
                                                   selectforeground=DARK_FG)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
                              background=DARK_FRAME_BG, foreground=DARK_FG)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def on_mode_change(self):
        """Handle mode change between land tiles and static items"""
        mode = self.mode_var.get()
        self.current_mode = mode
        
        # Update default directory based on mode
        if mode == "land_tiles":
            self.image_dir_var.set(DEFAULT_LANDTILES_DIR)
            self.log("\nMode changed to: Land Tiles")
        else:
            self.image_dir_var.set(DEFAULT_STATICS_DIR)
            self.log("\nMode changed to: Static Items")
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
    
    def browse_image_dir(self):
        """Browse for image directory"""
        directory = filedialog.askdirectory(initialdir=self.image_dir_var.get())
        if directory:
            self.image_dir_var.set(directory)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def analyze_images(self):
        """Analyze all images in directory"""
        image_dir = self.image_dir_var.get()
        
        if not os.path.exists(image_dir):
            messagebox.showerror("Error", f"Directory not found: {image_dir}")
            return
        
        self.clear_log()
        self.log("Starting analysis...")
        self.log(f"Image Directory: {image_dir}")
        self.log(f"Min Brightness: {self.brightness_var.get()}")
        self.log(f"Min Alpha: {self.alpha_var.get()}")
        self.log("-" * 80)
        
        self.progress.start()
        self.status_var.set("Analyzing...")
        
        # Update global settings
        global MIN_BRIGHTNESS, MIN_ALPHA
        MIN_BRIGHTNESS = self.brightness_var.get()
        MIN_ALPHA = self.alpha_var.get()
        
        self.log(f"Using base dyeable UO hue data from game (906 hues)...")
        self.log(f"Analysis mode: {self.current_mode}\n")
        
        # Process images based on mode
        if self.current_mode == "static_items":
            self.results = process_static_items(image_dir, log_callback=self.log)
        else:
            self.results = process_land_tiles(image_dir, log_callback=self.log)
        
        self.progress.stop()
        
        if self.results:
            self.log("-" * 80)
            item_type = "static items" if self.current_mode == "static_items" else "land tiles"
            id_key = "item_id_hex" if self.current_mode == "static_items" else "land_id_hex"
            
            self.log(f"\nAnalysis complete! Found {len(self.results)} {item_type}")
            self.log(f"Estimated output: ~{(len(self.results) + 9) // 10} lines in compact format")
            self.log("\nSample results:")
            for result in self.results[:10]:
                self.log(f"  {result[id_key]}: Hue {result['uo_hue']} - {result['color_name']} (RGB: {result['rgb']})")
            if len(self.results) > 10:
                self.log(f"  ... and {len(self.results) - 10} more")
            
            # Show compact format preview
            self.log("\nCompact format preview (first 3 rows):")
            compact_preview = generate_compact_hue_dict(self.results[:30], self.current_mode)
            preview_lines = compact_preview.split('\n')[3:6]  # Skip header, show first 3 data rows
            for line in preview_lines:
                self.log(f"  {line}")
            
            self.status_var.set(f"Analysis complete - {len(self.results)} {item_type} processed")
        else:
            self.log("\nNo results found")
            self.status_var.set("No results")
    
    def export_json(self):
        """Export results to JSON"""
        if not self.results:
            messagebox.showwarning("Warning", "No results to export. Run analysis first.")
            return
        
        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        prefix = "static_item" if self.current_mode == "static_items" else "land_tile"
        filename = f"{prefix}_analysis_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        if export_results_to_json(self.results, filepath, self.current_mode):
            self.log(f"\nExported to: {filepath}")
            self.status_var.set(f"Exported to {filename}")
            messagebox.showinfo("Success", f"Results exported to:\n{filepath}")
        else:
            messagebox.showerror("Error", "Failed to export results")
    
    def export_compact_hues(self):
        """Export compact text file with land_id: hue_id, 10 per row"""
        if not self.results:
            messagebox.showwarning("Warning", "No results to export. Run analysis first.")
            return
        
        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        prefix = "static_item" if self.current_mode == "static_items" else "land_tile"
        filename = f"{prefix}_hues_compact_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        if export_compact_hue_txt(self.results, filepath, self.current_mode):
            self.log(f"\nExported compact hue dict to: {filepath}")
            
            # Show preview
            compact_dict = generate_compact_hue_dict(self.results, self.current_mode)
            all_lines = compact_dict.split('\n')
            preview_lines = all_lines[:15]  # Show first 15 lines
            self.log("\nPreview (first 15 lines):")
            self.log('\n'.join(preview_lines))
            if len(all_lines) > 15:
                self.log(f"... and {len(all_lines) - 15} more lines")
            
            self.status_var.set(f"Exported to {filename}")
            messagebox.showinfo("Success", f"Compact hue dict exported to:\n{filepath}")
        else:
            messagebox.showerror("Error", "Failed to export compact hue dict")
    
    def copy_compact_code(self):
        """Copy compact Python code to clipboard"""
        if not self.results:
            messagebox.showwarning("Warning", "No results to copy. Run analysis first.")
            return
        
        compact_code = generate_compact_hue_dict(self.results, self.current_mode)
        
        self.root.clipboard_clear()
        self.root.clipboard_append(compact_code)
        
        self.log("\nCompact hue dict copied to clipboard!")
        self.log("\nPreview (first 15 lines):")
        all_lines = compact_code.split('\n')
        preview_lines = all_lines[:15]
        self.log('\n'.join(preview_lines))
        if len(all_lines) > 15:
            self.log(f"... and {len(all_lines) - 15} more lines")
        
        self.status_var.set("Compact hue dict copied to clipboard")
        messagebox.showinfo("Success", "Compact hue dictionary code copied to clipboard!")
    
    def show_color_preview(self):
        """Show visual preview of sample land tiles with color comparison"""
        if not self.results:
            messagebox.showwarning("Warning", "No results to preview. Run analysis first.")
            return
        
        # Get sample items based on mode
        import random
        id_key = "item_id_decimal" if self.current_mode == "static_items" else "land_id_decimal"
        
        if self.current_mode == "land_tiles":
            # Select known land tiles
            known_ids = [0x0003, 0x0004, 0x00A8, 0x015A, 0x0150]  # Grass, Water, Sand, Dirt
            preview_tiles = []
            for tile_id in known_ids:
                result = next((r for r in self.results if r[id_key] == tile_id), None)
                if result:
                    preview_tiles.append(result)
            # Add random samples
            remaining = [r for r in self.results if r[id_key] not in known_ids]
            if remaining:
                preview_tiles.extend(random.sample(remaining, min(5, len(remaining))))
        else:
            # For static items, just get random samples
            preview_tiles = random.sample(self.results, min(10, len(self.results)))
        
        # Create preview window with dark mode
        preview_window = tk.Toplevel(self.root)
        title = "Static Item Color Preview" if self.current_mode == "static_items" else "Land Tile Color Preview"
        preview_window.title(title)
        preview_window.geometry("1000x800")
        preview_window.configure(bg=DARK_BG)
        
        # Add scrollable canvas
        canvas = tk.Canvas(preview_window, bg=DARK_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_title = "Static Item" if self.current_mode == "static_items" else "Land Tile"
        ttk.Label(header_frame, text=f"{header_title} Color Analysis Preview", font=('Arial', 12, 'bold')).pack()
        ttk.Label(header_frame, text="Comparing: Original Image | Analyzed RGB Average | Matched UO Hue Color").pack()
        
        # Display each tile
        for idx, result in enumerate(preview_tiles):
            self.create_tile_preview(scrollable_frame, result, idx)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        item_type = "static items" if self.current_mode == "static_items" else "land tiles"
        self.log(f"\nShowing color preview for {len(preview_tiles)} {item_type}")
    
    def create_tile_preview(self, parent, result, index):
        """Create a single tile preview row"""
        id_hex = result.get('item_id_hex') or result.get('land_id_hex')
        item_type = "Static Item" if self.current_mode == "static_items" else "Land Tile"
        frame = ttk.LabelFrame(parent, text=f"{item_type} {id_hex} - {result['color_name']}", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create three columns: Original | RGB Average | UO Hue Match
        columns_frame = ttk.Frame(frame)
        columns_frame.pack(fill=tk.X)
        
        # Column 1: Original Image
        col1 = ttk.Frame(columns_frame)
        col1.pack(side=tk.LEFT, padx=10)
        ttk.Label(col1, text="Original Image", font=('Arial', 9, 'bold')).pack()
        
        try:
            image_path = os.path.join(self.image_dir_var.get(), result['filename'])
            if os.path.exists(image_path):
                img = Image.open(image_path).convert('RGBA')
                # Resize for display (maintain aspect ratio)
                img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                # Use ImageTk.PhotoImage instead of tk.PhotoImage to avoid PPM encoder error
                photo = ImageTk.PhotoImage(img)
                # Store reference to prevent garbage collection
                if not hasattr(self, 'preview_images'):
                    self.preview_images = []
                self.preview_images.append(photo)
                
                img_label = ttk.Label(col1, image=photo)
                img_label.pack()
            else:
                ttk.Label(col1, text="Image not found", foreground="#ff6666").pack()
        except Exception as e:
            ttk.Label(col1, text=f"Error: {str(e)}", foreground="#ff6666").pack()
        
        # Column 2: Analyzed RGB Average
        col2 = ttk.Frame(columns_frame)
        col2.pack(side=tk.LEFT, padx=10)
        ttk.Label(col2, text="Analyzed RGB Average", font=('Arial', 9, 'bold')).pack()
        
        rgb = result['rgb']
        hex_color = result['hex_color']
        
        # Create color swatch
        rgb_canvas = tk.Canvas(col2, width=100, height=100, bg=hex_color, highlightthickness=1, highlightbackground=DARK_FG)
        rgb_canvas.pack()
        
        ttk.Label(col2, text=f"RGB: {rgb}", font=('Arial', 8)).pack()
        ttk.Label(col2, text=f"Hex: {hex_color}", font=('Arial', 8)).pack()
        ttk.Label(col2, text=f"Coverage: {result['coverage_percent']}%", font=('Arial', 8)).pack()
        
        # Column 3: Matched UO Hue
        col3 = ttk.Frame(columns_frame)
        col3.pack(side=tk.LEFT, padx=10)
        ttk.Label(col3, text="Matched UO Hue", font=('Arial', 9, 'bold')).pack()
        
        uo_hue_id = result['uo_hue']
        uo_rgb = generate_uo_hue_color_accurate(uo_hue_id)
        uo_hex = f"#{uo_rgb[0]:02x}{uo_rgb[1]:02x}{uo_rgb[2]:02x}"
        
        # Create color swatch
        hue_canvas = tk.Canvas(col3, width=100, height=100, bg=uo_hex, highlightthickness=1, highlightbackground=DARK_FG)
        hue_canvas.pack()
        
        ttk.Label(col3, text=f"Hue ID: {uo_hue_id}", font=('Arial', 8)).pack()
        ttk.Label(col3, text=f"RGB: {uo_rgb}", font=('Arial', 8)).pack()
        ttk.Label(col3, text=f"Hex: {uo_hex}", font=('Arial', 8)).pack()
        ttk.Label(col3, text=f"Name: {result['color_name']}", font=('Arial', 8)).pack()
        
        # Column 4: Color Distance Info
        col4 = ttk.Frame(columns_frame)
        col4.pack(side=tk.LEFT, padx=10)
        ttk.Label(col4, text="Match Quality", font=('Arial', 9, 'bold')).pack()
        
        # Calculate color distance
        distance = calculate_color_distance(rgb, uo_rgb)
        ttk.Label(col4, text=f"Distance: {distance:.2f}", font=('Arial', 8)).pack()
        
        # Quality indicator 
        if distance < 30:
            quality = "Excellent"
            color = "#4CAF50"  # Bright green
        elif distance < 60:
            quality = "Good"
            color = "#2196F3"  # Bright blue
        elif distance < 100:
            quality = "Fair"
            color = "#FF9800"  # Bright orange
        else:
            quality = "Poor"
            color = "#F44336"  # Bright red
        
        ttk.Label(col4, text=f"Quality: {quality}", font=('Arial', 8, 'bold'), foreground=color).pack()
        ttk.Label(col4, text=f"Pattern: {result['pattern_type']}", font=('Arial', 8)).pack()
        ttk.Label(col4, text=f"Char: '{result['suggested_char']}'", font=('Arial', 8)).pack()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    root = tk.Tk()
    app = LandTileAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()