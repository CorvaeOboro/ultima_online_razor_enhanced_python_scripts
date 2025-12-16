"""
Development Font Color Gump - Razor Enhanced Python Script for Ultima Online

Displays a visual grid of all Ultima Online hue palette of the base dyeable colors in a custom gump.
comparing to html color font text
Tests and verifies Ultima Online font hue hex codes visually.

REFERENCES: https://outlands.uorazorscripts.com/hues

DATA SOURCE:
============
UO_HUE_COLORS dictionary contains 860 actual hues extracted from UO game files.
- Hue range: 1-906 (with some gaps)
- Format: {hue_id: "#RRGGBB"}

PALETTE STRUCTURE :
========================================================

1. GROUPS OF 5 BRIGHTNESS LEVELS
   - Hues organized in families of 5 consecutive IDs
   - Each family shows INCREASING brightness progression
   - Example: Hues 2-6 (Blue family)
     * Hue 2: RGB(0,0,184) - Dark Blue
     * Hue 3: RGB(0,0,232) - Bright Blue  
     * Hue 4: RGB(48,48,232) - Light Blue
     * Hue 5: RGB(96,96,240) - Sky Blue
     * Hue 6: RGB(144,144,240) - Pale Blue

2. COLOR WHEEL PROGRESSION
   - Every 5 hues shifts dominant color channel
   - Cycles through: Blue → Purple → Magenta → Red → Orange → Yellow → Green → Cyan → Blue
     * Hues 2-21: Blue to Purple to Magenta 
     * Hues 22-51: Red to Orange to Yellow 
     * Hues 52-86: Yellow to Green to Cyan 
     * Hues 87-100: Cyan to Blue 

4. PALETTE CHARACTERISTICS
   - Discrete palette system (not continuous HSV/HSL)
   - Consistent brightness progression within families
   - Systematic color wheel rotation every 5 hues

EXAMPLE HUE FAMILIES (verified from actual data):
==================================================
Red Family (Hues 32-36):
  32: RGB(184,0,40)    #B80028 - Dark Red
  33: RGB(232,0,48)    #E80030 - Bright Red
  34: RGB(232,48,88)   #E83058 - Coral Red
  35: RGB(240,96,128)  #F06080 - Light Coral
  36: RGB(240,144,168) #F090A8 - Pale Coral

Yellow Family (Hues 52-56):
  52: RGB(184,184,0)   #B8B800 - Dark Yellow
  53: RGB(232,232,0)   #E8E800 - Bright Yellow
  54: RGB(232,232,48)  #E8E830 - Light Yellow
  55: RGB(240,240,96)  #F0F060 - Pale Yellow
  56: RGB(240,240,144) #F0F090 - Cream Yellow

USAGE:
======
- Displays 100 hues per row in scrollable grid
- Each square shows the  hue color


VERSION: 20250121
"""

DEBUG_MODE = True

TEXT_COLOR_SWATCH = "█"

# gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID = 3429654444

GUMP_X = 100
GUMP_Y = 100

# Grid configuration
SQUARES_PER_ROW = 100  # 100 colors per row
SQUARE_WIDTH = 19  # Width of gump image 210
SQUARE_HEIGHT = 20  # Height of gump image 210
SQUARE_SPACING_X = 20  # Horizontal spacing (slightly larger than image width)
SQUARE_SPACING_Y = 21  # Vertical spacing (slightly larger than image height)
LABEL_HEIGHT = 25  # Height for label area

# Comparison section configuration
COMPARISON_HUES_PER_ROW = 100  # Show all hues in comparison section (same as main grid)
COMPARISON_SPACING_X = 30  # Tight spacing to match main grid
COMPARISON_SPACING_Y = 25  # Compact vertical spacing for triangle overlap
COMPARISON_SECTION_GAP = 30  # Minimal gap between main grid and comparison section

UO_HUE_COLORS = {
    0:"#000008",1:"#0000B4",2:"#0000E6",3:"#3131E6",4:"#6262EE",5:"#8B8BEE",6:"#3900B4",7:"#4A00E6",8:"#6A31E6",9:"#8B62EE",
    10:"#AC8BEE",11:"#6A00B4",12:"#8B00E6",13:"#9C31E6",14:"#AC62EE",15:"#C58BEE",16:"#A400B4",17:"#CD00E6",18:"#D531E6",19:"#DE62EE",
    20:"#E68BEE",21:"#B40094",22:"#E600B4",23:"#E631BD",24:"#EE62CD",25:"#EE8BD5",26:"#B4005A",27:"#E60073",28:"#E63194",29:"#EE62A4",
    30:"#EE8BBD",31:"#B40029",32:"#E60031",33:"#E6315A",34:"#EE6283",35:"#EE8BA4",36:"#B41000",37:"#E61800",38:"#E64A31",39:"#EE7362",
    40:"#EE9C8B",41:"#B44A00",42:"#E66200",43:"#E68331",44:"#EE9462",45:"#EEB48B",46:"#B48300",47:"#E69C00",48:"#E6AC31",49:"#EEBD62",
    50:"#EECD8B",51:"#B4B400",52:"#E6E600",53:"#E6E631",54:"#EEEE62",55:"#EEEE8B",56:"#83B400",57:"#9CE600",58:"#ACE631",59:"#BDEE62",
    60:"#CDEE8B",61:"#4AB400",62:"#62E600",63:"#83E631",64:"#94EE62",65:"#B4EE8B",66:"#10B400",67:"#18E600",68:"#4AE631",69:"#73EE62",
    70:"#9CEE8B",71:"#00B429",72:"#00E631",73:"#31E65A",74:"#62EE83",75:"#8BEEA4",76:"#00B45A",77:"#00E67B",78:"#31E694",79:"#62EEA4",
    80:"#8BEEBD",81:"#00B494",82:"#00E6B4",83:"#31E6BD",84:"#62EECD",85:"#8BEED5",86:"#00A4B4",87:"#00CDE6",88:"#31D5E6",89:"#62DEEE",
    90:"#8BE6EE",91:"#006AB4",92:"#008BE6",93:"#319CE6",94:"#62ACEE",95:"#8BC5EE",96:"#0039B4",97:"#004AE6",98:"#316AE6",99:"#628BEE",
    100:"#8BACEE",101:"#0808AC",102:"#1010D5",103:"#3939DE",104:"#6A6AE6",105:"#9494E6",106:"#4108AC",107:"#5210D5",108:"#7339DE",109:"#8B6AE6",
    110:"#AC94E6",111:"#6A08AC",112:"#8B10D5",113:"#9C39DE",114:"#AC6AE6",115:"#C594E6",116:"#9C08AC",117:"#BD10D5",118:"#CD39DE",119:"#D56AE6",
    120:"#DE94E6",121:"#AC088B",122:"#D510AC",123:"#DE39B4",124:"#E66AC5",125:"#E694D5",126:"#AC085A",127:"#D51073",128:"#DE3994",129:"#E66AA4",
    130:"#E694BD",131:"#AC0831",132:"#D51039",133:"#DE3962",134:"#E66A83",135:"#E694A4",136:"#AC1808",137:"#D52910",138:"#DE5239",139:"#E67B6A",
    140:"#E69C94",141:"#AC4A08",142:"#D56210",143:"#DE8339",144:"#E69C6A",145:"#E6B494",146:"#AC7B08",147:"#D59C10",148:"#DEA439",149:"#E6BD6A",
    150:"#E6CD94",151:"#ACAC08",152:"#D5D510",153:"#DEDE39",154:"#E6E66A",155:"#E6E694",156:"#7BAC08",157:"#9CD510",158:"#A4DE39",159:"#BDE66A",
    160:"#CDE694",161:"#4AAC08",162:"#62D510",163:"#83DE39",164:"#9CE66A",165:"#B4E694",166:"#18AC08",167:"#29D510",168:"#52DE39",169:"#7BE66A",
    170:"#9CE694",171:"#08AC31",172:"#10D539",173:"#39DE62",174:"#6AE683",175:"#94E6A4",176:"#08AC5A",177:"#10D57B",178:"#39DE94",179:"#6AE6A4",
    180:"#94E6BD",181:"#08AC8B",182:"#10D5AC",183:"#39DEB4",184:"#6AE6C5",185:"#94E6D5",186:"#089CAC",187:"#10BDD5",188:"#39CDDE",189:"#6AD5E6",
    190:"#94DEE6",191:"#086AAC",192:"#108BD5",193:"#399CDE",194:"#6AACE6",195:"#94C5E6",196:"#0841AC",197:"#1052D5",198:"#3973DE",199:"#6A8BE6",
    200:"#94ACE6",201:"#1010A4",202:"#1818CD",203:"#4A4AD5",204:"#7373DE",205:"#9C9CE6",206:"#4110A4",207:"#5218CD",208:"#734AD5",209:"#8B73DE",
    210:"#AC9CE6",211:"#6A10A4",212:"#8B18CD",213:"#944AD5",214:"#AC73DE",215:"#C59CE6",216:"#9410A4",217:"#B418CD",218:"#C54AD5",219:"#CD73DE",
    220:"#DE9CE6",221:"#A41083",222:"#CD18A4",223:"#D54AB4",224:"#DE73C5",225:"#E69CD5",226:"#A4105A",227:"#CD1873",228:"#D54A94",229:"#DE73A4",
    230:"#E69CBD",231:"#A41031",232:"#CD1841",233:"#D54A6A",234:"#DE7383",235:"#E69CAC",236:"#A42010",237:"#CD3118",238:"#D55A4A",239:"#DE8373",
    240:"#E6A49C",241:"#A45210",242:"#CD6218",243:"#D5834A",244:"#DE9C73",245:"#E6B49C",246:"#A47B10",247:"#CD9C18",248:"#D5A44A",249:"#DEB473",
    250:"#E6CD9C",251:"#A4A410",252:"#CDCD18",253:"#D5D54A",254:"#DEDE73",255:"#E6E69C",256:"#7BA410",257:"#9CCD18",258:"#A4D54A",259:"#B4DE73",
    260:"#CDE69C",261:"#52A410",262:"#62CD18",263:"#83D54A",264:"#9CDE73",265:"#B4E69C",266:"#20A410",267:"#31CD18",268:"#5AD54A",269:"#83DE73",
    270:"#A4E69C",271:"#10A431",272:"#18CD41",273:"#4AD56A",274:"#73DE83",275:"#9CE6AC",276:"#10A45A",277:"#18CD7B",278:"#4AD594",279:"#73DEA4",
    280:"#9CE6BD",281:"#10A483",282:"#18CDA4",283:"#4AD5B4",284:"#73DEC5",285:"#9CE6D5",286:"#1094A4",287:"#18B4CD",288:"#4AC5D5",289:"#73CDDE",
    290:"#9CDEE6",291:"#106AA4",292:"#188BCD",293:"#4A94D5",294:"#73ACDE",295:"#9CC5E6",296:"#1041A4",297:"#1852CD",298:"#4A73D5",299:"#738BDE",
    300:"#9CACE6",301:"#20209C",302:"#2929BD",303:"#5252C5",304:"#7B7BD5",305:"#9C9CDE",306:"#41209C",307:"#5A29BD",308:"#7B52C5",309:"#947BD5",
    310:"#B49CDE",311:"#6A209C",312:"#8329BD",313:"#9452C5",314:"#AC7BD5",315:"#C59CDE",316:"#8B209C",317:"#AC29BD",318:"#BD52C5",319:"#C57BD5",
    320:"#D59CDE",321:"#9C2083",322:"#BD299C",323:"#C552AC",324:"#D57BBD",325:"#DE9CCD",326:"#9C205A",327:"#BD2973",328:"#C55294",329:"#D57BA4",
    330:"#DE9CBD",331:"#9C2039",332:"#BD294A",333:"#C5526A",334:"#D57B8B",335:"#DE9CAC",336:"#9C2920",337:"#BD3929",338:"#C56252",339:"#D5837B",
    340:"#DEA49C",341:"#9C5220",342:"#BD6A29",343:"#C58352",344:"#D59C7B",345:"#DEB49C",346:"#9C7320",347:"#BD9429",348:"#C5A452",349:"#D5B47B",
    350:"#DECD9C",351:"#9C9C20",352:"#BDBD29",353:"#C5C552",354:"#D5D57B",355:"#DEDE9C",356:"#739C20",357:"#94BD29",358:"#A4C552",359:"#B4D57B",
    360:"#CDDE9C",361:"#529C20",362:"#6ABD29",363:"#83C552",364:"#9CD57B",365:"#B4DE9C",366:"#299C20",367:"#39BD29",368:"#62C552",369:"#83D57B",
    370:"#A4DE9C",371:"#209C39",372:"#29BD4A",373:"#52C56A",374:"#7BD58B",375:"#9CDEAC",376:"#209C5A",377:"#29BD7B",378:"#52C594",379:"#7BD5A4",
    380:"#9CDEBD",381:"#209C83",382:"#29BD9C",383:"#52C5AC",384:"#7BD5BD",385:"#9CDECD",386:"#208B9C",387:"#29ACBD",388:"#52BDC5",389:"#7BC5D5",
    390:"#9CD5DE",391:"#206A9C",392:"#2983BD",393:"#5294C5",394:"#7BACD5",395:"#9CC5DE",396:"#20419C",397:"#295ABD",398:"#527BC5",399:"#7B94D5",
    400:"#9CB4DE",401:"#292994",402:"#3131B4",403:"#5A5ABD",404:"#8383CD",405:"#A4A4D5",406:"#4A2994",407:"#6231B4",408:"#7B5ABD",409:"#9483CD",
    410:"#B4A4D5",411:"#622994",412:"#8331B4",413:"#945ABD",414:"#AC83CD",415:"#C5A4D5",416:"#832994",417:"#A431B4",418:"#B45ABD",419:"#C583CD",
    420:"#D5A4D5",421:"#94297B",422:"#B4319C",423:"#BD5AA4",424:"#CD83BD",425:"#D5A4CD",426:"#94295A",427:"#B43173",428:"#BD5A94",429:"#CD83A4",
    430:"#D5A4BD",431:"#942941",432:"#B43152",433:"#BD5A73",434:"#CD838B",435:"#D5A4AC",436:"#943129",437:"#B44131",438:"#BD6A5A",439:"#CD8383",
    440:"#D5ACA4",441:"#945229",442:"#B46A31",443:"#BD8B5A",444:"#CD9C83",445:"#D5BDA4",446:"#947329",447:"#B48B31",448:"#BD9C5A",449:"#CDB483",
    450:"#D5C5A4",451:"#949429",452:"#ACB431",453:"#BDBD5A",454:"#CDCD83",455:"#D5D5A4",456:"#739429",457:"#8BB431",458:"#9CBD5A",459:"#B4CD83",
    460:"#C5D5A4",461:"#529429",462:"#6AB431",463:"#8BBD5A",464:"#9CCD83",465:"#BDD5A4",466:"#319429",467:"#41B431",468:"#6ABD5A",469:"#83CD83",
    470:"#ACD5A4",471:"#299441",472:"#31B452",473:"#5ABD73",474:"#83CD8B",475:"#A4D5AC",476:"#29945A",477:"#31B47B",478:"#5ABD94",479:"#83CDA4",
    480:"#A4D5BD",481:"#29947B",482:"#31B49C",483:"#5ABDA4",484:"#83CDBD",485:"#A4D5CD",486:"#298394",487:"#31A4B4",488:"#5AB4BD",489:"#83C5CD",
    490:"#A4D5D5",491:"#296294",492:"#3183B4",493:"#5A94BD",494:"#83ACCD",495:"#A4C5D5",496:"#294A94",497:"#3162B4",498:"#5A7BBD",499:"#8394CD",
    500:"#A4B4D5",501:"#313183",502:"#4141A4",503:"#6A6AB4",504:"#8383C5",505:"#ACACD5",506:"#4A3183",507:"#6241A4",508:"#836AB4",509:"#9483C5",
    510:"#B4ACD5",511:"#623183",512:"#8341A4",513:"#946AB4",514:"#AC83C5",515:"#C5ACD5",516:"#7B3183",517:"#9C41A4",518:"#AC6AB4",519:"#BD83C5",
    520:"#CDACD5",521:"#833173",522:"#A44194",523:"#B46AA4",524:"#C583B4",525:"#D5ACCD",526:"#83315A",527:"#A44173",528:"#B46A94",529:"#C583A4",
    530:"#D5ACBD",531:"#833141",532:"#A4415A",533:"#B46A7B",534:"#C58394",535:"#D5ACB4",536:"#833931",537:"#A45241",538:"#B4736A",539:"#C58B83",
    540:"#D5ACAC",541:"#835231",542:"#A46A41",543:"#B48B6A",544:"#C59C83",545:"#D5BDAC",546:"#836A31",547:"#A48B41",548:"#B49C6A",549:"#C5AC83",
    550:"#D5C5AC",551:"#838331",552:"#A4A441",553:"#B4B46A",554:"#C5C583",555:"#D5D5AC",556:"#6A8331",557:"#8BA441",558:"#9CB46A",559:"#ACC583",
    560:"#C5D5AC",561:"#528331",562:"#6AA441",563:"#8BB46A",564:"#9CC583",565:"#BDD5AC",566:"#398331",567:"#52A441",568:"#73B46A",569:"#8BC583",
    570:"#ACD5AC",571:"#318341",572:"#41A45A",573:"#6AB47B",574:"#83C594",575:"#ACD5B4",576:"#31835A",577:"#41A47B",578:"#6AB494",579:"#83C5A4",
    580:"#ACD5BD",581:"#318373",582:"#41A494",583:"#6AB4A4",584:"#83C5B4",585:"#ACD5CD",586:"#317B83",587:"#419CA4",588:"#6AACB4",589:"#83BDC5",
    590:"#ACCDD5",591:"#316283",592:"#4183A4",593:"#6A94B4",594:"#83ACC5",595:"#ACC5D5",596:"#314A83",597:"#4162A4",598:"#6A83B4",599:"#8394C5",
    600:"#ACB4D5",601:"#39397B",602:"#52529C",603:"#7373AC",604:"#8B8BBD",605:"#ACACCD",606:"#52397B",607:"#6A529C",608:"#8373AC",609:"#9C8BBD",
    610:"#B4ACCD",611:"#62397B",612:"#7B529C",613:"#9473AC",614:"#A48BBD",615:"#BDACCD",616:"#73397B",617:"#94529C",618:"#A473AC",619:"#B48BBD",
    620:"#CDACCD",621:"#7B396A",622:"#9C528B",623:"#AC739C",624:"#BD8BB4",625:"#CDACC5",626:"#7B395A",627:"#9C5273",628:"#AC7394",629:"#BD8BA4",
    630:"#CDACBD",631:"#7B394A",632:"#9C5262",633:"#AC7383",634:"#BD8B94",635:"#CDACB4",636:"#7B4139",637:"#9C5A52",638:"#AC7B73",639:"#BD948B",
    640:"#CDB4AC",641:"#7B5A39",642:"#9C7352",643:"#AC8B73",644:"#BD9C8B",645:"#CDBDAC",646:"#7B6A39",647:"#9C8352",648:"#AC9473",649:"#BDAC8B",
    650:"#CDC5AC",651:"#7B7B39",652:"#9C9C52",653:"#ACAC73",654:"#BDBD8B",655:"#CDCDAC",656:"#6A7B39",657:"#839C52",658:"#94AC73",659:"#ACBD8B",
    660:"#C5CDAC",661:"#5A7B39",662:"#739C52",663:"#8BAC73",664:"#9CBD8B",665:"#BDCDAC",666:"#417B39",667:"#5A9C52",668:"#7BAC73",669:"#94BD8B",
    670:"#B4CDAC",671:"#397B4A",672:"#529C62",673:"#73AC83",674:"#8BBD94",675:"#ACCDB4",676:"#397B5A",677:"#529C7B",678:"#73AC94",679:"#8BBDA4",
    680:"#ACCDBD",681:"#397B6A",682:"#529C8B",683:"#73AC9C",684:"#8BBDB4",685:"#ACCDC5",686:"#39737B",687:"#52949C",688:"#73A4AC",689:"#8BB4BD",
    690:"#ACCDCD",691:"#39627B",692:"#527B9C",693:"#7394AC",694:"#8BA4BD",695:"#ACBDCD",696:"#39527B",697:"#526A9C",698:"#7383AC",699:"#8B9CBD",
    700:"#ACB4CD",701:"#4A4A73",702:"#5A5A94",703:"#7B7B9C",704:"#9494B4",705:"#B4B4C5",706:"#524A73",707:"#6A5A94",708:"#8B7B9C",709:"#9C94B4",
    710:"#BDB4C5",711:"#624A73",712:"#7B5A94",713:"#947B9C",714:"#A494B4",715:"#BDB4C5",716:"#6A4A73",717:"#8B5A94",718:"#9C7B9C",719:"#AC94B4",
    720:"#C5B4C5",721:"#734A6A",722:"#945A83",723:"#9C7B94",724:"#B494AC",725:"#C5B4C5",726:"#734A5A",727:"#945A73",728:"#9C7B94",729:"#B494A4",
    730:"#C5B4BD",731:"#734A52",732:"#945A6A",733:"#9C7B83",734:"#B4949C",735:"#C5B4B4",736:"#734A4A",737:"#94625A",738:"#9C837B",739:"#B49494",
    740:"#C5B4B4",741:"#735A4A",742:"#94735A",743:"#9C8B7B",744:"#B4A494",745:"#C5BDB4",746:"#73624A",747:"#94835A",748:"#9C947B",749:"#B4AC94",
    750:"#C5C5B4",751:"#73734A",752:"#94945A",753:"#9C9C7B",754:"#B4B494",755:"#C5C5B4",756:"#62734A",757:"#83945A",758:"#949C7B",759:"#ACB494",
    760:"#C5C5B4",761:"#5A734A",762:"#73945A",763:"#8B9C7B",764:"#A4B494",765:"#BDC5B4",766:"#4A734A",767:"#62945A",768:"#839C7B",769:"#94B494",
    770:"#B4C5B4",771:"#4A7352",772:"#5A946A",773:"#7B9C83",774:"#94B49C",775:"#B4C5B4",776:"#4A735A",777:"#5A947B",778:"#7B9C94",779:"#94B4A4",
    780:"#B4C5BD",781:"#4A736A",782:"#5A9483",783:"#7B9C94",784:"#94B4AC",785:"#B4C5C5",786:"#4A6A73",787:"#5A8B94",788:"#7B9C9C",789:"#94ACB4",
    790:"#B4C5C5",791:"#4A6273",792:"#5A7B94",793:"#7B949C",794:"#94A4B4",795:"#B4BDC5",796:"#4A5273",797:"#5A6A94",798:"#7B8B9C",799:"#949CB4",
    800:"#B4BDC5",801:"#52526A",802:"#6A6A83",803:"#838394",804:"#9C9CAC",805:"#B4B4C5",806:"#5A526A",807:"#736A83",808:"#8B8394",809:"#A49CAC",
    810:"#BDB4C5",811:"#62526A",812:"#7B6A83",813:"#948394",814:"#A49CAC",815:"#BDB4C5",816:"#62526A",817:"#836A83",818:"#948394",819:"#AC9CAC",
    820:"#C5B4C5",821:"#6A5262",822:"#836A7B",823:"#948394",824:"#AC9CA4",825:"#C5B4BD",826:"#6A525A",827:"#836A73",828:"#948394",829:"#AC9CA4",
    830:"#C5B4BD",831:"#6A525A",832:"#836A73",833:"#94838B",834:"#AC9C9C",835:"#C5B4BD",836:"#6A5252",837:"#836A6A",838:"#948B83",839:"#AC9C9C",
    840:"#C5BDB4",841:"#6A5A52",842:"#83736A",843:"#948B83",844:"#ACA49C",845:"#C5BDB4",846:"#6A6252",847:"#837B6A",848:"#949483",849:"#ACA49C",
    850:"#C5BDB4",851:"#6A6A52",852:"#83836A",853:"#949483",854:"#ACAC9C",855:"#C5C5B4",856:"#626A52",857:"#7B836A",858:"#949483",859:"#A4AC9C",
    860:"#BDC5B4",861:"#5A6A52",862:"#73836A",863:"#8B9483",864:"#A4AC9C",865:"#BDC5B4",866:"#526A52",867:"#6A836A",868:"#8B9483",869:"#9CAC9C",
    870:"#BDC5B4",871:"#526A5A",872:"#6A8373",873:"#83948B",874:"#9CAC9C",875:"#B4C5BD",876:"#526A5A",877:"#6A837B",878:"#839494",879:"#9CACA4",
    880:"#B4C5BD",881:"#526A62",882:"#6A837B",883:"#839494",884:"#9CACA4",885:"#B4C5BD",886:"#52626A",887:"#6A8383",888:"#839494",889:"#9CACAC",
    890:"#B4C5C5",891:"#52626A",892:"#6A7B83",893:"#839494",894:"#9CA4AC",895:"#B4BDC5",896:"#525A6A",897:"#6A7383",898:"#838B94",899:"#9CA4AC",
    900:"#B4BDC5",901:"#5A5A5A",902:"#7B7B7B",903:"#949494",904:"#A4A4A4",905:"#BDBDBD"
}


def html_to_rgb(html_color):
    """
    Convert HTML hex color code to RGB tuple.
    
    Args:
        html_color: String like '#RRGGBB' or '#rrggbb'
        
    Returns:
        tuple: (r, g, b) values (0-255)
    """
    html_color = html_color.lstrip('#')
    return tuple(int(html_color[i:i+2], 16) for i in (0, 2, 4))


def get_uo_hue_color(hue_id):
    """
    Get RGB color for UO hue ID from the actual game palette.
    
    Uses UO_HUE_COLORS dictionary which contains the actual 860 hues
    extracted from the game files (hues 1-906 with some gaps).
    
    Args:
        hue_id: Integer hue ID (1-906)
        
    Returns:
        tuple: (r, g, b) values (0-255), or (128, 128, 128) if hue not found
    """
    html_color = UO_HUE_COLORS.get(hue_id)
    if html_color:
        return html_to_rgb(html_color)
    else:
        # Return gray for missing hues
        return (128, 128, 128)


def generate_hue_name(hue_id):
    """
    Generate descriptive name for a hue based on its RGB values.
    
    Uses the actual RGB values from UO_HUE_COLORS to determine
    the color name based on dominant channels and brightness.
    
    Args:
        hue_id: Integer hue ID
        
    Returns:
        str: Descriptive color name
    """
    rgb = get_uo_hue_color(hue_id)
    r, g, b = rgb
    
    # Calculate brightness
    brightness = (r + g + b) / 3
    
    # Determine dominant color
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    
    # Grayscale check
    if max_val - min_val < 30:
        if brightness < 60:
            return "Black"
        elif brightness < 100:
            return "Dark Gray"
        elif brightness < 150:
            return "Gray"
        elif brightness < 200:
            return "Light Gray"
        else:
            return "White"
    
    # Determine base color
    if r == max_val and g == max_val:  # Yellow family
        if b < 50:
            base_color = "Yellow"
        else:
            base_color = "Cream"
    elif r == max_val and b == max_val:  # Magenta family
        if g < 50:
            base_color = "Magenta"
        else:
            base_color = "Pink"
    elif g == max_val and b == max_val:  # Cyan family
        if r < 50:
            base_color = "Cyan"
        else:
            base_color = "Aqua"
    elif r == max_val:  # Red family
        if g > b:
            base_color = "Orange" if g > 100 else "Red"
        else:
            base_color = "Rose" if b > 100 else "Red"
    elif g == max_val:  # Green family
        if r > b:
            base_color = "Lime" if r > 100 else "Green"
        else:
            base_color = "Teal" if b > 100 else "Green"
    else:  # Blue family
        if r > g:
            base_color = "Purple" if r > 100 else "Blue"
        else:
            base_color = "Azure" if g > 100 else "Blue"
    
    # Brightness modifier
    if brightness < 80:
        modifier = "Dark"
    elif brightness < 150:
        modifier = "Medium"
    elif brightness < 200:
        modifier = "Light"
    else:
        modifier = "Pale"
    
    return f"{modifier} {base_color}"


def rgb_to_html(rgb):
    """
    Convert RGB tuple to HTML hex color code.
    
    Args:
        rgb: Tuple of (r, g, b) values (0-255)
        
    Returns:
        str: HTML color code like '#RRGGBB'
    """
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def get_available_hues():
    """
    Get list of all available hue IDs from UO_HUE_COLORS.
    
    Returns:
        list: Sorted list of hue IDs
    """
    return sorted(UO_HUE_COLORS.keys())


def generate_hue_data_from_palette():
    """
    Generate hue color data from UO_HUE_COLORS palette.
    
    Creates a dictionary with RGB, HTML, and name for each hue
    in the actual game palette.
    
    Returns:
        dict: Dictionary with format {hue_id: {'rgb': (r,g,b), 'html': '#RRGGBB', 'name': 'Color Name'}}
    """
    hue_data = {}
    
    for hue_id in UO_HUE_COLORS.keys():
        rgb = get_uo_hue_color(hue_id)
        html = UO_HUE_COLORS[hue_id]
        name = generate_hue_name(hue_id)
        
        hue_data[hue_id] = {
            'rgb': rgb,
            'html': html,
            'name': name
        }
    
    return hue_data


class FontColorGump:
    def __init__(self):
        """
        Initialize the gump with actual UO hue color data.
        
        Uses UO_HUE_COLORS dictionary which contains 860 actual hues
        from the game files (hues 1-906 with some gaps).
        """
        # Generate hue data from actual game palette
        self.hue_data = generate_hue_data_from_palette()
        self.available_hues = get_available_hues()

    def show(self):
        """Display gump with grid of colored squares and comparison section."""
        g = Gumps.CreateGump(True, True, False, False)  # movable, closable
        Gumps.AddPage(g, 0)
        
        # Calculate grid dimensions
        total_hues = len(self.available_hues)
        main_grid_rows = (total_hues + SQUARES_PER_ROW - 1) // SQUARES_PER_ROW
        
        # Calculate comparison section dimensions
        comparison_hues = self.available_hues  # Show ALL hues in comparison section
        comparison_rows = (len(comparison_hues) + COMPARISON_HUES_PER_ROW - 1) // COMPARISON_HUES_PER_ROW
        
        # Calculate gump size
        width = max(
            SQUARES_PER_ROW * SQUARE_SPACING_X + 30,  # Main grid width
            COMPARISON_HUES_PER_ROW * COMPARISON_SPACING_X + 30  # Comparison section width
        )
        
        main_grid_height = LABEL_HEIGHT + (main_grid_rows * SQUARE_SPACING_Y)
        comparison_section_height = (comparison_rows * COMPARISON_SPACING_Y) + 60
        height = main_grid_height + COMPARISON_SECTION_GAP + comparison_section_height + 40
        
        # Background (required for clickable/draggable gump)
        Gumps.AddBackground(g, 0, 0, width, height, 30546)
        Gumps.AddAlphaRegion(g, 0, 0, width, height)
        
        # Title (using HTML so it's clickable/movable)
        title_text = f"<CENTER>UO Hue Color Grid ({total_hues} hues: 1-906) - {SQUARES_PER_ROW} per row</CENTER>"
        Gumps.AddHtml(g, 10, 5, width - 50, 20, title_text, False, False)
        
        # ===== MAIN GRID: Draw all hues as colored squares =====
        y_offset = LABEL_HEIGHT
        for idx, hue_id in enumerate(self.available_hues):
            row = idx // SQUARES_PER_ROW
            col = idx % SQUARES_PER_ROW
            
            x = 15 + (col * SQUARE_SPACING_X)
            y = y_offset + (row * SQUARE_SPACING_Y)
            
            # Use AddImage with hue to create colored square
            Gumps.AddImage(g, x, y, 210, hue_id)
        
        # ===== COMPARISON SECTION: UO Hue vs HTML Color =====
        comparison_y_start = main_grid_height + COMPARISON_SECTION_GAP
        
        # Section title
        comparison_title = "<CENTER><BASEFONT COLOR=#FFFFFF>Comparison: Image(hue) + HTML(color) + Label(hue) - Triangle Overlap</BASEFONT></CENTER>"
        Gumps.AddHtml(g, 10, comparison_y_start, width - 20, 20, comparison_title, False, False)
        
        comparison_y_start += 50  # Extra space for title + note
        
        # Draw comparison items - Triangle overlap pattern
        for idx, hue_id in enumerate(comparison_hues):
            col = idx % COMPARISON_HUES_PER_ROW
            row = idx // COMPARISON_HUES_PER_ROW
            
            x = 15 + (col * COMPARISON_SPACING_X)
            y = comparison_y_start + (row * COMPARISON_SPACING_Y)
            
            # Get HTML color for this hue
            html_color = self.hue_data[hue_id]['html']
            
            # Triangle overlap arrangement (3 swatches only):
            # 1. AddImage with hue (bottom-left corner)
            Gumps.AddImage(g, x, y + 8, 210, hue_id)
            
            # 2. AddHtml with HTML color (top corner, offset)
            html_swatch = f"<BASEFONT COLOR={html_color}>{TEXT_COLOR_SWATCH}</BASEFONT>"
            Gumps.AddHtml(g, x + 5, y, 30, 20, html_swatch, False, False)
            
            # 3. AddLabel with UO hue color (bottom-right corner, offset)
            Gumps.AddLabel(g, x + 10, y + 8, hue_id, TEXT_COLOR_SWATCH)
        
        # Add close button
        Gumps.AddButton(g, width - 30, 5, 3600, 3601, 1, 0, 0)
        
        # Send gump with 0,0 position to remember moved location
        Gumps.SendGump(GUMP_ID, Player.Serial, 0, 0, g.gumpDefinition, g.gumpStrings)

if __name__ == '__main__':
    # Display all 
    FontColorGump().show()
