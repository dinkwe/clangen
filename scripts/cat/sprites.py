import logging
import os
from copy import copy

import pygame
import ujson

from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.special_dates import SpecialDate, is_today

logger = logging.getLogger(__name__)


class Sprites:
    cat_tints = {}
    white_patches_tints = {}
    clan_symbols = []

    def __init__(self):
        """Class that handles and hold all spritesheets.
        Size is normally automatically determined by the size
        of the lineart. If a size is passed, it will override
        this value."""
        self.symbol_dict = None
        self.size = None
        self.spritesheets = {}
        self.images = {}
        self.sprites = {}

        # Shared empty sprite for placeholders
        self.blank_sprite = None

        self.load_tints()

    def load_tints(self):
        try:
            with open("sprites/dicts/tint.json", "r", encoding="utf-8") as read_file:
                self.cat_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading Tints")

        try:
            with open(
                "sprites/dicts/white_patches_tint.json", "r", encoding="utf-8"
            ) as read_file:
                self.white_patches_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading White Patches Tints")

    def spritesheet(self, a_file, name):
        """
        Add spritesheet called name from a_file.

        Parameters:
        a_file -- Path to the file to create a spritesheet from.
        name -- Name to call the new spritesheet.
        """
        self.spritesheets[name] = pygame.image.load(a_file).convert_alpha()

    def make_group(
        self, spritesheet, pos, name, sprites_x=3, sprites_y=7, no_index=False
    ):  # pos = ex. (2, 3), no single pixels
        """
        Divide sprites on a spritesheet into groups of sprites that are easily accessible
        :param spritesheet: Name of spritesheet file
        :param pos: (x,y) tuple of offsets. NOT pixel offset, but offset of other sprites
        :param name: Name of group being made
        :param sprites_x: default 3, number of sprites horizontally
        :param sprites_y: default 3, number of sprites vertically
        :param no_index: default False, set True if sprite name does not require cat pose index
        """

        group_x_ofs = pos[0] * sprites_x * self.size
        group_y_ofs = pos[1] * sprites_y * self.size
        i = 0

        # splitting group into singular sprites and storing into self.sprites section
        for y in range(sprites_y):
            for x in range(sprites_x):
                if no_index:
                    full_name = f"{name}"
                else:
                    full_name = f"{name}{i}"

                try:
                    new_sprite = pygame.Surface.subsurface(
                        self.spritesheets[spritesheet],
                        group_x_ofs + x * self.size,
                        group_y_ofs + y * self.size,
                        self.size,
                        self.size,
                    )

                except ValueError:
                    # Fallback for non-existent sprites
                    print(f"WARNING: nonexistent sprite - {full_name}")
                    if not self.blank_sprite:
                        self.blank_sprite = pygame.Surface(
                            (self.size, self.size), pygame.HWSURFACE | pygame.SRCALPHA
                        )
                    new_sprite = self.blank_sprite

                self.sprites[full_name] = new_sprite
                i += 1

    def load_all(self):
        # get the width and height of the spritesheet
        lineart = pygame.image.load("sprites/lineart.png")
        width, height = lineart.get_size()
        del lineart  # unneeded

        # if anyone changes lineart for whatever reason update this
        if isinstance(self.size, int):
            pass
        elif width / 3 == height / 7:
            self.size = width / 3
        else:
            self.size = 50  # default, what base clangen uses
            print(f"lineart.png is not 3x7, falling back to {self.size}")
            print(
                f"if you are a modder, please update scripts/cat/sprites.py and "
                f"do a search for 'if width / 3 == height / 7:'"
            )

        del width, height  # unneeded

        for x in (
            "lineart", "lineartdf", "lineartdead", "flutter_lineart", "flutter_lineartdf", "flutter_lineartdead", "lamp_lineart", "lamp_lineartdf", "lamp_lineartdead",
            "eyes", "skin", "skin_magic", "skin_elemental", "skin_bingle", "skin_bingle2", "skin_mathkangaroo", "eyesdark", "eyesvivid", "towheeeyes",
            "scars", "missingscars", "wild", "eyes_wing", "eyes2_halo", "colorsplash_neckerchief", "colorsplash_witchhat", "skin_stain", "skin_turtle", "eyes_snail",
            "medcatherbs", "beetleeyes", "beetlemore",  "moss_accs", "neos_eyes", "neos_eyes2", "lamp_eyes", "flutter_eyes", "flutter_eyes2",
            "collars", "bellcollars", "bowcollars", "nyloncollars", "colorsplash_horn", "colorsplash_kitsune", "colorsplash_mermaid",
            "singlecolours", "speckledcolours", "tabbycolours", "bengalcolours", "marbledcolours",
            "rosettecolours", "smokecolours", "tickedcolours", "mackerelcolours", "classiccolours",
            "sokokecolours", "agouticolours", "singlestripecolours", "maskedcolours",
            "manedcolours", "ocelotcolours", "lynxcolours", "abyssiniancolours", "cloudedcolours", "dobermancolours", "ghosttabbycolours", "merlecolours", "monarchcolours", "oceloidcolours", "pinstripetabbycolours", "snowflakecolours", "royalcolours", "bobcatcolours", "cheetahcolours",
            "shadersnewwhite", "lightingnew", "pokemon",
            "whitepatches", "minkswhite", "voithexpatches", "exoticwhitepatches", "tortiepatchesmasks", "minkstorties",
            "fademask", "fadestarclan", "fadedarkforest", "bandanas", "stainvoithex",
            "symbols", "plant2_accessories", "flower_accessories", "snake_accessories", "eragonatorite", "eragonawp", "eragonaeyes",
            "brindlecolours", "wildcatcolours", "wolfcolours", "spotscolours", "smokepointcolours",
            "dalmatiancolours", "finleappatchescolours", "eragonatorite2", "sterflowers", "harnesses", "bows", "teethcollars", "smallAnimal_accessories", "aliveInsect_accessories",
            "deadInsect_accessories", "fruit_accessories", "crafted_accessories", "tail2_accessories", "bonesacc", "butterflymothacc", "twolegstuff", "steragouticolours", "sillyagouticolours", "danceagouticolours", "mimiagouticolours",
            "sterbengalcolours", "sillybengalcolours", "dancebengalcolours", "mimibengalcolours",
            "sterclassiccolours", "sillyclassiccolours", "danceclassiccolours", "mimiclassiccolours",
            "stermackerelcolours", "sillymackerelcolours", "dancemackerelcolours", "mimimackerelcolours",
            "stermarbledcolours", "sillymarbledcolours", "dancemarbledcolours", "mimimarbledcolours",
            "stermaskedcolours", "sillymaskedcolours", "dancemaskedcolours", "mimimaskedcolours",
            "sterrosettecolours", "sillyrosettecolours", "dancerosettecolours", "mimirosettecolours",
            "stersinglecolours", "sillysinglecolours", "dancesinglecolours", "mimisinglecolours",
            "stersinglestripecolours", "sillysinglestripecolours", "dancesinglestripecolours", "mimisinglestripecolours",
            "stersmokecolours", "sillysmokecolours", "dancesmokecolours", "mimismokecolours",
            "stersokokecolours", "french_scarves", "ties", "sillysokokecolours", "dancesokokecolours", "mimisokokecolours",
            "sterspeckledcolours", "sillyspeckledcolours", "dancespeckledcolours", "mimispeckledcolours",
            "stertabbycolours", "sillytabbycolours", "dancetabbycolours", "mimitabbycolours",
            "stertickedcolours", "sillytickedcolours", "dancetickedcolours", "mimitickedcolours",
            "boosbandanas_accessories", "sailormoon", "randomaccessories", "star_chimes", "lantern",
            "cs_agouticolours", "cs_bengalcolours", "cs_classiccolours", "cs_mackerelcolours", "cs_marbledcolours", "cs_maskedcolours", "cs_rosettecolours",
            "cs_singlecolours", "cs_singlestripecolours", "cs_smokecolours", "cs_sokokecolours", "cs_speckledcolours", "cs_tabbycolours", "cs_tickedcolours",
            "cs_agouti2colours", "cs_bengal2colours", "cs_classic2colours", "cs_mackerel2colours", "cs_marbled2colours", "cs_masked2colours", "cs_rosette2colours",
            "cs_single2colours", "cs_singlestripe2colours", "cs_smoke2colours", "cs_sokoke2colours", "cs_speckled2colours", "cs_tabby2colours", "cs_ticked2colours",
            "beetle_accessories", "beetle_feathers", "caliisokokecolours", "dotcolours",
            "caliispeckledcolours", "kintsugicolours", "dotfadecolours", "circletabbycolours", "colourpointcolours", "lynxpointcolours", "ncrestedcaracaracolours", "birchtabbycolours",
            "krisagouticolours", "krisbengalcolours", "krisclassiccolours", "krismackerelcolours", "krismarbledcolours", "krismaskedcolours", "krisrosettecolours",
            "krissinglecolours", "krissinglestripecolours", "krissmokecolours", "krissokokecolours", "krisspeckledcolours", "kristabbycolours", "kristickedcolours",
            "meteoragouticolours", "meteorbengalcolours", "meteorclassiccolours", "meteormackerelcolours", "meteormarbledcolours", "meteormaskedcolours", "meteorrosettecolours",
            "meteorsinglecolours", "meteorsinglestripecolours", "meteorsmokecolours", "meteorsokokecolours", "meteorspeckledcolours", "meteortabbycolours", "meteortickedcolours",
            "hiveagouticolours", "hivebengalcolours", "hiveclassiccolours", "hivemackerelcolours", "hivemarbledcolours", "hivemaskedcolours", "hiverosettecolours",
            "hivesinglecolours", "hivesinglestripecolours", "hivesmokecolours", "hivesokokecolours", "hivespeckledcolours", "hivetabbycolours", "hivetickedcolours",
            "pepperagouticolours", "pepperbengalcolours", "pepperclassiccolours", "peppermackerelcolours", "peppermarbledcolours", "pepperrosettecolours",
            "peppersinglecolours", "peppersinglestripecolours", "peppersmokecolours", "peppersokokecolours", "pepperspeckledcolours", "peppertabbycolours", "peppertickedcolours",
            "hetaagouticolours", "hetabengalcolours", "hetaclassiccolours", "hetamackerelcolours", "hetamarbledcolours", "hetarosettecolours",
            "hetasinglecolours", "hetasinglestripecolours", "hetasmokecolours", "hetasokokecolours", "hetaspeckledcolours", "hetatabbycolours", "hetatickedcolours",
            "pastelagouticolours", "pastelbengalcolours", "pastelclassiccolours", "pastelmackerelcolours", "pastelmarbledcolours", "pastelrosettecolours",
            "pastelsinglecolours", "pastelsinglestripecolours", "pastelsmokecolours", "pastelsokokecolours", "pastelspeckledcolours", "pasteltabbycolours", "pasteltickedcolours",
            "sparkleagouticolours", "sparklebengalcolours", "sparkleclassiccolours", "sparklemackerelcolours", "sparklemarbledcolours", "sparklemaskedcolours", "sparklerosettecolours",
            "sparklesinglecolours", "sparklesinglestripecolours", "sparklesmokecolours", "sparklesokokecolours", "sparklespeckledcolours", "sparkletabbycolours", "sparkletickedcolours",
            "prideagouticolours", "pridebengalcolours", "prideclassiccolours", "pridemackerelcolours",
            "minecraftagouticolours", "minecraftbengalcolours", "minecraftclassiccolours", "minecraftmackerelcolours", "minecraftmarbledcolours", "minecraftrosettecolours", "minecraftsinglestripecolours",
            "minecraftsinglecolours", "minecraftsmokecolours", "minecraftsokokecolours", "minecraftspeckledcolours", "minecrafttabbycolours", "minecrafttickedcolours",
            "anjuagouticolours", "anjubengalcolours", "anjuclassiccolours", "anjumackerelcolours", "anjumarbledcolours", "anjurosettecolours",
            "anjusinglecolours", "anjusmokecolours", "anjusokokecolours", "anjuspeckledcolours", "anjutabbycolours", "anjutickedcolours",
            "cs3_agouticolours", "cs3_bengalcolours", "cs3_classiccolours", "cs3_mackerelcolours", "cs3_marbledcolours", "cs3_maskedcolours", "cs3_rosettecolours",
            "cs3_singlecolours", "cs3_singlestripecolours", "cs3_smokecolours", "cs3_sokokecolours", "cs3_speckledcolours", "cs3_tabbycolours", "cs3_tickedcolours",
            "cs_eyes", "primaleyes", "primaleyes2", "paweyesnothers",
            "floraleyes","floraleyes2","aerialeyes","aerialeyes2","aquaticeyes","aquaticeyes2","arideyes","arideyes2",
            "artsi_acc","wildaccs_2", "pride_bandanas", "vickieyes", "heterochromiamask",
            "starcatchermerged", 'stareyesmerged', 'frfoxy_merged', "starcatcher_accs",
            'stormsacc', "meteorcolours",
        ):
            if "lineart" in x and (
                constants.CONFIG["fun"]["april_fools"]
                or is_today(SpecialDate.APRIL_FOOLS)
            ):
                self.spritesheet(f"sprites/aprilfools{x}.png", x)
            else:
                self.spritesheet(f"sprites/{x}.png", x)

        # Line art
        self.make_group("lineart", (0, 0), "lines")
        self.make_group("shadersnewwhite", (0, 0), "shaders")
        self.make_group("lightingnew", (0, 0), "lighting")

        self.make_group("lineartdead", (0, 0), "lineartdead")
        self.make_group("lineartdf", (0, 0), "lineartdf")

        self.make_group("flutter_lineart", (0, 0), "flutter_lines")
        self.make_group("flutter_lineartdead", (0, 0), "flutter_lineartdead")
        self.make_group("flutter_lineartdf", (0, 0), "flutter_lineartdf")

        self.make_group("lamp_lineart", (0, 0), "lamp_lines")
        self.make_group("lamp_lineartdead", (0, 0), "lamp_lineartdead")
        self.make_group("lamp_lineartdf", (0, 0), "lamp_lineartdf")

        # Fading Fog
        for i in range(0, 3):
            self.make_group("fademask", (i, 0), f"fademask{i}")
            self.make_group("fadestarclan", (i, 0), f"fadestarclan{i}")
            self.make_group("fadedarkforest", (i, 0), f"fadedf{i}")

        # Define eye colors
        eye_colors = [
            ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE', 'GREY', 'CYAN', 'EMERALD',
             'HEATHERBLUE', 'SUNLITICE'],
            ['COPPER', 'SAGE', 'COBALT', 'PALEBLUE', 'BRONZE', 'SILVER', 'PALEYELLOW', 'GOLD', 'GREENYELLOW',
             'SUNSET-P', 'RED-P', 'ORANGE-P'],
            ['PURPLE-P', 'PINK-P', 'LILAC-P', 'LAVENDER-P', 'VIOLET-P', 'ROSE-P', 'BLUSH',
            'HOTPINK', 'SALMON', 'CORAL', 'SCARLET', 'SUNRISE'],
            ['MIDNIGHT-P', 'PALE', 'LIGHTRED', 'LIGHTORANGE', 'DARKORANGE', 'DARKPURPLE',
            'LIGHTPURPLE', 'DARKPINK', 'LIGHTPINK', 'DARKGREEN', 'DARKYELLOW', 'FIRE'],
            ['BLURPLE', 'DARKHAZEL', 'LUNAR', 'MINTCHOCOLATE', 'FLOWERFROST', 'SEAGREEN',
            'BLOOM', 'MINT-P', 'REDROSE', 'DARKRED', 'COOLBOW', 'WARMBOW']
        ]
        beetle_eyes = [    
            ['ROSE', 'ALGAE', 'SEAFOAM', 'LIGHT FLAME', 'CLOUDY', 'RED', 'TURQUOISE', 'SWAMP', 'RAINY', 'AQUAMARINE', 'EARTH', 'PUMPKIN'],
            ['LILAC', 'PERIWINKLE', 'VIOLET', 'POND', 'DIRT', 'BROWN', 'CEDAR', 'CHRISTMAS', 'COTTON CANDY', 'VALENTINE', 'FIREWORK', 'LUCKY']
            ]
        beetle_more = [    
            ['DARK PINE', 'FALL', 'FOREST FIRE', 'GOLD MOON', 'HALLOWEEN', 'LOBELIA', 'MIDNIGHT', 'MOONSTONE', 'OXIDIZED', 'SNOW', 'BERRY BANANA', 'DAWN SKY'],
            ['TWILIGHT SKY', 'WORMY', 'BLUE HAZEL', 'THUNDERBOLT', 'VOLCANO', 'SEASHELL', 'PARADOX', 'CURSE', 'BLESSING', 'LIME', 'PALE BROWN', 'CRIMSON']
            ]
        towheeeyes = [    
            ['BULLET', 'LIGHT YELLOW', 'SUNSHINE', 'GOLD ORE', 'FOSSILIZED AMBER', 'DUSKY', 'LICHEN', 'SPRING', 'TREE', 'LEAVES', 'EMERALD ORE', 'HAZELNUT'],
            ['BLUE SKY', 'OCEAN', 'OVERCAST', 'AQUA', 'IRIS', 'ROBIN']
            ]
        eyesdark = [    
            ['GREY SILVER', 'SAND', 'MUSTARD', 'BRONZE ORE', 'TIMBER', 'COPPER ORE', 'FERN', 'APPLE', 'MOSS', 'THICKET', 'PEACOCK', 'OLIVE'],
            ['STORMY BLUE', 'DEPTHS', 'STORMY', 'TEAL', 'INDIGO', 'STEEL']
            ]
        eyesvivid = [    
            ['PEACH', 'DAFFODIL', 'MARIGOLD', 'BRASS', 'DARKAMBER', 'DAWN SKIES', 'MINT', 'CHARTREUSE', 'MEADOW', 'LEAF', 'LIGHT TURQUOISE', 'SAP',],
            ['ALBINISTIC', 'COBALT ORE', 'RAIN', 'CYAN DYE', 'PERIWINKLE PURPLE', 'ICY CRACK']
            ]
        neos_eyes = [['NEO FIRE', 'NEO AMETHYST', 'NEO LIME', 'NEO VIOLET', 'NEO SUN', 'NEO TURQUOISE', 'NEO YELLOW', 'NEO SCARLET', 'NEO PINKPURPLE', 'NEO LIGHTBLUE', 'NEO DARKBLUE', 'NEO CYAN'],
                 ['NEO YELLOWRED', 'NEO PINK', 'NEO INDIGO', 'NEO PURPLE', 'NEO YELLOWGREEN', 'NEO ICEBLUE', 'NEO PALEPINK', 'NEO MINT', 'NEO BLACKBLUE']]
        flutter_eyes = [['FLUTTER SUNSET', 'FLUTTER MONARCH', 'FLUTTER PEACOCK', 'FLUTTER LUNAR', 'FLUTTER GREENORANGE', 'FLUTTER BEACH', 'FLUTTER REDADMIRAL', 'FLUTTER DARK', 'FLUTTER RAINBOW', 'FLUTTER LIGHTBLUE', 'FLUTTER GALAXY', 'FLUTTER STAINEDGLASS'],
                 ['FLUTTER GLASSWING', 'FLUTTER GREENSTRIPE', 'FLUTTER BLUEYELLOW', 'FLUTTER PASTELGALAXY', 'FLUTTER MOTH', 'FLUTTER SPARKLYDUST', 'FLUTTER IMPERIAL', 'FLUTTER PINKHEARTS', 'FLUTTER DUSTOX']]

        lamp_eyes = [['LAMP YELLOW', 'LAMP ORANGE', 'LAMP HAZEL', 'LAMP YELLOWGREEN', 'LAMP GREEN', 'LAMP BLUE', 'LAMP DARKBLUE', 'LAMP GRAY', 'LAMP CYAN', 'LAMP TURQUOISE', 'LAMP PURPLE', 'LAMP GOLD'],
                 ['LAMP ORANGE2', 'LAMP DARKHAZEL', 'LAMP DARKBLUE2', 'LAMP BLUE2', 'LAMP BROWN', 'LAMP PALEYELLOW', 'LAMP LIGHTYELLOW', 'LAMP DARKYELLOW', 'LAMP GOLDENGREEN']]

        angel_eyes = [['ANGEL YELLOW', 'ANGEL ORANGE', 'ANGEL HAZEL', 'ANGEL YELLOWGREEN', 'ANGEL GREEN', 'ANGEL BLUE', 'ANGEL DARKBLUE', 'ANGEL GRAY', 'ANGEL CYAN', 'ANGEL TURQUOISE', 'ANGEL PURPLE', 'ANGEL GOLD'],
                 ['ANGEL COPPER', 'ANGEL MINT', 'ANGEL DARKBLUE2', 'ANGEL BLUE2', 'ANGEL BROWN', 'ANGEL SILVER', 'ANGEL LIGHTYELLOW', 'ANGEL DARKYELLOW', 'ANGEL GOLDENGREEN']]

        snail_eyes = [['SNAIL YELLOW', 'SNAIL ORANGE', 'SNAIL HAZEL', 'SNAIL YELLOWGREEN', 'SNAIL GREEN', 'SNAIL BLUE', 'SNAIL DARKBLUE', 'SNAIL GRAY', 'SNAIL CYAN', 'SNAIL TURQUOISE', 'SNAIL PURPLE', 'SNAIL GOLD'],
                 ['SNAIL COPPER', 'SNAIL MINT', 'SNAIL DARKBLUE2', 'SNAIL BLUE2', 'SNAIL BROWN', 'SNAIL SILVER', 'SNAIL LIGHTYELLOW', 'SNAIL DARKYELLOW', 'SNAIL GOLDENGREEN']]

        # Define era eye colors
        era_eye_colors = [
            ['DARK HAZEL', 'ROSE GOLD', 'DARK ROSE', 'REVERSE SUNLITICE', 'ICY', 'SUNSET', 'LAVENDER', 'ECLIPSE', 'BLACK',
             'MUDDY', 'DARK TURQUOISE', 'BLACKBERRY'],
            ['RUSTY', 'PASTEL', 'AVOCADO', 'PASTEL LAVENDER', 'ALBINO', 'WINTER ROSE', 'PINK', 'MORNING', 'DARK BROWN', 'BAY',
             'NEON GREEN', 'SEA'],
            ['DISCORD', 'AUTUMN LEAF', 'RUBY', 'PHANTOM', 'RIVER MOSS', 'WICKED']
        ]

        cseye_colors = [
            ['BERBERIDA', 'RANUNCULA', 'CAPPARIDA', 'VIOLA', 'FUMARIA', 'PAPAVERA', 'MAGNOLIA'],
            ['POLYGALA', 'RESEDA', 'CISTA', 'NYMPHEA', 'DIPTEROCARPA', 'DILLENIA', 'AMYGDALA'],
            ['ANONA', 'MYRTA', 'TILIA', 'PITTOSPORA', 'MALVA', 'SARRACENIA', 'DROSERA'],
            ['HIPPOCASTANA', 'TROPAEOLA', 'PASSIFLORA', 'OLACA', 'CRUCIA', 'LOASA', 'MALPIGHIA'],
            ['MESEMBRYA', 'VITA', 'MARCGRAVIA', 'CLUSIA', 'BOMBA', 'SAMYDA', 'BIXA'],
            ['GERANIA', 'COMPOSITA', 'RHAMNA', 'OXALIDA', 'ARALIA', 'TEREBINTHA', 'MELIA'],
            ['SAXIFRAGA', 'LINA', 'CAPRIFOLIA', 'CARYOPHYLLA', 'LEGUMINOSAE', 'CAMELLIA', 'CACTACEA'],
            ['JASMINEA', 'LYTHRA', 'ACANTHA', 'CRASSULA', 'RUBIA', 'HYPERICA', 'LORANTHA'],
            ['AURANTIA', 'RHIZOPHORA', 'BORAGINA', 'TAMARICA', 'MELASTOMA', 'LECYTHIDA', 'VALERIANA'],
            ['COMBRETA', 'APOCYNA', 'DIPSA', 'STYLIDIA', 'RUTA', 'SOLANA', 'PLUMBAGINA'],
            ['LAMIA', 'BEGONIA', 'GROSSULARIA', 'GENTIANA', 'ERICA', 'CAMPANULA', 'POMA'],
            ['BIGNONIA', 'AMARANTA', 'VACCINIA', 'ONAGRA', 'PRIMULA', 'SAPOTA', 'LOBELIA'],
            ['MYRSINA', 'PORTULA', 'PLANTAGINA', 'ELAEAGNA', 'OLEA', 'POLEMONIA', 'ORCHIDA'],
            ['EUPHORBIA', 'SCROPHULARIA', 'CONVOLVULA', 'MUSA', 'UTRICULARIA', 'UMBELLA', 'PROTEA'],
            ['GOODENIA', 'THYMELA', 'URTICA', 'OROBANCHA', 'HYDROPHYLLA', 'AMARYLLIDA', 'CONIFERA'],
            ['PHYTOLACCA', 'PAEONIA', 'IRIDA', 'DIOSCORA', 'GESNERIA', 'SANTALA', 'HYDROCHARIDA'],
            ['ZINGIBERA', 'ALISMA', 'POLYGONA', 'NYCTAGINA', 'BROMELIA', 'SMILA', 'EBENA'],
            ['ROSA', 'LILIA', 'JUNCA', 'VERBENA', 'HAEMODORA', 'COMMELINA', 'COLCHICA'],
        ]
        
        vicki_eyes = [
            ['PINWHEEL','BEE', 'VAST FOREST', 'OBSIDIAN', 'WARPED NYLIUM', 'SCULK', 'COPPER GLOW', 'DESERT', 'CUPID',
            'MISSING', 'HESTIA', 'BLOSSOM'],
            ['OVERGROWTH', 'PRIMAL', 'ALLIUM', 'GEM', 'AXOLOTL', 'PARAKEET', 'LUCID DREAM',
            'PETRICHOR', 'AZALEA', 'PEARL']
        ]
        
        starcatcher1 = [
            ['TORBIN', 'DARKLEAP', 'PASTEL BLUES', 'YELLOW SHEEN', 'PUMPKIN ORANGE', 'PASTEL YELLOW', 'ALGAE2', 'ANGELIC SILVER',
             'ANGELIC GREEN'],
            ['SPRAYPAINT PUNK', 'CHROME', 'BLACK CAT', 'VELVETY YELLOW', 'PAINT', 'MINTY', 'PRETTY BLUE',
            'LIGHT MINT', 'MINT GUM', 'SUNSHINE'],
            ['WINTERBERRY FOREST', 'RAINDROP', 'RED EYE', 'PANTHER', 'MELON', 'OXY', 'LILAN', 'LEMONLIME', 'MOONSHINE', 'DULL',
            'DEMONIC RED', 'DULL GREY'],
            ['VELVETY RED', 'SHINY', 'DEMONIC BLUE', 'BRIGHT VELVET', 'DULL BLUE', 'DARK MELON',
            'RED BERRY', 'LIGHT BERRY', 'PAINTED'],
            ['MELON BERRY', 'PASTEL YELLOWGREY', 'DARK MINT', 'PASTELS', 'EMO', 'RED LILY', 'STRAWBERRY', 'PUMPKIN SEED',
            'ANGELIC PASTELS', 'SEED', 'RED ANGELIC', 'DEMONIC BLUE2'],
            ['PASTY YELLOW', 'ALBINO2', 'ANGELIC ALGAE', 'ANGELIC GOLD',
            'BLUD', 'PASTEL LILAC', 'SEASAND', 'ANGELIC SEASAND', 'FIREY AMBER'],
            ['SICKLY GREY', 'GLOW IN THE DARK', 'FRUITY', 'BLOOD', 'PASTEL MINT', 'CUTE PASTELS', 'VALENTINES DAY', 'CUPID2',
            'CUTE SUNSET', 'VERY LIGHT BLUE', 'LIGHT MELON', 'SONNE'],
            ['HOT COCOA', 'LIGHTNING DOG', 'HEADLIGHTS', 'GRAPE SEEDS',
            'YELLOW AND BROWN', 'SEA CORAL', 'BLOODY MARY', 'BLUE CORAL', 'RED FOIL'],
            ['BRIGHT PUMPKIN', 'WOWIE MELON', 'OCEANIC GOLD', 'PAIN', 'BERRY JUICE', 'COTTON CANDY2', 'PINK SUNSET', 'EMO SHINE',
            'JUICY BERRY', 'PURPLE SUNSET', 'LIGHT RED SUNSET', 'ANGELIC SUNSET PASTELS'],
            ['MOONY', 'EMO MINT', 'SEASHELL2',
            'GRASS', 'PASTEL BEACH', 'ANGELIC VELVET', 'LIGHT MINT CHOC', 'DARK ALGAE', 'ANGELIC'],
            ['BURNET', 'DARK BLACK', 'BURNET AMBER', 'LIGHT MELON2', 'OCEANIC SEASHELL', 'CARAMEL APPLE', 'BERRY VELVET',
            'LILAC COFFEE', 'PASTEL HEADLIGHTS', 'EMO WATERMELON', 'CRIMSON LAVA', 'REVERSE ALBINO'],
            ['ALBINO3', 'FOIL GOLD', 'PINK VELVET', 'LOL BLUE', 'LAVA RED', 'RED GREY', 'NORMAL RED', 'RED GREY2', 'DARK PINK VELVET', 'STARDUST']
        ]
        
        freyes1 = [
            ["BRIGHT EARTH FR", "BRIGHT PLAGUE FR", "BRIGHT WIND FR", "BRIGHT WATER FR", "BRIGHT LIGHTNING FR", "BRIGHT ICE FR", "BRIGHT LIGHT FR", "BRIGHT SHADOW FR", "BRIGHT ARCANE FR", "BRIGHT NATURE FR", "BRIGHT FIRE FR", "BASIC EARTH FR"],
            ["BASIC PLAGUE FR", "BASIC WIND FR", "BASIC WATER FR", "BASIC LIGHTNING FR", "BASIC ICE FR", "BASIC SHADOW FR", "BASIC LIGHT FR", "BASIC ARCANE FR", "BASIC NATURE"],
            ["BASIC FIRE FR", "DARK EARTH FR", "DARK PLAGUE FR", "DARK WIND FR", "DARK WATER FR", "DARK LIGHTNING FR", "DARK ICE FR", "DARK SHADOW FR", "DARK LIGHT FR", "DARK ARCANE FR", "DARK NATURE FR","DARK FIRE FR"],
            ["DARK SCLERA EARTH FR", "DARK SCLERA PLAGUE FR", "DARK SCLERA WIND FR", "DARK SCLERA WATER FR", "DARK SCLERA LIGHTNING FR", "DARK SCLERA ICE FR", "DARK SCLERA SHADOW FR", "DARK SCLERA LIGHT FR", "DARK SCLERA ARCANE"],
            ["DARK SCLERA NATURE FR", "FACETED FIRE FR", "FACETED EARTH FR", "FACETED PLAGUE FR", "FACETED WIND FR", "FACETED WATER FR", "FACETED LIGHTNING FR", "FACETED ICE FR", "FACETED SHADOW FR", "FACETED LIGHT FR", "FACETED ARCANE FR", "FACETED NATURE FR"],
            ["FACETED FIRE FR", "GLOWING EARTH FR", "GLOWING PLAGUE FR", "GLOWING WIND FR", "GLOWING WATER FR", "GLOWING LIGHTNING FR", "GLOWING ICE FR", "GLOWING SHADOW FR", "GLOWING LIGHT FR", "GLOWING ARCANE FR"],
            ["GLOWING NATURE FR", "GLOWING FIRE FR", "FADED EARTH FR", "FADED PLAGUE FR", "FADED WIND FR", "FADED WATER FR", "FADED LIGHTNING FR", "FADED ICE FR", "FADED SHADOW FR", "FADED LIGHT FR", "FADED ARCANE FR","FADED NATURE FR"],
            ["FADED FIRE FR", "PASTEL EARTH FR", "PASTEL PLAGUE FR", "PASTEL WIND FR", "PASTEL WATER", "PASTEL LIGHTNING FR", "PASTEL ICE FR", "PASTEL SHADOW FR", "PASTEL LIGHT FR"],
            ["PASTEL ARCANE FR", "PASTEL NATURE FR", "PASTEL FIRE FR", "UNUSUAL EARTH FR", "UNUSUAL PLAGUE FR", "UNUSUAL WIND FR", "UNUSUAL WATER FR", "UNUSUAL LIGHTNING FR", "UNUSUAL ICE FR", "UNUSUAL SHADOW FR", "UNUSUAL LIGHT FR", "UNUSUAL ARCANE FR"],
            ["UNUSUAL NATURE FR", "UNUSUAL FIRE FR", "FACETED EARTH FR", "FACETED PLAGUE FR", "FACETED WIND FR", "FACETED WATER FR", "FACETED LIGHTNING FR", "FACETED ICE FR", "FACETED SHADOW FR"],
            ["BLUE ALBINO", "RED ALBINO", "LIGHT BLUE ALBINO", "CYAN ALBINO", "PINK ALBINO", "DARKSTALKER", "CLAY", "COLD MONOCHROME", "GLORY", "MOON", "WARM MONOCHROME", "PEACEBRINGER"],
            ["PERIL", "PURPLE MYSTERY", "ROSEGOLD FLUTTER", "SEAFOAM SPLASH", "STARFLIGHT", "SUNNY", "SWAMP GOLD", "TSUNAMI", "VELVET"],
            ["ORANGENEW", "GOLD SCARAB", "BLUE MOON", "SUBMERGED", "GRAPE", "BLUEBERRY", "FOOLS GOLD", "DARK BLUE", "LIME", "LIGHT GOLD", "COOKIE", "MERRY CHRISTMAS"],
            ["TRICK OR TREAT", "SPINEL", "NEW DAWN", "DAMP MOSS", "BLIND BLUE", "BLIND GREEN", "BLIND RED", "BLIND PINK", "BLIND PURPLE"]
        ]

        
        primal_eyes = [['PRIMAL ARCANE', 'PRIMAL EARTH', 'PRIMAL FIRE', 'PRIMAL ICE'],
                   ['PRIMAL LIGHT', 'PRIMAL LIGHTNING', 'PRIMAL NATURE', 'PRIMAL PLAGUE'],
                   ['PRIMAL SHADOW', 'PRIMAL WATER', 'PRIMAL WIND']]
        
        paw_eyes = [['TRADITIONAL LUNA PB', 'TRADITIONAL SOL PB', 'TRADITIONAL ABYSSAL PB', 'TRADITIONAL ZENITH PB', 'TRADITIONAL HARVEST PB',
                  'TRADITIONAL COGWHEEL PB', 'TRADITIONAL METROPOLIS', 'VIBRANT LUNA PB', 'VIBRANT SOL PB', 'VIBRANT ABYSSAL PB',
                  'VIBRANT ZENITH PB', 'VIBRANT HARVEST PB'], ['VIBRANT COGWHEEL PB', 'VIBRANT METROPOLIS PB', 'SOLID GOLD',
                  'MISTLETOE', 'OCEAN WATER', 'PINK EYE', 'SEA GREEN', 'TOOTHPASTE', 'MINT CHOCOLATE']]
        
        stareyes10 = [
            ['TORCH','ALLIGATOR','SHINY VIOLET','LAZULI','TRUE SILVER','ORANGE-SILVER','PINK COPPER','PIXIE','PURPLE QUARTZ','MARBLE','PINE','FAUX HETEROCHROMIA',],
            ['BERRIES','BLINDING SUN','JUICY RED','REDPINK','DIANTHUS','IRISH','WINTER BERRY','WASTELAND','SOL','BLUE GLACIER'],
            ['GLAUCOUS','ARIEL','SAFFRON','HUCKLEBERRY','ULYSSES','PINK RUBY','RIDGE','STORMBRINGER','LIME SODA','COYOTE','OPALESCENCE','OBSIDIAN SHADOW'],
            ['TRANS','VELVET SATIN','COPPER LEAF','HAUYNE','PINKISH PURPLE','WORM','AGING COPPER','BUBONIC','SILVER-GREEN','FAIRY'],
            ['TEAL2','DEEP OCEAN','MERCY','SUNNY BROWN','SOFT SHIMMER','IKEA','COINS','DIZZY','RAVER GREEN','MINTY FRESH','BILLFISH','ALMONDS'],
            ['BISTRE','MISTY','WISTERIA','FAUX HETEROCHROMIA2','SHINING SILVER','COVELLITE','DARK MAGENTA','GOLDEN GRAY','CROW','BLUE HAZE'],
            ['FAUX HETEROCHROMIA3','WARM GRAY','EXPOSED BRONZE','WARM TARNISH','HAWKFROST','FAUX HETEROCHROMIA4','LUPINE','MIDNIGHT SHADOW','CAPRISUN','TARNISH','FAUX HETEROCHROMIA5', 'BATESIA'],
            ['FADED INK','FAUX HETEROCHROMIA6','HEMOPIGMENT','ORANGE SODA','ICY CYAN','LILYPAD','RUSTED BLUE','RUSTED NIGHT','EVENING','BLACKBIRD'],
            ['HYDRANGEA','TURQUOISE2','PALE PRIMARY','SAFARI','SOMETHING WICKED','SHINY BROWN','RED GRAY','PRINCESS','PALE INDIGO','ICEBERG','CROCODILE','STARLESS NIGHT'],
            ['NEON TEAL','FAUX HETEROCHROMIA7','SILVER-PINK','MACHINE','FAUX HETEROCHROMIA8','IRON RUBY','FOSSIL','SHARK','HAMMERHEAD','GRAY BROWN'],
            ['SUNSET SEA','CARAMEL DIP','BLUE-GRAY','PALEST PINK','SILVERY TEAL','FISHY','CREAMSICLE','WARM SILVER','APOCALYPSE','HEATHER GRAY','BLUE EMBER','SUMMER',],
            ['DUSTY','BLUE EMBER2','STRANGE CYAN','FADED GOLD','SILVER-16','SHERBERT','JADE','OFF-WHITE','HAUNTING','BLOODMOON'],
            ['GATORADE','WASP','GLARE','PASTEL SUMMER','DARKNESS','LASER BEAM','BRIGHT CYAN','INK JET','LAST SUNSET','HOLLYLEAF','MYSTERY','HADES'],
            ['ICTERINE','DARK CREAM','ALIEN BLUES','RASPBERRY','BLEEDING HEART','BABY BLUE','NEON ORANGE','NEON OPAL','OW THE EDGE','BLUE DRAGON'],
            ['FAIRYWREN','REDBRICK','TRUE GREEN','HAREBELL','WYSTERIA','ORANGE PASTELS','CAPRISUN2','EMBER','PURPLE PUMPKIN','BRIGHT LIME','ORANGE SKY','BRIGHT BI'],
            ['LIGHT GRAY','SEASIDE','CAIN','FIREYS','KELPIE','CELESTITE','PALE ROSE','SOFT PURPLE','SOFT TRANS','ZABA'],
            ['LAVA TRAP','CONCH SHELL','LABRADORITE','ROMANCE','TRAFFIC','ALCIDES','JACKOLANTERN','YELLOW SKY','FROGGY','CAVANSITE','RED-11','FADING LIGHT'],
            ['TORCHLIGHT','CHERRY LEMON','ROOK','SHIMMER','KYANITE','PASTEL BI','CIPHER','GAIA','MINT JADE','PEAR'],
            ['SETTING SUN','PURPLE SKY','FADED PINK','SPARKLING SODA','BRIGHT OLIVE','YEW','MINT LIME','BLUE FLAX','RISING DAWN','BEACHBALL','RED-ORANGE','HOLLY'],
            ['GOLD LEAF','DARKER JACK','ANOTHER ALBINO','MERCURY','RED DUSK','PARROT','VOLCANIC ASH','BISEXUAL','BRIGHT ALBINO','LARKSPUR'],
            ['SPOOKY PASTEL','RIDDLE','HYDRANGEA2','BLITZ','SINISTER','DOVE','OLD WORLD BLUES','BENITOITE','RED-40','CRATER LAKE','BLUE FIRE','GRIM'],
            ['FAUX GRASS','IDIA','DIAMOND','SILVER CYAN','RUBY SAPPHIRE','SPOOKY NIGHT','PINK-SILVER','SHINY VELVET','SYNTHWAVE','CUCUMBER'],
            ['BOYSENBERRY','SOFT MAROON','NEON GRAY','FRESH PUMPKIN','ALMOST BLUE','PINK-BROWN','SUNDOWN','SEAL','PLATINUM2','PEACHY','MALLEUS','UMBER'],
            ['ORANGE-PINK','SNAPDRAGON','BLACKPINK','CHRYSOCOLLA','PINK-ISH','ICHOR','PINK PEONY','CHINCHILLA','SMITHSONITE','PETUNIA'],
            ['SWEETTOOTH','ARTICHOKE','PRINTER INK','MANGROVE','FALLOUT','EDELWEISS','GRAPE SODA','VOID','FADED GREEN','BLACK OPAL','BURNT BLUE','SOFT RED'],
            ['NIGHTWATCH','KELP FOREST','MIDNIGHT VELVET','BUBBLES','HOT CHOCOLATE','FADED INDIGO','CHAOS','MIKU','HONEYBERRY','RED VELVET']
            
        ]

        
        
        for row, colors in enumerate(stareyes10):
            for col, color in enumerate(colors):
                self.make_group('stareyesmerged', (col, row), f'eyes{color}')
        
        for row, colors in enumerate(paw_eyes):
            for col, color in enumerate(colors):
                self.make_group("paweyesnothers", (col, row), f"eyes{color}")
        
        for row, colors in enumerate(primal_eyes):
            for col, color in enumerate(colors):
                self.make_group("primaleyes", (col, row), f"eyes{color}")
                self.make_group("primaleyes2", (col, row), f"eyes2{color}")

        for row, colors in enumerate(cseye_colors):
            for col, color in enumerate(colors):
                self.make_group("cs_eyes", (col, row), f"eyes{color}")

        for row, colors in enumerate(eye_colors):
            for col, color in enumerate(colors):
                self.make_group("eyes", (col, row), f"eyes{color}")

        for row, colors in enumerate(beetle_eyes):
            for col, color in enumerate(colors):
                self.make_group('beetleeyes', (col, row), f'eyes{color}')
        
        for row, colors in enumerate(vicki_eyes):
            for col, color in enumerate(colors):
                self.make_group('vickieyes', (col, row), f'eyes{color}')
        
        for row, colors in enumerate(starcatcher1):
            for col, color in enumerate(colors):
                self.make_group('starcatchermerged', (col, row), f'eyes{color}')
        

        for row, colors in enumerate(beetle_more):
            for col, color in enumerate(colors):
                self.make_group('beetlemore', (col, row), f'eyes{color}')

        for row, colors in enumerate(era_eye_colors):
            for col, color in enumerate(colors):
                self.make_group('eragonaeyes', (col, row), f'eyes{color}')

        for row, colors in enumerate(towheeeyes):
            for col, color in enumerate(colors):
                self.make_group('towheeeyes', (col, row), f'eyes{color}')

        for row, colors in enumerate(eyesdark):
            for col, color in enumerate(colors):
                self.make_group('eyesdark', (col, row), f'eyes{color}')

        for row, colors in enumerate(eyesvivid):
            for col, color in enumerate(colors):
                self.make_group('eyesvivid', (col, row), f'eyes{color}')

        for row, colors in enumerate(neos_eyes):
            for col, color in enumerate(colors):
                self.make_group('neos_eyes', (col, row), f'eyes{color}')
                self.make_group('neos_eyes2', (col, row), f'eyes2{color}')

        for row, colors in enumerate(flutter_eyes):
            for col, color in enumerate(colors):
                self.make_group('flutter_eyes', (col, row), f'eyes{color}')
                self.make_group('flutter_eyes2', (col, row), f'eyes2{color}')

        for row, colors in enumerate(lamp_eyes):
            for col, color in enumerate(colors):
                self.make_group('lamp_eyes', (col, row), f'eyes{color}')
                self.make_group('lamp_eyes', (col, row), f'eyes2{color}')

        for row, colors in enumerate(angel_eyes):
            for col, color in enumerate(colors):
                self.make_group('eyes_wing', (col, row), f'eyes{color}')
                self.make_group('eyes2_halo', (col, row), f'eyes2{color}')

        for row, colors in enumerate(snail_eyes):
            for col, color in enumerate(colors):
                self.make_group('eyes_snail', (col, row), f'eyes{color}')
                
        for row, colors in enumerate(freyes1):
            for col, color in enumerate(colors):
                self.make_group('frfoxy_merged', (col, row), f'eyes{color}')
                
        eye_colors = [
            ['BERBERID-FLORA', 'RANUNCUL-FLORA', 'CAPPARID-FLORA', 'VIOL-FLORA', 'FUMARI-FLORA', 'PAPAVER-FLORA', 'MAGNOLI-FLORA'],
            ['POLYGAL-FLORA', 'RESED-FLORA', 'CIST-FLORA', 'NYMPHE-FLORA', 'DIPTEROCARP-FLORA', 'DILLENI-FLORA', 'AMYGDAL-FLORA'],
            ['ANON-FLORA', 'MYRT-FLORA', 'TILI-FLORA', 'PITTOSPOR-FLORA', 'MALV-FLORA', 'SARRACENI-FLORA', 'DROSER-FLORA'],
            ['HIPPOCASTAN-FLORA', 'TROPAEOL-FLORA', 'PASSIFLOR-FLORA', 'OLAC-FLORA', 'CRUCI-FLORA', 'LOAS-FLORA', 'MALPIGHI-FLORA'],
            ['MESEMBRY-FLORA', 'VIT-FLORA', 'MARCGRAVI-FLORA', 'CLUSI-FLORA', 'BOMB-FLORA', 'SAMYD-FLORA', 'BIX-FLORA'],
            ['GERANI-FLORA', 'COMPOSIT-FLORA', 'RHAMN-FLORA', 'OXALID-FLORA', 'ARALI-FLORA', 'TEREBINTH-FLORA', 'MELI-FLORA'],
            ['SAXIFRAG-FLORA', 'LIN-FLORA', 'CAPRIFOLI-FLORA', 'CARYOPHYLL-FLORA', 'LEGUMINOSAE-FLORA', 'CAMELLI-FLORA', 'CACT-FLORA'],
            ['JASMINE-FLORA', 'LYTHR-FLORA', 'ACANTH-FLORA', 'CRASSUL-FLORA', 'RUBI-FLORA', 'HYPERIC-FLORA', 'LORANTH-FLORA'],
            ['AURANTI-FLORA', 'RHIZOPHOR-FLORA', 'BORAGIN-FLORA', 'TAMARIC-FLORA', 'MELASTOM-FLORA', 'LECYTHID-FLORA', 'VALERIAN-FLORA'],
            ['COMBRET-FLORA', 'APOCYN-FLORA', 'DIPS-FLORA', 'STYLIDI-FLORA', 'RUT-FLORA', 'SOLAN-FLORA', 'PLUMBAGIN-FLORA'],
            ['LAMI-FLORA', 'BEGONI-FLORA', 'GROSSULARI-FLORA', 'GENTIAN-FLORA', 'ERIC-FLORA', 'CAMPANUL-FLORA', 'POM-FLORA'],
            ['BIGNONI-FLORA', 'AMARANT-FLORA', 'VACCINI-FLORA', 'ONAGR-FLORA', 'PRIMUL-FLORA', 'SAPOT-FLORA', 'LOBELI-FLORA'],
            ['MYRSIN-FLORA', 'PORTUL-FLORA', 'PLANTAGIN-FLORA', 'ELAEAGN-FLORA', 'OLE-FLORA', 'POLEMONI-FLORA', 'ORCHID-FLORA'],
            ['EUPHORBI-FLORA', 'SCROPHULARI-FLORA', 'CONVOLVUL-FLORA', 'MUS-FLORA', 'UTRICULARI-FLORA', 'UMBELL-FLORA', 'PROTE-FLORA'],
            ['GOODENI-FLORA', 'THYMEL-FLORA', 'URTIC-FLORA', 'OROBANCH-FLORA', 'HYDROPHYLL-FLORA', 'AMARYLLID-FLORA', 'CONIFER-FLORA'],
            ['PHYTOLACC-FLORA', 'PAEONI-FLORA', 'IRID-FLORA', 'DIOSCOR-FLORA', 'GESNERI-FLORA', 'SANTAL-FLORA', 'HYDROCHARID-FLORA'],
            ['ZINGIBER-FLORA', 'ALISM-FLORA', 'POLYGON-FLORA', 'NYCTAGIN-FLORA', 'BROMELI-FLORA', 'SMIL-FLORA', 'EBEN-FLORA'],
            ['ROS-FLORA', 'LILI-FLORA', 'JUNC-FLORA', 'VERBEN-FLORA', 'HAEMODOR-FLORA', 'COMMELIN-FLORA', 'COLCHIC-FLORA'],
        ]

        for row, colors in enumerate(eye_colors):
            for col, color in enumerate(colors):
                self.make_group("floraleyes", (col, row), f"eyes{color}")
                self.make_group("floraleyes2", (col, row), f"eyes2{color}")
        
        eye_colors = [
            ['BERBERID-AERIAL', 'RANUNCUL-AERIAL', 'CAPPARID-AERIAL', 'VIOL-AERIAL', 'FUMARI-AERIAL', 'PAPAVER-AERIAL', 'MAGNOLI-AERIAL'],
            ['POLYGAL-AERIAL', 'RESED-AERIAL', 'CIST-AERIAL', 'NYMPHE-AERIAL', 'DIPTEROCARP-AERIAL', 'DILLENI-AERIAL', 'AMYGDAL-AERIAL'],
            ['ANON-AERIAL', 'MYRT-AERIAL', 'TILI-AERIAL', 'PITTOSPOR-AERIAL', 'MALV-AERIAL', 'SARRACENI-AERIAL', 'DROSER-AERIAL'],
            ['HIPPOCASTAN-AERIAL', 'TROPAEOL-AERIAL', 'PASSIFLOR-AERIAL', 'OLAC-AERIAL', 'CRUCI-AERIAL', 'LOAS-AERIAL', 'MALPIGHI-AERIAL'],
            ['MESEMBRY-AERIAL', 'VIT-AERIAL', 'MARCGRAVI-AERIAL', 'CLUSI-AERIAL', 'BOMB-AERIAL', 'SAMYD-AERIAL', 'BIX-AERIAL'],
            ['GERANI-AERIAL', 'COMPOSIT-AERIAL', 'RHAMN-AERIAL', 'OXALID-AERIAL', 'ARALI-AERIAL', 'TEREBINTH-AERIAL', 'MELI-AERIAL'],
            ['SAXIFRAG-AERIAL', 'LIN-AERIAL', 'CAPRIFOLI-AERIAL', 'CARYOPHYLL-AERIAL', 'LEGUMINOSAE-AERIAL', 'CAMELLI-AERIAL', 'CACT-AERIAL'],
            ['JASMINE-AERIAL', 'LYTHR-AERIAL', 'ACANTH-AERIAL', 'CRASSUL-AERIAL', 'RUBI-AERIAL', 'HYPERIC-AERIAL', 'LORANTH-AERIAL'],
            ['AURANTI-AERIAL', 'RHIZOPHOR-AERIAL', 'BORAGIN-AERIAL', 'TAMARIC-AERIAL', 'MELASTOM-AERIAL', 'LECYTHID-AERIAL', 'VALERIAN-AERIAL'],
            ['COMBRET-AERIAL', 'APOCYN-AERIAL', 'DIPS-AERIAL', 'STYLIDI-AERIAL', 'RUT-AERIAL', 'SOLAN-AERIAL', 'PLUMBAGIN-AERIAL'],
            ['LAMI-AERIAL', 'BEGONI-AERIAL', 'GROSSULARI-AERIAL', 'GENTIAN-AERIAL', 'ERIC-AERIAL', 'CAMPANUL-AERIAL', 'POM-AERIAL'],
            ['BIGNONI-AERIAL', 'AMARANT-AERIAL', 'VACCINI-AERIAL', 'ONAGR-AERIAL', 'PRIMUL-AERIAL', 'SAPOT-AERIAL', 'LOBELI-AERIAL'],
            ['MYRSIN-AERIAL', 'PORTUL-AERIAL', 'PLANTAGIN-AERIAL', 'ELAEAGN-AERIAL', 'OLE-AERIAL', 'POLEMONI-AERIAL', 'ORCHID-AERIAL'],
            ['EUPHORBI-AERIAL', 'SCROPHULARI-AERIAL', 'CONVOLVUL-AERIAL', 'MUS-AERIAL', 'UTRICULARI-AERIAL', 'UMBELL-AERIAL', 'PROTE-AERIAL'],
            ['GOODENI-AERIAL', 'THYMEL-AERIAL', 'URTIC-AERIAL', 'OROBANCH-AERIAL', 'HYDROPHYLL-AERIAL', 'AMARYLLID-AERIAL', 'CONIFER-AERIAL'],
            ['PHYTOLACC-AERIAL', 'PAEONI-AERIAL', 'IRID-AERIAL', 'DIOSCOR-AERIAL', 'GESNERI-AERIAL', 'SANTAL-AERIAL', 'HYDROCHARID-AERIAL'],
            ['ZINGIBER-AERIAL', 'ALISM-AERIAL', 'POLYGON-AERIAL', 'NYCTAGIN-AERIAL', 'BROMELI-AERIAL', 'SMIL-AERIAL', 'EBEN-AERIAL'],
            ['ROS-AERIAL', 'LILI-AERIAL', 'JUNC-AERIAL', 'VERBEN-AERIAL', 'HAEMODOR-AERIAL', 'COMMELIN-AERIAL', 'COLCHIC-AERIAL']
        ]

        for row, colors in enumerate(eye_colors):
            for col, color in enumerate(colors):
                self.make_group("aerialeyes", (col, row), f"eyes{color}")
                self.make_group("aerialeyes2", (col, row), f"eyes2{color}")
        
        eye_colors = [
            ['BERBERID-AQUATIC', 'RANUNCUL-AQUATIC', 'CAPPARID-AQUATIC', 'VIOL-AQUATIC', 'FUMARI-AQUATIC', 'PAPAVER-AQUATIC', 'MAGNOLI-AQUATIC'],
            ['POLYGAL-AQUATIC', 'RESED-AQUATIC', 'CIST-AQUATIC', 'NYMPHE-AQUATIC', 'DIPTEROCARP-AQUATIC', 'DILLENI-AQUATIC', 'AMYGDAL-AQUATIC'],
            ['ANON-AQUATIC', 'MYRT-AQUATIC', 'TILI-AQUATIC', 'PITTOSPOR-AQUATIC', 'MALV-AQUATIC', 'SARRACENI-AQUATIC', 'DROSER-AQUATIC'],
            ['HIPPOCASTAN-AQUATIC', 'TROPAEOL-AQUATIC', 'PASSIFLOR-AQUATIC', 'OLAC-AQUATIC', 'CRUCI-AQUATIC', 'LOAS-AQUATIC', 'MALPIGHI-AQUATIC'],
            ['MESEMBRY-AQUATIC', 'VIT-AQUATIC', 'MARCGRAVI-AQUATIC', 'CLUSI-AQUATIC', 'BOMB-AQUATIC', 'SAMYD-AQUATIC', 'BIX-AQUATIC'],
            ['GERANI-AQUATIC', 'COMPOSIT-AQUATIC', 'RHAMN-AQUATIC', 'OXALID-AQUATIC', 'ARALI-AQUATIC', 'TEREBINTH-AQUATIC', 'MELI-AQUATIC'],
            ['SAXIFRAG-AQUATIC', 'LIN-AQUATIC', 'CAPRIFOLI-AQUATIC', 'CARYOPHYLL-AQUATIC', 'LEGUMINOSAE-AQUATIC', 'CAMELLI-AQUATIC', 'CACT-AQUATIC'],
            ['JASMINE-AQUATIC', 'LYTHR-AQUATIC', 'ACANTH-AQUATIC', 'CRASSUL-AQUATIC', 'RUBI-AQUATIC', 'HYPERIC-AQUATIC', 'LORANTH-AQUATIC'],
            ['AURANTI-AQUATIC', 'RHIZOPHOR-AQUATIC', 'BORAGIN-AQUATIC', 'TAMARIC-AQUATIC', 'MELASTOM-AQUATIC', 'LECYTHID-AQUATIC', 'VALERIAN-AQUATIC'],
            ['COMBRET-AQUATIC', 'APOCYN-AQUATIC', 'DIPS-AQUATIC', 'STYLIDI-AQUATIC', 'RUT-AQUATIC', 'SOLAN-AQUATIC', 'PLUMBAGIN-AQUATIC'],
            ['LAMI-AQUATIC', 'BEGONI-AQUATIC', 'GROSSULARI-AQUATIC', 'GENTIAN-AQUATIC', 'ERIC-AQUATIC', 'CAMPANUL-AQUATIC', 'POM-AQUATIC'],
            ['BIGNONI-AQUATIC', 'AMARANT-AQUATIC', 'VACCINI-AQUATIC', 'ONAGR-AQUATIC', 'PRIMUL-AQUATIC', 'SAPOT-AQUATIC', 'LOBELI-AQUATIC'],
            ['MYRSIN-AQUATIC', 'PORTUL-AQUATIC', 'PLANTAGIN-AQUATIC', 'ELAEAGN-AQUATIC', 'OLE-AQUATIC', 'POLEMONI-AQUATIC', 'ORCHID-AQUATIC'],
            ['EUPHORBI-AQUATIC', 'SCROPHULARI-AQUATIC', 'CONVOLVUL-AQUATIC', 'MUS-AQUATIC', 'UTRICULARI-AQUATIC', 'UMBELL-AQUATIC', 'PROTE-AQUATIC'],
            ['GOODENI-AQUATIC', 'THYMEL-AQUATIC', 'URTIC-AQUATIC', 'OROBANCH-AQUATIC', 'HYDROPHYLL-AQUATIC', 'AMARYLLID-AQUATIC', 'CONIFER-AQUATIC'],
            ['PHYTOLACC-AQUATIC', 'PAEONI-AQUATIC', 'IRID-AQUATIC', 'DIOSCOR-AQUATIC', 'GESNERI-AQUATIC', 'SANTAL-AQUATIC', 'HYDROCHARID-AQUATIC'],
            ['ZINGIBER-AQUATIC', 'ALISM-AQUATIC', 'POLYGON-AQUATIC', 'NYCTAGIN-AQUATIC', 'BROMELI-AQUATIC', 'SMIL-AQUATIC', 'EBEN-AQUATIC'],
            ['ROS-AQUATIC', 'LILI-AQUATIC', 'JUNC-AQUATIC', 'VERBEN-AQUATIC', 'HAEMODOR-AQUATIC', 'COMMELIN-AQUATIC', 'COLCHIC-AQUATIC']
        ]

        for row, colors in enumerate(eye_colors):
            for col, color in enumerate(colors):
                self.make_group("aquaticeyes", (col, row), f"eyes{color}")
                self.make_group("aquaticeyes2", (col, row), f"eyes2{color}")
        
        eye_colors = [
            ['BERBERID-DEMON', 'RANUNCUL-DEMON', 'CAPPARID-DEMON', 'VIOL-DEMON', 'FUMARI-DEMON', 'PAPAVER-DEMON', 'MAGNOLI-DEMON'],
            ['POLYGAL-DEMON', 'RESED-DEMON', 'CIST-DEMON', 'NYMPHE-DEMON', 'DIPTEROCARP-DEMON', 'DILLENI-DEMON', 'AMYGDAL-DEMON'],
            ['ANON-DEMON', 'MYRT-DEMON', 'TILI-DEMON', 'PITTOSPOR-DEMON', 'MALV-DEMON', 'SARRACENI-DEMON', 'DROSER-DEMON'],
            ['HIPPOCASTAN-DEMON', 'TROPAEOL-DEMON', 'PASSIFLOR-DEMON', 'OLAC-DEMON', 'CRUCI-DEMON', 'LOAS-DEMON', 'MALPIGHI-DEMON'],
            ['MESEMBRY-DEMON', 'VIT-DEMON', 'MARCGRAVI-DEMON', 'CLUSI-DEMON', 'BOMB-DEMON', 'SAMYD-DEMON', 'BIX-DEMON'],
            ['GERANI-DEMON', 'COMPOSIT-DEMON', 'RHAMN-DEMON', 'OXALID-DEMON', 'ARALI-DEMON', 'TEREBINTH-DEMON', 'MELI-DEMON'],
            ['SAXIFRAG-DEMON', 'LIN-DEMON', 'CAPRIFOLI-DEMON', 'CARYOPHYLL-DEMON', 'LEGUMINOSAE-DEMON', 'CAMELLI-DEMON', 'CACT-DEMON'],
            ['JASMINE-DEMON', 'LYTHR-DEMON', 'ACANTH-DEMON', 'CRASSUL-DEMON', 'RUBI-DEMON', 'HYPERIC-DEMON', 'LORANTH-DEMON'],
            ['AURANTI-DEMON', 'RHIZOPHOR-DEMON', 'BORAGIN-DEMON', 'TAMARIC-DEMON', 'MELASTOM-DEMON', 'LECYTHID-DEMON', 'VALERIAN-DEMON'],
            ['COMBRET-DEMON', 'APOCYN-DEMON', 'DIPS-DEMON', 'STYLIDI-DEMON', 'RUT-DEMON', 'SOLAN-DEMON', 'PLUMBAGIN-DEMON'],
            ['LAMI-DEMON', 'BEGONI-DEMON', 'GROSSULARI-DEMON', 'GENTIAN-DEMON', 'ERIC-DEMON', 'CAMPANUL-DEMON', 'POM-DEMON'],
            ['BIGNONI-DEMON', 'AMARANT-DEMON', 'VACCINI-DEMON', 'ONAGR-DEMON', 'PRIMUL-DEMON', 'SAPOT-DEMON', 'LOBELI-DEMON'],
            ['MYRSIN-DEMON', 'PORTUL-DEMON', 'PLANTAGIN-DEMON', 'ELAEAGN-DEMON', 'OLE-DEMON', 'POLEMONI-DEMON', 'ORCHID-DEMON'],
            ['EUPHORBI-DEMON', 'SCROPHULARI-DEMON', 'CONVOLVUL-DEMON', 'MUS-DEMON', 'UTRICULARI-DEMON', 'UMBELL-DEMON', 'PROTE-DEMON'],
            ['GOODENI-DEMON', 'THYMEL-DEMON', 'URTIC-DEMON', 'OROBANCH-DEMON', 'HYDROPHYLL-DEMON', 'AMARYLLID-DEMON', 'CONIFER-DEMON'],
            ['PHYTOLACC-DEMON', 'PAEONI-DEMON', 'IRID-DEMON', 'DIOSCOR-DEMON', 'GESNERI-DEMON', 'SANTAL-DEMON', 'HYDROCHARID-DEMON'],
            ['ZINGIBER-DEMON', 'ALISM-DEMON', 'POLYGON-DEMON', 'NYCTAGIN-DEMON', 'BROMELI-DEMON', 'SMIL-DEMON', 'EBEN-DEMON'],
            ['ROS-DEMON', 'LILI-DEMON', 'JUNC-DEMON', 'VERBEN-DEMON', 'HAEMODOR-DEMON', 'COMMELIN-DEMON', 'COLCHIC-DEMON']
        ]

        for row, colors in enumerate(eye_colors):
            for col, color in enumerate(colors):
                self.make_group("arideyes", (col, row), f"eyes{color}")
                self.make_group("arideyes2", (col, row), f"eyes2{color}")

        # toritemasktwo
        torite_mask_two = [
            ['CHAOSONE', 'CHAOSTWO', 'CHAOSTHREE', 'CHAOSFOUR', 'ERROR', 'WAVE', 'PONINTTORITE', 'MASKTORITE', 'LITTLESTAR', 'TANBUNNY'],
            ['STRIPES', 'PINITO', 'SKULL', 'SIGHT', 'BRINDLETORITE', 'SNOW', 'ROSETTESTORITE', 'AMBERONE', 'KINTSUGIONE', 'BENGALMASK'],
            ['SHADOW', 'RAIN', 'MGLA', 'MOONLIGHT', 'MOUSE', 'SATURN', 'MARBLETORINE', 'AMBERTWO', 'PATTERN', 'MOSS'],
            ['MONKEY', 'BUMBLEBEE', 'KINTSUGITWO', 'STORM', 'CLASSICTORNIE', 'STRIPEONETORITE', 'MACKERELTORITE', 'AMBERTHREE', 'SHADE', 'GRAFFITI'],
            ['AGOUTITORIE', 'BENGALTORITE', 'TABBYTORITE', 'SOKKOKETORITE', 'SPECKLEDTORITE', 'TICKEDTORIE', 'MORRO', 'AMBERFOUR', 'DOG', 'ONESPOT'],

           ]

        # Define white patches
        white_patches = [
            [
                "FULLWHITE",
                "ANY",
                "TUXEDO",
                "LITTLE",
                "COLOURPOINT",
                "VAN",
                "ANYTWO",
                "MOON",
                "PHANTOM",
                "POWDER",
                "BLEACHED",
                "SAVANNAH",
                "FADESPOTS",
                "PEBBLESHINE",
            ],
            [
                "EXTRA",
                "ONEEAR",
                "BROKEN",
                "LIGHTTUXEDO",
                "BUZZARDFANG",
                "RAGDOLL",
                "LIGHTSONG",
                "VITILIGO",
                "BLACKSTAR",
                "PIEBALD",
                "CURVED",
                "PETAL",
                "SHIBAINU",
                "OWL",
            ],
            [
                "TIP",
                "FANCY",
                "FRECKLES",
                "RINGTAIL",
                "HALFFACE",
                "PANTSTWO",
                "GOATEE",
                "VITILIGOTWO",
                "PAWS",
                "MITAINE",
                "BROKENBLAZE",
                "SCOURGE",
                "DIVA",
                "BEARD",
            ],
            [
                "TAIL",
                "BLAZE",
                "PRINCE",
                "BIB",
                "VEE",
                "UNDERS",
                "HONEY",
                "FAROFA",
                "DAMIEN",
                "MISTER",
                "BELLY",
                "TAILTIP",
                "TOES",
                "TOPCOVER",
            ],
            [
                "APRON",
                "CAPSADDLE",
                "MASKMANTLE",
                "SQUEAKS",
                "STAR",
                "TOESTAIL",
                "RAVENPAW",
                "PANTS",
                "REVERSEPANTS",
                "SKUNK",
                "KARPATI",
                "HALFWHITE",
                "APPALOOSA",
                "DAPPLEPAW",
            ],
            [
                "HEART",
                "LILTWO",
                "GLASS",
                "MOORISH",
                "SEPIAPOINT",
                "MINKPOINT",
                "SEALPOINT",
                "MAO",
                "LUNA",
                "CHESTSPECK",
                "WINGS",
                "PAINTED",
                "HEARTTWO",
                "WOODPECKER",
            ],
            [
                "BOOTS",
                "MISS",
                "COW",
                "COWTWO",
                "BUB",
                "BOWTIE",
                "MUSTACHE",
                "REVERSEHEART",
                "SPARROW",
                "VEST",
                "LOVEBUG",
                "TRIXIE",
                "SAMMY",
                "SPARKLE",
            ],
            [
                "RIGHTEAR",
                "LEFTEAR",
                "ESTRELLA",
                "SHOOTINGSTAR",
                "EYESPOT",
                "REVERSEEYE",
                "FADEBELLY",
                "FRONT",
                "BLOSSOMSTEP",
                "PEBBLE",
                "TAILTWO",
                "BUDDY",
                "BACKSPOT",
                "EYEBAGS",
            ],
            [
                "BULLSEYE",
                "FINN",
                "DIGIT",
                "KROPKA",
                "FCTWO",
                "FCONE",
                "MIA",
                "SCAR",
                "BUSTER",
                "SMOKEY",
                "HAWKBLAZE",
                "CAKE",
                "ROSINA",
                "PRINCESS",
            ],
            ["LOCKET", "BLAZEMASK", "TEARS", "DOUGIE"],
        ]
        # Define mink's white patches
        minks_white_patches = [
            ['MINKONE', 'MINKTWO', 'MINKTHREE', 'MINKFOUR', 'MINKREDTAIL', 'MINKDELILAH', 'MINKHALF', 'MINKSTREAK',
             'MINKMASK', 'MINKSMOKE'],
            ['MINKMINIMALONE', 'MINKMINIMALTWO', 'MINKMINIMALTHREE', 'MINKMINIMALFOUR', 'MINKOREO', 'MINKSWOOP',
             'MINKCHIMERA', 'MINKCHEST', 'MINKARMTAIL',
             'MINKGRUMPYFACE'],
            ['MINKMOTTLED', 'MINKSIDEMASK', 'MINKEYEDOT', 'MINKBANDANA', 'MINKPACMAN', 'MINKSTREAMSTRIKE',
             'MINKSMUDGED', 'MINKDAUB', 'MINKEMBER', 'MINKBRIE'],
            ['MINKORIOLE', 'MINKROBIN', 'MINKBRINDLE', 'MINKPAIGE', 'MINKROSETAIL', 'MINKSAFI', 'MINKDAPPLENIGHT',
             'MINKBLANKET', 'MINKBELOVED', 'MINKBODY'],
            ['MINKSHILOH', 'MINKFRECKLED', 'MINKHEARTBEAT']
        ]

        exotic_white_patches = [
            ['JACKAL', 'CHITAL']    
        ]

        # Define era white patches
        era_white_patches = [
            ['INK', 'WOLF', 'EYEV', 'GEM', 'FOX', 'ORCA', 'PINTO', 'FRECKLESTWO', 'SOLDIER',
             'AKITA'],
            ['CHESSBORAD', 'ANT', 'CREAMV', 'BUNNY', 'MOJO', 'STAINSONE', 'STAINST',
              'HALFHEART', 'FRECKLESTHREE', 'KITTY'],
            ['SUNRISE', 'HUSKY', 'STATNTHREE', 'ERAMASK', 'S', 'PAW', 'SWIFTPAW', 'BOOMSTAR', 'MIST', 'LEON'],
            ['LADY', 'LEGS', 'MEADOW', 'SALT', 'BAMBI', 'PRIMITVE', 'SKUNKSTRIPE', 'NEPTUNE', 'KARAPATITWO', 'CHAOS'],
            ['MOSCOW', 'ERAHALF', 'CAPETOWN', 'SUN', 'BANAN', 'PANDA', 'DOVE', 'PINTOTWO', 'SNOWSHOE', 'SKY'],
            ['MOONSTONE', 'DRIP', 'CRESCENT', 'ETERNAL', 'WINGTWO', 'STARBORN', 'SPIDERLEGS', 'APPEL', 'RUG', 'LUCKY'],
            ['SOCKS', 'BRAMBLEBERRY', 'LATKA', 'ASTRONAUT', 'STORK']
        ]
        for row, patches in enumerate(white_patches):
            for col, patch in enumerate(patches):
                self.make_group("whitepatches", (col, row), f"white{patch}")
        for row, minkpatches in enumerate(minks_white_patches):
            for col, minkpatch in enumerate(minkpatches):
                self.make_group('minkswhite', (col, row), f'white{minkpatch}')

        for row, patches in enumerate(white_patches):
            for col, patch in enumerate(patches):
                self.make_group('whitepatches', (col, row), f'white{patch}')
        for row, patches in enumerate(exotic_white_patches):
            for col, patch in enumerate(patches):
                self.make_group('exoticwhitepatches', (col, row), f'white{patch}')

        for row, wps in enumerate(era_white_patches):
            for col, wp in enumerate(wps):
                self.make_group('eragonawp', (col, row), f'white{wp}')

        for row, wps in enumerate(torite_mask_two):
            for col, wp in enumerate(wps):
                self.make_group('eragonatorite', (col, row), f'white{wp}')

        voithex_patches = [
            ['BODYSTRIPE', 'BLACKBODYSTRIPE', 'BROWNBODYSTRIPE', 'GINGERBODYSTRIPE', 'TIGERBODYSTRIPE', 'BLACKTIGERBODYSTRIPE', 'BROWNTIGERBODYSTRIPE',
             'GINGERTIGERBODYSTRIPE', 'SPRAYEDBODYSTRIPE', 'BLACKSPRAYEDBODYSTRIPE', 'BROWNSPRAYEDBODYSTRIPE', 'GINGERSPRAYEDBODYSTRIPE'],
            ['REVERSEBODYSPRITE', 'BLACKREVERSEBODYSPRITE', 'BROWNREVERSEBODYSPRITE', 'GINGERREVERSEBODYSPRITE', 'REVERSETIGERBODYSPRITE',
             'BLACKREVERSETIGERBODYSPRITE', 'BROWNREVERSETIGERBODYSPRITE', 'GINGERREVERSETIGERBODYSPRITE', 'REVERSELEOPARDBODYSPRITE',
             'BLACKREVERSELEOPARDBODYSPRITE', 'BROWNREVERSELEOPARDBODYSPRITE', 'GINGERREVERSELEOPARDBODYSPRITE']
        ]
        for row, vopatches in enumerate(voithex_patches):
            for col, vopatch in enumerate(vopatches):
                self.make_group('voithexpatches', (col, row), f'white{vopatch}')

        # Define colors and categories
        color_categories = [
            ["WHITE", "PALEGREY", "SILVER", "GREY", "DARKGREY", "GHOST", "BLACK"],
            ["CREAM", "PALEGINGER", "GOLDEN", "GINGER", "DARKGINGER", "SIENNA"],
            ["LIGHTBROWN", "LILAC", "BROWN", "GOLDEN-BROWN", "DARKBROWN", "CHOCOLATE"],
        ]

        minecraft_color_categories = [
            ['ACACIALOG', 'BAMBOO', 'BIRCHLOG', 'CHERRYLOG', 'CRIMSONSTEM', 'DARKOAKLOG', 'JUNGLELOG', 'MANGROVELOG', 'OAKLOG', 'SPRUCELOG', 'WARPEDSTEM'],
            ['ACACIAPLANKS', 'BAMBOOPLANKS', 'BIRCHPLANKS', 'CHERRYPLANKS', 'CRIMSONPLANKS', 'DARKOAKPLANKS', 'JUNGLEPLANKS', 'MANGROVEPLANKS', 'OAKPLANKS', 'SPRUCEPLANKS', 'WARPEDPLANKS'],
            ['AMETHYST', 'BLACKGLAZEDTERRACOTTA', 'BLUEGLAZEDTERRACOTTA', 'BROWNGLAZEDTERRACOTTA', 'BROWN MUSHROOM', 'COPPER', 'CRYING OBSIDIAN', 'CYANGLAZEDTERRACOTTA', 'EXPOSEDCOPPER', 'GRAYGLAZEDTERRACOTTA', 'GREENGLAZEDTERRACOTTA'],
            ['LIGHTBLUEGLAZED TERRACOTTA', 'LIGHTGRAYGLAZEDTERRACOTTA', 'LIMEGLAZEDTERRACOTTA', 'MAGENTAGLAZEDTERRACOTTA', 'MUSHROOMINSIDE', 'MUSHROOMSTEM', 'OBSIDIAN', 'ORANGEGLAZEDTERRACOTTA', 'OXIDIZEDCOPPER', 'PINKGLAZEDTERRACOTTA', 'PURPLEGLAZEDTERRACOTTA'],
            ['PURPUR', 'QUARTZ', 'REDGLAZEDTERRACOTTA', 'REDMUSHROOM', 'WEATHEREDCOPPER', 'WHITEGLAZEDTERRACOTTA', 'YELLOWGLAZEDTERRACOTTA']
        ]

        anju_color_categories = [['PINK', 'RED', 'LIGHTGREEN', 'GREEN', 'CYAN', 'BLUE', 'PURPLE']]

        cs2_color_categories = [
            ['LIGHTLIME', 'PINKGREY', 'YELLOWBROWN', 'REDGREY', 'BLUEBROWN', 'GHOSTBROWN', 'BLACKPURPLE'],
            ['BLUECREAM', 'PALEPINKPURPLE', 'ICEBLUE', 'BLUECS2', 'GREENBROWN', 'NAVYBLUE'],
            ['PURPLECREAM', 'INDIGOBLUSH', 'VIOLETBLUSH', 'MAGENTA', 'NAVYBROWN', 'MULBERRY']
        ]

        cs_color_categories = [
                ['ICEWHITE', 'CRYSTAL', 'ORCHID', 'CERULEAN', 'GRAPE', 'GHOSTBLUE', 'BLACKBLUE'],
                ['THISTLE', 'SUNYELLOW', 'BUBBLEGUM', 'REDSTAIN', 'ROSE', 'DUSKBROWN'],
                ['FROZENSUN', 'GREENGOLD', 'OCEAN', 'TEAL', 'REDBLUE', 'TREE']
        ]

        heta_color_categories = [
            ['REDHETA', 'ORANGEHETA', 'YELLOWHETA', 'NEONYELLOW', 'NEONGREEN', 'GREENHETA', 'MINTGREEN'],
            ['DARKMINT', 'NEONTEAL', 'CYANHETA', 'BLUEHETA', 'NAVYHETA', 'INDIGOHETA'],
            ['PURPLEHETA', 'VIOLETHETA', 'MAGENTAHETA', 'PINKHETA', 'SCARLETPINK', 'DARKREDHETA']
        ]

        # mega colors mod

        dance_color_categories = [
            ['LIGHTCINNAMON', 'CINNAMON', 'SILVERFAWN', 'DARKCINNAMON', 'DARKFAWN', 'FAWN', 'LIGHTFAWN'],
            ['PALEFAWN', 'PALECREAM', 'LIGHTCREAM', 'DANCECREAM', 'DARKCREAM', 'DARKGOLD'],
            ['GOLD', 'LIGHTGOLD', 'SILVERCREAM', 'PALEGOLD', 'SUNSHINE', 'BRONZE']
        ]

        silly_color_categories = [
            ['LIGHTLILAC', 'LILACSILLY', 'DARKLILAC', 'DARKASH', 'ASH', 'LIGHTASH', 'PALEASH'],
            ['SILVERCINNAMON', 'SILVERRED', 'PALEBROWN', 'LIGHTBROWNSILLY', 'BROWNSILLY', 'DARKBROWNSILLY'],
            ['EBONY', 'DARKCHOCOLATE', 'CHOCOLATESILLY', 'LIGHTCHOCOLATE', 'PALECHOCOLATE', 'PALECINNAMON']
        ]

        ster_color_categories = [
            ['WHITESTER', 'PALEGREYSTER', 'LIGHTGREY', 'GREYSTER', 'DARKGREYSTER', 'BLACKSTER', 'OBSIDIANSTER'],
            ['GHOSTSTER', 'PALEBLUE', 'LIGHTBLUE', 'BLUESTER', 'DARKBLUE', 'SILVERCHOCOLATE'],
            ['SILVERORANGE', 'DARKSLATE', 'SLATE', 'LIGHTSLATE', 'PALESLATE', 'PALELILAC']
        ]

        mimi_color_categories= [
            ['COPPERMIMI', 'DARKORANGE', 'ORANGE', 'LIGHTORANGE', 'PALEORANGE', 'PALEGINGERMIMI', 'LIGHTGINGER'],
            ['GINGERMIMI', 'DARKGINGERMIMI', 'SILVERGOLD', 'RUSSET', 'DARKRED', 'REDMIMI'],
            ['LIGHTRED', 'PALERED', 'SILVERMIMI', 'SILVERGREY', 'SILVERBLUE', 'SILVERSLATE']
        ]

        hive_color_categories = [
            ['GREENH', 'TEALH', 'BLUEH', 'NAVYH', 'INDIGOH', 'PURPLEH', 'VIOLETH'],
            ['PINKH', 'ROSEH', 'DARKPINKH', 'REDH', 'ORANGEH', 'GOLDH'],
            ['PASTELPURPLEH', 'DARKGREENH', 'BROWN-PURPLE', 'YELLOWH', 'DARKMOSS', 'PURPLESWIRL']
        ]

        kris_color_categories = [
            ['PINKCREAM', 'BLUEMINT', 'SUNSET', 'PINK-BLUE', 'INDIGOK', 'BLUEGHOSTK', 'PINKK'],
            ['PASTELPINKBLUE', 'RUSTYGREEN', 'OURPLE', 'BLUE-YELLOW', 'BLUE-PURPLE', 'DARKSUNSET'],
            ['BANANABERRY', 'BRIGHTBLUEK', 'SUNRISE', 'GREEN-NAVY', 'PINKSHADOW', 'REDK']
        ]

        meteor_color_categories = [
            ['SILVERMETEOR', 'SILVERNAVY', 'CREAMSILVER', 'GREYSTAR', 'DARKGREYSTAR', 'BLACK-BROWN', 'BLUESPOTTED'],
            ['CREAMMETEOR', 'PINK-WHITE', 'TANSPOTTED', 'REVERSESUN', 'WARM-BLUE', 'INDIGO-VIOLET'],
            ['GREYMETEOR', 'ICESPOTTED', 'SHADOW', 'BLUE-EARTH', 'EARTHSPOTTED', 'BROWN-TAN']
        ]

        pastel_color_categories = [
            ['PALEPINK-PURPLE', 'PALEGREY-PINK', 'PALEBLUE-YELLOW', 'PALEMINT-PURPLE', 'PALEGREEN-INDIGO', 'PALEYELLOW-INDIGO', 'PALEORANGE-BLUE'],
            ['PALEPURPLE-GOLD', 'PALECYAN-GOLD', 'PALEMINT-MAGENTA', 'PALEMINT-VIOLET', 'PALEGREEN-BLUE', 'PALEGREEN-NAVY'],
            ['PALEBLUE-INDIGO', 'PALECYAN-PURPLE', 'PALECYAN-NAVY', 'PALECYAN-BLUE', 'PALEYELLOWGREEN', 'PALEYELLOW-BLUE']
        ]

        pepper_color_categories = [
            ['ICEPEPPER', 'CYANPEPPER', 'BLUEPEPPER', 'OCEANPEPPER', 'DARKBLUEPEPPER', 'BLUEGHOSTPEPPER', 'BLACKBLUEPEPPER'],
            ['GOLDCREAM', 'GOLDPEPPER', 'YELLOW-RED', 'BRIGHTYELLOW-RED', 'NEONRED', 'REDBLACK'],
            ['PALEBLUE-GOLD', 'INDIGOPEPPER', 'RUSTBLUEPEPPER', 'REDPEPPER', 'REDBLUEBLACK', 'SCARLETPEPPER']
        ]

        sparkle_color_categories = [
            ['REDS', 'RED-ORANGES', 'DARKYELLOWS', 'GREENREDS', 'CYANPINKG', 'INDIGOREDS', 'REVERSERAINBOW'],
            ['PINKREDS', 'RUSTYS', 'GREENORANGES', 'REDCYANS', 'MINTBLUES', 'BLACKBLUES'],
            ['BANANAS', 'WHITEGREENS', 'BROWNREDS', 'RAINBOW', 'GREENDARKREDS', 'SUNNYS']
        ]

        cs3_color_categories = [
            ['BERBERIDA', 'RANUNCULA', 'CAPPARIDA', 'VIOLA', 'FUMARIA', 'PAPAVERA', 'MAGNOLIA'],
            ['POLYGALA', 'RESEDA', 'CISTA', 'NYMPHEA', 'DIPTEROCARPA', 'DILLENIA', 'AMYGDALA'],
            ['ANONA', 'MYRTA', 'TILIA', 'PITTOSPORA', 'MALVA', 'SARRACENIA', 'DROSERA'],
            ['HIPPOCASTANA', 'TROPAEOLA', 'PASSIFLORA', 'OLACA', 'CRUCIA', 'LOASA', 'MALPIGHIA'],
            ['MESEMBRYA', 'VITA', 'MARCGRAVIA', 'CLUSIA', 'BOMBA', 'SAMYDA', 'BIXA'],
            ['GERANIA', 'COMPOSITA', 'RHAMNA', 'OXALIDA', 'ARALIA', 'TEREBINTHA', 'MELIA'],
            ['SAXIFRAGA', 'LINA', 'CAPRIFOLIA', 'CARYOPHYLLA', 'LEGUMINOSAE', 'CAMELLIA', 'CACTACEA'],
            ['JASMINEA', 'LYTHRA', 'ACANTHA', 'CRASSULA', 'RUBIA', 'HYPERICA', 'LORANTHA'],
            ['AURANTIA', 'RHIZOPHORA', 'BORAGINA', 'TAMARICA', 'MELASTOMA', 'LECYTHIDA', 'VALERIANA'],
            ['COMBRETA', 'APOCYNA', 'DIPSA', 'STYLIDIA', 'RUTA', 'SOLANA', 'PLUMBAGINA'],
            ['LAMIA', 'BEGONIA', 'GROSSULARIA', 'GENTIANA', 'ERICA', 'CAMPANULA', 'POMA'],
            ['BIGNONIA', 'AMARANTA', 'VACCINIA', 'ONAGRA', 'PRIMULA', 'SAPOTA', 'LOBELIA'],
            ['MYRSINA', 'PORTULA', 'PLANTAGINA', 'ELAEAGNA', 'OLEA', 'POLEMONIA', 'ORCHIDA'],
            ['EUPHORBIA', 'SCROPHULARIA', 'CONVOLVULA', 'MUSA', 'UTRICULARIA', 'UMBELLA', 'PROTEA'],
            ['GOODENIA', 'THYMELA', 'URTICA', 'OROBANCHA', 'HYDROPHYLLA', 'AMARYLLIDA', 'CONIFERA'],
            ['PHYTOLACCA', 'PAEONIA', 'IRIDA', 'DIOSCORA', 'GESNERIA', 'SANTALA', 'HYDROCHARIDA'],
            ['ZINGIBERA', 'ALISMA', 'POLYGONA', 'NYCTAGINA', 'BROMELIA', 'SMILA', 'EBENA'],
            ['ROSA', 'LILIA', 'JUNCA', 'VERBENA', 'HAEMODORA', 'COMMELINA', 'COLCHICA']
        ]
        
        potato_color_categories = [ 
            ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST', 'BLACK', 'MIDNIGHT', 'AZUL', 'SKY', 'RED-P', 'ORANGE-P',
             'LIGHTRED-P', 'PASTELBOW', 'DEEPWINKLE', 'SUNLIGHT', 'MIDNIGHTGREEN', 'WINKLE'],
            ['CREAM', 'PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'SIENNA', 'ROSE-P', 'CHERRY', 'CORNFLOWER', 'THISTLE-P',
             'LIGHTORANGE-P', 'LEMON', 'OLIVE', 'RAINBOW-P', 'MIDNIGHTBLUE', 'CORALS', 'MIDNIGHTCYAN', 'UNICORN'],
            ['LIGHTBROWN', 'LILAC', 'BROWN', 'GOLDEN-BROWN', 'DARKBROWN', 'CHOCOLATE', 'HEATHER', 'LAVENDER', 'FADEDSKY',
             'DEEPTHISTLE', 'PALEYELLOW', 'GOLD-P', 'RUSTY', 'PLINK', 'DEEPSEA', 'PALEWINKLE', 'BRIGHTERNIGHT', 'PALEROSES'],
            ['BROWNGOLD', 'DARKHEATHER', 'FLARE', 'SEAFOAM', 'ORCHID-P', 'VIOLET', 'FADEDGREEN', 'OAK', 'PALEGREEN', 'PERIWINKLE',
             'CRIMSON', 'BURNTORANGE', 'GARNET', 'BRIGHTERTHYST', 'SWAMP', 'MIDNIGHTPURPLE', 'PURPLEISH', 'CLOUDRIVER'],
            ['RUBY', 'TINTEDROSE', 'DARKLEAF', 'RUST', 'GREENMINT', 'PITCHNIGHT', 'ROSENIGHT', 'BLACKWHITE', 'GOLDSUN',
             'DEEPFLARE', 'PINK-P', 'PALEPURPLE', 'BLOSSOMS', 'BLOOMS', 'MOSSES', 'MIDNIGHTRED', 'EVERGREEN', 'MYTHICAL'],
            ['LEAF', 'COOLGREEN', 'PITCHLEAF', 'MINT', 'WARMWHITE', 'DARKMINT-P', 'NAVY', 'DARKPURPLE', 'BRIGHTPURPLE', 'BLUE-P',
             'FADEDBLUE', 'SKYBLUE', 'LOLIPOP', 'BUBBLEGUM-P', 'MEADOWS', 'MIDNIGHTPINK', 'OCEAN-P', 'SUNCLOUD'],
            ['FADEDMAGENTA', 'ROSETINT', 'DEEPROSE', 'HOTPINK', 'SILVERROSE', 'FADEDROSE', 'PLATINUM', 'METAL', 'METALIC', 'STONE',
             'STORM', 'PITCHBLACK', 'GREEN-P', 'MAGENTA-P', 'DARKYELLOW', 'MIDNIGHTYELLOW', 'DEEPCARAMEL', 'SUNRISES']
        ]
        
        potato_color_types = ["singlecolours",
            "tabbycolours",
            "marbledcolours",
            "rosettecolours",
            "smokecolours",
            "tickedcolours",
            "speckledcolours",
            "bengalcolours",
            "mackerelcolours",
            "classiccolours",
            "sokokecolours",
            "agouticolours",
            "singlestripecolours",
            "maskedcolours",
            "meteorcolours"]

        color_types = [
            "manedcolours", "ocelotcolours",
            "lynxcolours", "royalcolours", "abyssiniancolours", "cloudedcolours", "stainvoithex",
            "dobermancolours", "ghosttabbycolours", "merlecolours", "monarchcolours",
            "oceloidcolours", "pinstripetabbycolours", "snowflakecolours", "bobcatcolours",
            "cheetahcolours", "brindlecolours", "wildcatcolours",
            "wolfcolours", "spotscolours", "smokepointcolours",
            "dalmatiancolours", "finleappatchescolours", "finleappatchescolours",
            "caliisokokecolours", "dotcolours",
            "caliispeckledcolours", "kintsugicolours", "dotfadecolours", "circletabbycolours", "colourpointcolours", "lynxpointcolours", "ncrestedcaracaracolours",
            "birchtabbycolours",
            "prideagouticolours", "pridebengalcolours", "prideclassiccolours", "pridemackerelcolours"

        ]

        for row, colors in enumerate(color_categories):
            for col, color in enumerate(colors):
                for color_type in color_types:
                    self.make_group(color_type, (col, row), f"{color_type[:-7]}{color}")
                    
        for row, colors in enumerate(potato_color_categories):
            for col, color in enumerate(colors):
                for color_type in potato_color_types:
                    self.make_group(color_type, (col, row), f"{color_type[:-7]}{color}")

        minecraft_color_types = ['minecraftagouticolours', 'minecraftbengalcolours', 'minecraftclassiccolours', 'minecraftmackerelcolours', 'minecraftmarbledcolours', 'minecraftrosettecolours',
            'minecraftsinglecolours', 'minecraftsokokecolours', 'minecraftspeckledcolours', 'minecrafttabbycolours', 'minecrafttickedcolours', 'minecraftsmokecolours', 'minecraftsinglestripecolours']
        anju_color_types = ['anjuagouticolours', 'anjubengalcolours', 'anjuclassiccolours', 'anjumackerelcolours', 'anjumarbledcolours', 'anjurosettecolours',
            'anjusinglecolours', 'anjusokokecolours', 'anjuspeckledcolours', 'anjutabbycolours', 'anjutickedcolours', 'anjusmokecolours']

        heta_color_types = ['hetaagouticolours', 'hetabengalcolours', 'hetaclassiccolours', 'hetamackerelcolours', 'hetamarbledcolours', 'hetarosettecolours',
            'hetasinglecolours', 'hetasinglestripecolours', 'hetasmokecolours', 'hetasokokecolours', 'hetaspeckledcolours', 'hetatabbycolours', 'hetatickedcolours']
        cs_color_types = ['cs_agouticolours', 'cs_bengalcolours', 'cs_classiccolours', 'cs_mackerelcolours', 'cs_marbledcolours', 'cs_maskedcolours', 'cs_rosettecolours',
            'cs_singlecolours', 'cs_singlestripecolours', 'cs_smokecolours', 'cs_sokokecolours', 'cs_speckledcolours', 'cs_tabbycolours', 'cs_tickedcolours']
        cs2_color_types = ['cs_agouti2colours', 'cs_bengal2colours', 'cs_classic2colours', 'cs_mackerel2colours', 'cs_marbled2colours', 'cs_masked2colours', 'cs_rosette2colours',
            'cs_single2colours', 'cs_singlestripe2colours', 'cs_smoke2colours', 'cs_sokoke2colours', 'cs_speckled2colours', 'cs_tabby2colours', 'cs_ticked2colours']
        dance_color_types = ['danceagouticolours', 'dancebengalcolours', 'danceclassiccolours', 'dancemackerelcolours', 'dancemarbledcolours', 'dancemaskedcolours', 'dancerosettecolours',
         'dancesinglecolours', 'dancesmokecolours', 'dancesokokecolours', 'dancespeckledcolours', 'dancesinglestripecolours', 'dancetabbycolours', 'dancetickedcolours']
        mimi_color_types = ['mimiagouticolours', 'mimibengalcolours', 'mimiclassiccolours', 'mimimackerelcolours', 'mimimarbledcolours', 'mimimaskedcolours', 'mimirosettecolours',
         'mimisinglecolours', 'mimismokecolours', 'mimisokokecolours', 'mimispeckledcolours', 'mimisinglestripecolours', 'mimitabbycolours', 'mimitickedcolours']
        silly_color_types = ['sillyagouticolours', 'sillybengalcolours', 'sillyclassiccolours', 'sillymackerelcolours', 'sillymarbledcolours', 'sillymaskedcolours', 'sillyrosettecolours',
         'sillysinglecolours', 'sillysmokecolours', 'sillysokokecolours', 'sillyspeckledcolours', 'sillysinglestripecolours', 'sillytabbycolours', 'sillytickedcolours']
        ster_color_types = ['steragouticolours', 'sterbengalcolours', 'sterclassiccolours', 'stermackerelcolours', 'stermarbledcolours', 'stermaskedcolours', 'sterrosettecolours',
         'stersinglecolours', 'stersmokecolours', 'stersokokecolours', 'sterspeckledcolours', 'stersinglestripecolours', 'stertabbycolours', 'stertickedcolours']
        hive_color_types = ['hiveagouticolours', 'hivebengalcolours', 'hiveclassiccolours', 'hivemackerelcolours', 'hivemarbledcolours', 'hivemaskedcolours', 'hiverosettecolours',
            'hivesinglecolours', 'hivesinglestripecolours', 'hivesmokecolours', 'hivesokokecolours', 'hivespeckledcolours', 'hivetabbycolours', 'hivetickedcolours']
        kris_color_types = ['krisagouticolours', 'krisbengalcolours', 'krisclassiccolours', 'krismackerelcolours', 'krismarbledcolours', 'krismaskedcolours', 'krisrosettecolours',
            'krissinglecolours', 'krissinglestripecolours', 'krissmokecolours', 'krissokokecolours', 'krisspeckledcolours', 'kristabbycolours', 'kristickedcolours']
        meteor_color_types = ['meteoragouticolours', 'meteorbengalcolours', 'meteorclassiccolours', 'meteormackerelcolours', 'meteormarbledcolours', 'meteormaskedcolours', 'meteorrosettecolours',
            'meteorsinglecolours', 'meteorsinglestripecolours', 'meteorsmokecolours', 'meteorsokokecolours', 'meteorspeckledcolours', 'meteortabbycolours', 'meteortickedcolours']
        pastel_color_types = ['pastelagouticolours', 'pastelbengalcolours', 'pastelclassiccolours', 'pastelmackerelcolours', 'pastelmarbledcolours', 'pastelrosettecolours',
            'pastelsinglecolours', 'pastelsinglestripecolours', 'pastelsmokecolours', 'pastelsokokecolours', 'pastelspeckledcolours', 'pasteltabbycolours', 'pasteltickedcolours']
        pepper_color_types = ['pepperagouticolours', 'pepperbengalcolours', 'pepperclassiccolours', 'peppermackerelcolours', 'peppermarbledcolours', 'pepperrosettecolours',
            'peppersinglecolours', 'peppersinglestripecolours', 'peppersmokecolours', 'peppersokokecolours', 'pepperspeckledcolours', 'peppertabbycolours', 'peppertickedcolours']
        sparkle_color_types = ['sparkleagouticolours', 'sparklebengalcolours', 'sparkleclassiccolours', 'sparklemackerelcolours', 'sparklemarbledcolours', 'sparklemaskedcolours', 'sparklerosettecolours',
            'sparklesinglecolours', 'sparklesinglestripecolours', 'sparklesmokecolours', 'sparklesokokecolours', 'sparklespeckledcolours', 'sparkletabbycolours', 'sparkletickedcolours']
        cs3_color_types = ['cs3_agouticolours', 'cs3_bengalcolours', 'cs3_classiccolours', 'cs3_mackerelcolours', 'cs3_marbledcolours', 'cs3_maskedcolours', 'cs3_rosettecolours',
            'cs3_singlecolours', 'cs3_singlestripecolours', 'cs3_smokecolours', 'cs3_sokokecolours', 'cs3_speckledcolours', 'cs3_tabbycolours', 'cs3_tickedcolours']

        for row, colors in enumerate(minecraft_color_categories):
            for col, color in enumerate(colors):
                for color_type in minecraft_color_types:
                    category = color_type[9:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(anju_color_categories):
            for col, color in enumerate(colors):
                for color_type in anju_color_types:
                    category = color_type[4:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(cs_color_categories):
            for col, color in enumerate(colors):
                for color_type in cs_color_types:
                    category = color_type[3:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(cs2_color_categories):
            for col, color in enumerate(colors):
                for color_type in cs2_color_types:
                    category = color_type[3:]
                    category = category.replace('2', '')
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(heta_color_categories):
            for col, color in enumerate(colors):
                for color_type in heta_color_types:
                    category = color_type[4:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(dance_color_categories):
            for col, color in enumerate(colors):
                for color_type in dance_color_types:
                    category = color_type[5:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(mimi_color_categories):
            for col, color in enumerate(colors):
                for color_type in mimi_color_types:
                    category = color_type[4:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(silly_color_categories):
            for col, color in enumerate(colors):
                for color_type in silly_color_types:
                    category = color_type[5:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(ster_color_categories):
            for col, color in enumerate(colors):
                for color_type in ster_color_types:
                    category = color_type[4:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(hive_color_categories):
            for col, color in enumerate(colors):
                for color_type in hive_color_types:
                    category = color_type[4:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')
        for row, colors in enumerate(kris_color_categories):
            for col, color in enumerate(colors):
                for color_type in kris_color_types:
                    category = color_type[4:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')
        for row, colors in enumerate(meteor_color_categories):
            for col, color in enumerate(colors):
                for color_type in meteor_color_types:
                    category = color_type[6:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')
        for row, colors in enumerate(pastel_color_categories):
            for col, color in enumerate(colors):
                for color_type in pastel_color_types:
                    category = color_type[6:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')
        for row, colors in enumerate(pepper_color_categories):
            for col, color in enumerate(colors):
                for color_type in pepper_color_types:
                    category = color_type[6:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')
        for row, colors in enumerate(sparkle_color_categories):
            for col, color in enumerate(colors):
                for color_type in sparkle_color_types:
                    category = color_type[7:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        for row, colors in enumerate(cs3_color_categories):
            for col, color in enumerate(colors):
                for color_type in cs3_color_types:
                    category = color_type[4:]
                    self.make_group(color_type, (col, row), f'{category[:-7]}{color}')

        # tortiepatchesmasks
        tortiepatchesmasks = [
            [
                "ONE",
                "TWO",
                "THREE",
                "FOUR",
                "REDTAIL",
                "DELILAH",
                "HALF",
                "STREAK",
                "MASK",
                "SMOKE",
            ],
            [
                "MINIMALONE",
                "MINIMALTWO",
                "MINIMALTHREE",
                "MINIMALFOUR",
                "OREO",
                "SWOOP",
                "CHIMERA",
                "CHEST",
                "ARMTAIL",
                "GRUMPYFACE",
            ],
            [
                "MOTTLED",
                "SIDEMASK",
                "EYEDOT",
                "BANDANA",
                "PACMAN",
                "STREAMSTRIKE",
                "SMUDGED",
                "DAUB",
                "EMBER",
                "BRIE",
            ],
            [
                "ORIOLE",
                "ROBIN",
                "BRINDLE",
                "PAIGE",
                "ROSETAIL",
                "SAFI",
                "DAPPLENIGHT",
                "BLANKET",
                "BELOVED",
                "BODY",
            ],
            ["SHILOH", "FRECKLED", "HEARTBEAT"],
        ]

        # Define mink's tortie patches
        minks_tortie_patches = [
            ['MINKFULLWHITE', 'MINKANY', 'MINKTUXEDO', 'MINKLITTLE', 'MINKCOLOURPOINT', 'MINKVAN', 'MINKANYTWO',
             'MINKMOON', 'MINKPHANTOM', 'MINKPOWDER',
             'MINKBLEACHED', 'MINKSAVANNAH', 'MINKFADESPOTS', 'MINKPEBBLESHINE'],
            ['MINKEXTRA', 'MINKONEEAR', 'MINKBROKEN', 'MINKLIGHTTUXEDO', 'MINKBUZZARDFANG', 'MINKRAGDOLL',
             'MINKLIGHTSONG', 'MINKVITILIGO', 'MINKBLACKSTAR',
             'MINKPIEBALD', 'MINKCURVED', 'MINKPETAL', 'MINKSHIBAINU', 'MINKOWL'],
            ['MINKTIP', 'MINKFANCY', 'MINKFRECKLES', 'MINKRINGTAIL', 'MINKHALFFACE', 'MINKPANTSTWO', 'MINKGOATEE',
             'MINKVITILIGOTWO', 'MINKPAWS', 'MINKMITAINE',
             'MINKBROKENBLAZE', 'MINKSCOURGE', 'MINKDIVA', 'MINKBEARD'],
            ['MINKTAIL', 'MINKBLAZE', 'MINKPRINCE', 'MINKBIB', 'MINKVEE', 'MINKUNDERS', 'MINKHONEY', 'MINKFAROFA',
             'MINKDAMIEN', 'MINKMISTER', 'MINKBELLY',
             'MINKTAILTIP', 'MINKTOES', 'MINKTOPCOVER'],
            ['MINKAPRON', 'MINKCAPSADDLE', 'MINKMASKMANTLE', 'MINKSQUEAKS', 'MINKSTAR', 'MINKTOESTAIL', 'MINKRAVENPAW',
             'MINKPANTS', 'MINKREVERSEPANTS',
             'MINKSKUNK', 'MINKKARPATI', 'MINKHALFWHITE', 'MINKAPPALOOSA', 'MINKDAPPLEPAW'],
            ['MINKHEART', 'MINKLILTWO', 'MINKGLASS', 'MINKMOORISH', 'MINKSEPIAPOINT', 'MINKMINKPOINT', 'MINKSEALPOINT',
             'MINKMAO', 'MINKLUNA', 'MINKCHESTSPECK',
             'MINKWINGS', 'MINKPAINTED', 'MINKHEARTTWO', 'MINKWOODPECKER'],
            ['MINKBOOTS', 'MINKMISS', 'MINKCOW', 'MINKCOWTWO', 'MINKBUB', 'MINKBOWTIE', 'MINKMUSTACHE',
             'MINKREVERSEHEART', 'MINKSPARROW', 'MINKVEST',
             'MINKLOVEBUG', 'MINKTRIXIE', 'MINKSAMMY', 'MINKSPARKLE'],
            ['MINKRIGHTEAR', 'MINKLEFTEAR', 'MINKESTRELLA', 'MINKSHOOTINGSTAR', 'MINKEYESPOT', 'MINKREVERSEEYE',
             'MINKFADEBELLY', 'MINKFRONT',
             'MINKBLOSSOMSTEP', 'MINKPEBBLE', 'MINKTAILTWO', 'MINKBUDDY', 'MINKBACKSPOT', 'MINKEYEBAGS'],
            ['MINKBULLSEYE', 'MINKFINN', 'MINKDIGIT', 'MINKKROPKA', 'MINKFCTWO', 'MINKFCONE', 'MINKMIA', 'MINKSCAR',
             'MINKBUSTER', 'MINKSMOKEY', 'MINKHAWKBLAZE',
             'MINKCAKE', 'MINKROSINA', 'MINKPRINCESS'],
            ['MINKLOCKET', 'MINKBLAZEMASK', 'MINKTEARS', 'MINKDOUGIE']
        ]

        # toritemaskthree
        torite_mask_two2 = [
            ['INK', 'WOLF', 'EYEV', 'GEM', 'FOX', 'ORCA', 'PINTO', 'FRECKLESTWO', 'SOLDIER',
             'AKITA'],
            ['CHESSBORAD', 'ANT', 'CREAMV', 'BUNNY', 'MOJO', 'STAINSONE', 'STAINST',
              'HALFHEART', 'FRECKLESTHREE', 'KITTY'],
            ['SUNRISE', 'HUSKY', 'STATNTHREE', 'ERAMASK', 'S', 'PAW', 'SWIFTPAW', 'BOOMSTAR', 'MIST', 'LEON'],
            ['LADY', 'LEGS', 'MEADOW', 'SALT', 'BAMBI', 'PRIMITVE', 'SKUNKSTRIPE', 'NEPTUNE', 'KARAPATITWO', 'CHAOS'],
            ['MOSCOW', 'ERAHALF', 'CAPETOWN', 'SUN', 'BANAN', 'PANDA', 'DOVE', 'PINTOTWO', 'SNOWSHOE', 'SKY'],
            ['MOONSTONE', 'DRIP', 'CRESCENT', 'ETERNAL', 'WINGTWO', 'STARBORN', 'SPIDERLEGS', 'APPEL', 'RUG', 'LUCKY'],
            ['SOCKS', 'BRAMBLEBERRY', 'LATKA', 'ASTRONAUT', 'STORK']
          ]

        for row, masks in enumerate(tortiepatchesmasks):
            for col, mask in enumerate(masks):
                self.make_group('tortiepatchesmasks', (col, row), f"tortiemask{mask}")
        for row, minkmasks in enumerate(minks_tortie_patches):
            for col, minkmask in enumerate(minkmasks):
                self.make_group('minkstorties', (col, row), f"tortiemask{minkmask}")
        for row, masks in enumerate(tortiepatchesmasks):
            for col, mask in enumerate(masks):
                self.make_group("tortiepatchesmasks", (col, row), f"tortiemask{mask}")
        for row, maskstwo in enumerate(torite_mask_two):
            for col, masktwo in enumerate(maskstwo):
                self.make_group('eragonatorite', (col, row), f"tortiemask{masktwo}")
        for row, masksthree in enumerate(torite_mask_two2):
            for col, maskthree in enumerate(masksthree):
                self.make_group('eragonatorite2', (col, row), f"tortiemask{maskthree}")
                
        self.make_group('heterochromiamask', (0,0), f"heterochromiamask")

        # Define skin colors
        skin_colors = [
            ["BLACK", "RED", "PINK", "DARKBROWN", "BROWN", "LIGHTBROWN"],
            ["DARK", "DARKGREY", "GREY", "DARKSALMON", "SALMON", "PEACH"],
            ["DARKMARBLED", "MARBLED", "LIGHTMARBLED", "DARKBLUE", "BLUE", "LIGHTBLUE"],
        ]
        
        skin_colors_magic = [
            ['FLAMES', 'BUBBLES', 'FLOWERS', 'LIGHT1', 'SPARKLES', 'INK'],
            ['MIST', 'MAGMA', 'SMOKE', 'PURPLEFLAMES', 'INK2', 'THUNDERSTORM'],
            ['LIGHT2', 'DEATHBERRIES', 'SKELETON', 'FLESH', 'POWERLESS1', 'POWERLESS2']
        ]
        
        skin_colors_elemental = [
            ['FLAMES2', 'BUBBLES2', 'VINES', 'WIND', 'LIGHTNING', 'BLUEFLAMES'],
            ['FROZEN', 'STONE', 'TREE', 'PURPLESPARKS', 'PURPLEGLOW', 'SHADOW'],
            ['YELLOWGLOW', 'FAEMANE', 'GREENGLOW', 'SHADOWBEAST', 'SPARKLES2', 'ROOTS']
        ]
        
        skin_colors_bingle = [
            ['GREENCHIMERA', 'CORALCHIMERA', 'FROSTGLOW', 'THIRDEYE', 'CRYSTALS', 'FOXTAIL'],
            ['BATWINGS', 'CLOUDS', 'TRANSCLOUDS', 'SPOOKYCRYSTALS', 'MAGEGIFT', 'DEVILWINGS'],
            ['SPARROWGIFT', 'DOVEWINGS', 'ANTLERS', 'BLUECORALCHIMERA', 'ICECRYSTALS', 'BLACKFOX']
        ]
        
        skin_colors_bingle2 = [
            ['SHADOWSELF', 'FIRETAIL', 'BLUEFIRETAIL', 'SCORPION', 'SNOWFOX', 'KITSUNE'],
            ['FENNECKITSUNE', '006', '007', '008', '009', '010'],
            ['011', '012', '013', '014', '015', '016']
        ]

        skin_colors_math = [
            ['LIGHTPURPLE', 'BLUE2', 'DARKPURPLE', 'DARKBLUE', 'NEONGREEN', 'BLUESPECKLED'],
            ['BRIGHTPINK', 'BRIGHTORANGE', 'MAGENTA', 'PINKBLUE', 'PURPLEYELLOW', 'BLUEORANGE'],
            ['WHITE', 'BLACK2', 'AQUA', 'DARKGREEN', 'BRIGHTYELLOW', 'NULL1']
        ]

        skin_colors_turtle = [
            ['BLACKTURTLE', 'REDTURTLE', 'PINKTURTLE', 'DARKBROWNTURTLE', 'BROWNTURTLE', 'LIGHTBROWNTURTLE'],
            ['DARKTURTLE', 'DARKGREYTURTLE', 'GREYTURTLE', 'DARKSALMONTURTLE', 'SALMONTURTLE', 'PEACHTURTLE'],
            ['DARKMARBLEDTURTLE', 'MARBLEDTURTLE', 'LIGHTMARBLEDTURTLE', 'DARKBLUETURTLE', 'BLUETURTLE', 'LIGHTBLUETURTLE']]

        skin_colors_stain = [
            ['STAINDUST', 'STAINICEBLUE', 'STAININDIGO', 'STAINBLUE', 'STAINPURPLE', 'STAINDARKBLUE'],
            ['STAINLIGHTPINK', 'STAINYELLOW', 'STAINPINK', 'STAINGOLD', 'STAINHOTPINK', 'STRAINDIRT'],
            ['STAINCYAN', 'STAINLIME', 'STAINTURQUOISE', 'STAINGREEN', 'STAINBLUEGREEN', 'STAINPEACOCK']]

        for row, colors in enumerate(skin_colors):
            for col, color in enumerate(colors):
                self.make_group("skin", (col, row), f"skin{color}")
        
        for row, colors in enumerate(skin_colors_magic):
            for col, color in enumerate(colors):
                self.make_group('skin_magic', (col, row), f"skin{color}")
        
        for row, colors in enumerate(skin_colors_elemental):
            for col, color in enumerate(colors):
                self.make_group('skin_elemental', (col, row), f"skin{color}")
        
        for row, colors in enumerate(skin_colors_bingle):
            for col, color in enumerate(colors):
                self.make_group('skin_bingle', (col, row), f"skin{color}")

        for row, colors in enumerate(skin_colors_bingle2):
            for col, color in enumerate(colors):
                self.make_group('skin_bingle2', (col, row), f"skin{color}")

        for row, colors in enumerate(skin_colors_math):
            for col, color in enumerate(colors):
                self.make_group('skin_mathkangaroo', (col, row), f"skin{color}")

        for row, colors in enumerate(skin_colors_turtle):
            for col, color in enumerate(colors):
                self.make_group('skin_turtle', (col, row), f"skin{color}")

        for row, colors in enumerate(skin_colors_stain):
            for col, color in enumerate(colors):
                self.make_group('skin_stain', (col, row), f"skin{color}")

        self.load_scars()
        self.load_symbols()

    def load_scars(self):
        """
        Loads scar sprites and puts them into groups.
        """

        # Define scars
        scars_data = [
            [
                "ONE",
                "TWO",
                "THREE",
                "MANLEG",
                "BRIGHTHEART",
                "MANTAIL",
                "BRIDGE",
                "RIGHTBLIND",
                "LEFTBLIND",
                "BOTHBLIND",
                "BURNPAWS",
                "BURNTAIL",
            ],
            [
                "BURNBELLY",
                "BEAKCHEEK",
                "BEAKLOWER",
                "BURNRUMP",
                "CATBITE",
                "RATBITE",
                "FROSTFACE",
                "FROSTTAIL",
                "FROSTMITT",
                "FROSTSOCK",
                "QUILLCHUNK",
                "QUILLSCRATCH",
            ],
            [
                "TAILSCAR",
                "SNOUT",
                "CHEEK",
                "SIDE",
                "THROAT",
                "TAILBASE",
                "BELLY",
                "TOETRAP",
                "SNAKE",
                "LEGBITE",
                "NECKBITE",
                "FACE",
            ],
            [
                "HINDLEG",
                "BACK",
                "QUILLSIDE",
                "SCRATCHSIDE",
                "TOE",
                "BEAKSIDE",
                "CATBITETWO",
                "SNAKETWO",
                "FOUR",
            ],
        ]

        # define missing parts
        missing_parts_data = [
            [
                "LEFTEAR",
                "RIGHTEAR",
                "NOTAIL",
                "NOLEFTEAR",
                "NORIGHTEAR",
                "NOEAR",
                "HALFTAIL",
                "NOPAW",
            ]
        ]

        # scars
        for row, scars in enumerate(scars_data):
            for col, scar in enumerate(scars):
                self.make_group("scars", (col, row), f"scars{scar}")

        # missing parts
        for row, missing_parts in enumerate(missing_parts_data):
            for col, missing_part in enumerate(missing_parts):
                self.make_group("missingscars", (col, row), f"scars{missing_part}")

        # accessories
        # to my beloved modders, im very sorry for reordering everything <333 -clay
        medcatherbs_data = [
            [
                "MAPLE LEAF",
                "HOLLY",
                "BLUE BERRIES",
                "FORGET ME NOTS",
                "RYE STALK",
                "CATTAIL",
                "POPPY",
                "ORANGE POPPY",
                "CYAN POPPY",
                "WHITE POPPY",
                "PINK POPPY",
            ],
            [
                "BLUEBELLS",
                "LILY OF THE VALLEY",
                "SNAPDRAGON",
                "HERBS",
                "PETALS",
                "NETTLE",
                "HEATHER",
                "GORSE",
                "JUNIPER",
                "RASPBERRY",
                "LAVENDER",
            ],
            [
                "OAK LEAVES",
                "CATMINT",
                "MAPLE SEED",
                "LAUREL",
                "BULB WHITE",
                "BULB YELLOW",
                "BULB ORANGE",
                "BULB PINK",
                "BULB BLUE",
                "CLOVER",
                "DAISY",
            ],
            [
                "WISTERIA",
                "ROSE MALLOW",
                "PICKLEWEED",
                "GOLDEN CREEPING JENNY",
                "DESERT WILLOW",
                "CACTUS FLOWER",
                "PRAIRIE FIRE",
                "VERBENA EAR",
                "VERBENA PELT",
            ],
        ]
        dryherbs_data = [["DRY HERBS", "DRY CATMINT", "DRY NETTLES", "DRY LAURELS"]]
        wild_data = [
            [
                "RED FEATHERS",
                "BLUE FEATHERS",
                "JAY FEATHERS",
                "GULL FEATHERS",
                "SPARROW FEATHERS",
                "MOTH WINGS",
                "ROSY MOTH WINGS",
                "MORPHO BUTTERFLY",
                "MONARCH BUTTERFLY",
                "CICADA WINGS",
                "BLACK CICADA",
            ],
            [
                "ROAD RUNNER FEATHER",
            ],
        ]

        ster_data = [
            ["POPPYFLOWER", "JUNIPERBERRY", "DAISYFLOWER", "BORAGEFLOWER", "OAK", "BEECH"],
            ["LAURELLEAVES", "COLTSFOOT", "BINDWEED", "TORMENTIL", "BRIGHTEYE", "LAVENDERWREATH"],
            ["YARROW"]
        ]

        collars_data = [
            ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"],
            ["GREEN", "RAINBOW", "BLACK", "SPIKES", "WHITE"],
            ["PINK", "PURPLE", "MULTI", "INDIGO"],
        ]

        bellcollars_data = [
            [
                "CRIMSONBELL",
                "BLUEBELL",
                "YELLOWBELL",
                "CYANBELL",
                "REDBELL",
                "LIMEBELL",
            ],
            ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL"],
            ["PINKBELL", "PURPLEBELL", "MULTIBELL", "INDIGOBELL"],
        ]

        bowcollars_data = [
            ["CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW", "LIMEBOW"],
            ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW"],
            ["PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW"],
        ]

        nyloncollars_data = [
            [
                "CRIMSONNYLON",
                "BLUENYLON",
                "YELLOWNYLON",
                "CYANNYLON",
                "REDNYLON",
                "LIMENYLON",
            ],
            ["GREENNYLON", "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON"],
            ["PINKNYLON", "PURPLENYLON", "MULTINYLON", "INDIGONYLON"],
        ]

        plant2_data = [
            ["OGCLOVER", "STICK", "PUMPKIN", "MOSS", "IVY", "ACORN", "MOSS PELT", "REEDS", "BAMBOO"]
        ]
        
        colorsplash_horn_data = [
            ["CSYELLOWHORN", "CSORANGEHORN", "CSGREENHORN", "CSFROSTHORN", "CSSILVERHORN", "CSCYANHORN"],
            ["CSMAROONHORN", "CSVIOLETHORN", "CSINDIGOHORN", "CSBLUEHORN", "CSBLACKHORN"],
            ["CSLIMEHORN", "CSGOLDHORN", "CSMOSSHORN", "CSBROWNHORN"]
        ]
        
        colorsplash_kitsune_data = [
            ["CSYELLOWKITSUNE", "CSORANGEKITSUNE", "CSGREENKITSUNE", "CSFROSTKITSUNE", "CSSILVERKITSUNE", "CSCYANKITSUNE"],
            ["CSMAROONKITSUNE", "CSVIOLETKITSUNE", "CSINDIGOKITSUNE", "CSBLUEKITSUNE", "CSBLACKKITSUNE"],
            ["CSLIMEKITSUNE", "CSGOLDKITSUNE", "CSMOSSKITSUNE", "CSBROWNKITSUNE"]
        ]
        
        colorsplash_mermaid_data = [
            ["CSYELLOWMERMAID", "CSORANGEMERMAID", "CSGREENMERMAID", "CSFROSTMERMAID", "CSSILVERMERMAID", "CSCYANMERMAID"],
            ["CSMAROONMERMAID", "CSVIOLETMERMAID", "CSINDIGOMERMAID", "CSBLUEMERMAID", "CSBLACKMERMAID"],
            ["CSLIMEMERMAID", "CSGOLDMERMAID", "CSMOSSMERMAID", "CSBROWNMERMAID"]
        ]
        
        beetle_accessories_data = [
            ["FROG FRIEND", "MOUSE FRIEND", "BUNNY HAT", "SMILEY HAT", "PARTY HAT", "SANTA HAT"],
            ["STICK FRIEND", "BAT WING SUIT", "PINK BOWTIE", "GRAY BOWTIE", "PINK SCARF"],
            ["BLUETAILED SKINK", "BLACKHEADED ORIOLE", "MILKSNAKE", "WORM FRIEND"]
        ]

        beetle_feathers_data = [
            ["THRUSH FEATHERS", "GOLDFINCH FEATHERS", "DOVE FEATHERS", "PEACOCK FEATHERS", "HAWK FEATHERS", "BLUE JAY FEATHERS"],
            ["ROBIN FEATHERS", "FIERY FEATHERS", "SUNSET FEATHERS", "SILVER FEATHERS"]
            ]
        
        sailormoon_data = [
            ["MOON", "MERCURY", "MARS", "JUPITER", "VENUS", "TUXEDO MASK"],
            ["URANUS", "NEPTUNE", "PLUTO", "SATURN", "MINI MOON", "CRYSTAL BALL"]
        ]

        random_data = [
            ["DOGWOOD", "TREESTAR", "RACCOON LEAF", "WHITE RACCOON LEAF", "CHERRY BLOSSOM", "DAISY BLOOM"],
            ["FEATHERS", "RED ROSE", "WHITE ROSE", "PEBBLE", "PEBBLE COLLECTION", "GOLDEN FLOWER"],
            ["DANDELIONS", "DANDELION PUFFS", "DICE", "GOLDEN EARRINGS"]
        ]

        crafted_data = [
            ["WILLOWBARK BAG", "CLAY DAISY POT", "CLAY AMANITA POT", "CLAY BROWNCAP POT", "OGBIRD SKULL", "LEAF BOW"]
        ]

        flower_data = [
            ["OGDAISY", "DIANTHUS", "BLEEDING HEARTS", "FRANGIPANI", "BLUE GLORY", "CATNIP FLOWER", "BLANKET FLOWER", "ALLIUM", "LACELEAF", "PURPLE GLORY"],
            ["YELLOW PRIMROSE", "HESPERIS", "MARIGOLD", "OGWISTERIA"]
        ]

        snake_data = [
            ["GRASS SNAKE", "BLUE RACER", "WESTERN COACHWHIP", "KINGSNAKE"]
        ]

        deadInsect_data = [
            ["LUNAR MOTH", "ROSY MAPLE MOTH", "OGMONARCH BUTTERFLY", "DAPPLED MONARCH", "POLYPHEMUS MOTH", "MINT MOTH"]
        ]
        
        boos_data = [["CRIMSONBOO", "MAGENTABOO", "PINKBOO", "BLOODORANGEBOO", "ORANGEBOO", "YELLOWBOO"],
                    ["LIMEBOO", "DARKGREENBOO", "GREENBOO", "TEALBOO", "LIGHTBLUEBOO", "BLUEBOO"],
                    ["DARKBLUEBOO", "LIGHTPURPLEBOO", "DARKPURPLEBOO", "VIBRANTPURPLEBOO", "PINKREDBOO", "WHITEBOO"],
                    ["LIGHTGRAYBOO", "GRAYBOO", "BLACKBOO", "BROWNBOO"]]

        aliveInsect_data = [
            ["BROWN SNAIL", "RED SNAIL", "WORM", "BLUE SNAIL", "ZEBRA ISOPOD", "DUCKY ISOPOD", "DAIRY COW ISOPOD", "BEETLEJUICE ISOPOD", "BEE", "RED LADYBUG"],
            ["ORANGE LADYBUG", "YELLOW LADYBUG"]
        ]

        fruit_data = [
            ["OGRASPBERRY", "BLACKBERRY", "GOLDEN RASPBERRY", "CHERRY", "YEW"]
        ]

        smallAnimal_data = [
            ["GRAY SQUIRREL", "RED SQUIRREL", "CRAB", "WHITE RABBIT", "BLACK RABBIT", "BROWN RABBIT", "INDIAN GIANT SQUIRREL", "FAWN RABBIT", "BROWN AND WHITE RABBIT", "BLACK AND WHITE RABBIT"],
            ["WHITE AND FAWN RABBIT", "BLACK VITILIGO RABBIT", "BROWN VITILIGO RABBIT", "FAWN VITILIGO RABBIT", "BLACKBIRD", "ROBIN", "JAY", "THRUSH", "CARDINAL", "MAGPIE"],
            ["CUBAN TROGON", "TAN RABBIT", "TAN AND WHITE RABBIT", "TAN VITILIGO RABBIT", "RAT", "WHITE MOUSE", "BLACK MOUSE", "GRAY MOUSE", "BROWN MOUSE", "GRAY RABBIT"],
            ["GRAY AND WHITE RABBIT", "GRAY VITILIGO RABBIT"]
        ]

        tail2_data = [
            ["SEAWEED", "DAISY CORSAGE"]
        ]
        bones_data = [
            ["SNAKE", "BAT WINGS", "CANIDAE SKULL", "DEER ANTLERS", "RAM HORN", "GOAT HORN", "OX SKULL",
             "RAT SKULL", "TEETH COLLAR", "ROE SKULL"],
            ["BIRD SKULL", "RIBS", "FISH BONES"]
        ]
        
        butterflymoth_data = [
            ["PEACOCK BUTTERFLY", "DEATH HEAD HAWKMOTH", "GARDEN TIGER MOTH", "ATLAS MOTH", "CECOROPIA MOTH", "WHITE ERMINE MOTH",
             "IO MOTH", "COMET MOTH", "JADE HAWKMOTH", "HUMMINGBIRD HAWKMOTH"],
            ["OWL BUTTERFLY", "GLASSWING BUTTERFLY", "QUEEN ALEXANDRA BIRDWING BUTTERFLY", "GREEN DRAGONTAIL BUTTERFLY",
             "MENELAUS BLUE MORPHO BUTTERFLY", "DEAD LEAF BUTTERFLY"]
            
        ]
        
        twolegstuff_data = [
            ["OLD GOLD WATCH", "OLD SILVER WATCH", "GOLDEN KEY", "SILVER KEY", "DVD", "OLD PENCIL", "OLD BRUSH",
             "BANANA PEEL", "BROKEN VHS TAPE", "OLD NEWSPAPER"],
            ["SEA GLASS", "BAUBLES", "MUD AND DIRT"]
        ]
        bandanas_data = [
            ["CRIMSONBANDANA", "BLUEBANDANA", "YELLOWBANDANA", "CYANBANDANA", "REDBANDANA", "LIMEBANDANA"],
            ["GREENBANDANA", "RAINBOWBANDANA", "BLACKBANDANA", "SPIKESBANDANA", "WHITEBANDANA"],
            ["PINKBANDANA", "PURPLEBANDANA", "MULTIBANDANA", "INDIGOBANDANA"]
        ]
        
        harnesses_data = [
            ["CRIMSONH", "BLUEH", "YELLOWH", "CYANH", "REDH", "LIMEH"],
            ["GREENH", "RAINBOWH", "BLACKH", "SPIKESH", "WHITEH"],
            ["PINKH", "PURPLEH", "MULTIH", "INDIGOH"]
        ]
        
        bows_data = [
            ["CRIMSONBOWS", "BLUEBOWS", "YELLOWBOWS", "CYANBOWS", "REDBOWS", "LIMEBOWS"],
            ["GREENBOWS", "RAINBOWBOWS", "BLACKBOWS", "SPIKESBOWS", "WHITEBOWS"],
            ["PINKBOWS", "PURPLEBOWS", "MULTIBOWS", "INDIGOBOWS"]
        ]
       
        dog_teeth_collars_data = [
            ["CRIMSONTEETHCOLLAR", "BLUETEETHCOLLAR", "YELLOWTEETHCOLLAR", "CYANTEETHCOLLAR", "REDTEETHCOLLAR",
             "LIMETEETHCOLLAR"],
            ["GREENTEETHCOLLAR", "RAINBOWTEETHCOLLAR", "BLACKTEETHCOLLAR", "SPIKESTEETHCOLLAR", "WHITETEETHCOLLAR"],
            ["PINKTEETHCOLLAR", "PURPLETEETHCOLLAR", "MULTITEETHCOLLAR", "INDIGOTEETHCOLLAR"]
        ]

        ties_data = [
            ["CRIMSONTIE", "BLUETIE", "YELLOWTIE", "CYANTIE", "ORANGETIE", "LIMETIE"],
            ["GREENTIE", "RAINBOWTIE", "BLACKTIE", "SPIKESTIE", "WHITETIE"],
            ["PINKTIE", "PURPLETIE", "MULTITIE", "INDIGOTIE"]
        ]
     
        french_scarves_data = [
            ["CRIMSONS", "BLUES", "YELLOWS", "CYANS", "ORANGES", "LIMES"],
            ["GREENS", "RAINBOWS", "BLACKS", "SPIKESS", "WHITES"],
            ["PINKS", "PURPLES", "MULTIS", "INDIGOS"]
        ]
        
        
        chime_data = [["SILVER MOON", "GOLD STAR", "GOLD MOON", "MOON AND STARS"]]
        lantern_data = [["LANTERN"]]

        moss_data = [
            ["FAT CONE", "THIN CONE", "PEACH CORSAGE"]
        ]

        neckerchief_data = [["WHITE NECKERCHIEF", "BABYBLUE NECKERCHIEF", "LIGHTPURPLE NECKERCHIEF", "BLUE NECKERCHIEF", "PURPLE NECKERCHIEF", "DARKPURPLE NECKERCHIEF"],
                    ["LIGHTPINK NECKERCHIEF", "LIGHTYELLOW NECKERCHIEF", "PINK NECKERCHIEF", "ORANGE NECKERCHIEF", "RED NECKERCHIEF"],
                    ["CYAN NECKERCHIEF", "YELLOWGREEN NECKERCHIEF", "TURQUOISE NECKERCHIEF", "GREEN NECKERCHIEF"]]

        witchhat_data = [["WHITE WITCHHAT", "BABYBLUE WITCHHAT", "LIGHTPURPLE WITCHHAT", "BLUE WITCHHAT", "PURPLE WITCHHAT", "DARKPURPLE WITCHHAT"],
                    ["LIGHTPINK WITCHHAT", "LIGHTYELLOW WITCHHAT", "PINK WITCHHAT", "ORANGE WITCHHAT", "RED WITCHHAT"],
                    ["CYAN WITCHHAT", "YELLOWGREEN WITCHHAT", "TURQUOISE WITCHHAT", "GREEN WITCHHAT"]]

        pokemon_data = [["PIKACHU", "SQUIRTLE", "CHARMANDER", "SPHEAL", "GROWLITHE", "BULBASAUR"],
                    ["SENTRET", "SHAYMIN", "EMOLGA", "HISUI GROWLITHE", "ALOLAN VULPIX"],
                    ["VULPIX", "LUXRAY", "ALTARIA", "AZUMARILL"]]
        
        pride_bandanas_data = [
            ["LESBIAN BANDANA", "GAYMALE BANDANA", "NONBINARY BANDANA", "BISEXUAL BANDANA", "ASEXUAL BANDANA", "AGENDER BANDANA"],
            ["AROACE BANDANA", "GENDERFLUID BANDANA", "INTERSEX BANDANA", "PRIDE BANDANA", "TRANSGENDER BANDANA", "GENDERQUEER BANDANA"],
            ["AROMANTIC BANDANA", "PANSEXUAL BANDANA", "DEMIGENDER BANDANA", "OMNISEXUAL BANDANA", "GENDERFAE BANDANA", "DEMIGIRL BANDANA"],
            ["DEMIBOY BANDANA", "GENDERFAUN BANDANA", "GENDERFLOR BANDANA", "POLYAMOROUS BANDANA"]
        ]
        
        superartsi_data = [
            ["ORANGE BUTTERFLY", "CYAN BUTTERFLY", "BROWN HIDE", "GRAY HIDE", "BROWN HIDE AND HERBS", "GRAY HIDE AND HERBS"],
            ["HERB TAILWRAP", "MOSS AND TAILWRAP", "BLEEDING HEARTS VINES", "BLEEDING HEARTS VINES2", "LILLIES"]
        ]
        
        wild_accessories2_data = [
            ["LILYPADS",  "DEATHBERRY VINE", "DEATHBERRIES", "ACORN2", "PINECONE", "VINES"],
            ["CHERRIES", "BLEEDING HEARTS2", "SEASHELLS", "FERNS", "DRIED FERNS"],
            ["WHEAT", "BLACK WHEAT"]
        ]
        
        storms_accessories_data = [
            ["PEARL NECKLACE", "TAIL PEARLS", "DRAPES", "PEARL EARRINGS", "EYEPATCH"],
            ["PEARL BRACELETS", "JEWEL NECKLACE"]

        ]
        
        starcatcher_data = [
                ["FULL BANDAGES", "LEFT BANDAGES", "CLAWS"]
            ]
        
        #starcatcher accessories
        for row, accs in enumerate(starcatcher_data):
            for col, acc in enumerate(accs):
                self.make_group("starcatcher_accs", (col, row), f"acc_starcatcher{acc}")
        
        #pride bandanas
        for row, bandanas in enumerate(pride_bandanas_data):
            for col, bandana in enumerate(bandanas):
                self.make_group("pride_bandanas", (col, row), f"acc_pride{bandana}")
    
        #storms accessories, pirate coat is unfinished so we ignore
        for row, accessories in enumerate(storms_accessories_data):
            for col, accessory in enumerate(accessories):
                self.make_group("stormsacc", (col, row), f"acc_storm{accessory}")
        
        #superartsi's accessories
        for row, accessories in enumerate(superartsi_data):
            for col, accessory in enumerate(accessories):
                self.make_group('artsi_acc', (col, row), f'acc_superartsi{accessory}')

        #wild's accessories
        for row, accessories in enumerate(wild_accessories2_data):
            for col, accessory in enumerate(accessories):
                self.make_group('wildaccs_2', (col, row), f'acc_wild2{accessory}')

        # medcatherbs
        for row, herbs in enumerate(medcatherbs_data):
            for col, herb in enumerate(herbs):
                self.make_group("medcatherbs", (col, row), f"acc_herbs{herb}")
        # dryherbs
        for row, dry in enumerate(dryherbs_data):
            for col, dryherbs in enumerate(dry):
                self.make_group("medcatherbs", (col, 4), f"acc_herbs{dryherbs}")
        # wild
        for row, wilds in enumerate(wild_data):
            for col, wild in enumerate(wilds):
                self.make_group("wild", (col, row), f"acc_wild{wild}")

        # collars
        for row, collars in enumerate(collars_data):
            for col, collar in enumerate(collars):
                self.make_group("collars", (col, row), f"collars{collar}")

        # bellcollars
        for row, bellcollars in enumerate(bellcollars_data):
            for col, bellcollar in enumerate(bellcollars):
                self.make_group("bellcollars", (col, row), f"collars{bellcollar}")

        # bowcollars
        for row, bowcollars in enumerate(bowcollars_data):
            for col, bowcollar in enumerate(bowcollars):
                self.make_group("bowcollars", (col, row), f"collars{bowcollar}")

        # nyloncollars
        for row, nyloncollars in enumerate(nyloncollars_data):
            for col, nyloncollar in enumerate(nyloncollars):
                self.make_group("nyloncollars", (col, row), f"collars{nyloncollar}")

        # ohdan's accessories :3
        for row, plant2_accessories in enumerate(plant2_data):
            for col, plant2_accessory in enumerate(plant2_accessories):
                self.make_group('plant2_accessories', (col, row), f'acc_plant2{plant2_accessory}')

        for row, crafted_accessories in enumerate(crafted_data):
            for col, crafted_accessory in enumerate(crafted_accessories):
                self.make_group('crafted_accessories', (col, row), f'acc_crafted{crafted_accessory}')

        for row, flower_accessories in enumerate(flower_data):
            for col, flower_accessory in enumerate(flower_accessories):
                self.make_group('flower_accessories', (col, row), f'acc_flower{flower_accessory}')

        for row, snake_accessories in enumerate(snake_data):
            for col, snake_accessory in enumerate(snake_accessories):
                self.make_group('snake_accessories', (col, row), f'acc_snake{snake_accessory}')

        for row, deadInsect_accessories in enumerate(deadInsect_data):
            for col, deadInsect_accessory in enumerate(deadInsect_accessories):
                self.make_group('deadInsect_accessories', (col, row), f'acc_deadInsect{deadInsect_accessory}')

        for row, aliveInsect_accessories in enumerate(aliveInsect_data):
            for col, aliveInsect_accessory in enumerate(aliveInsect_accessories):
                self.make_group('aliveInsect_accessories', (col, row), f'acc_aliveInsect{aliveInsect_accessory}')

        for row, fruit_accessories in enumerate(fruit_data):
            for col, fruit_accessory in enumerate(fruit_accessories):
                self.make_group('fruit_accessories', (col, row), f'acc_fruit{fruit_accessory}')

        for row, smallAnimal_accessories in enumerate(smallAnimal_data):
            for col, smallAnimal_accessory in enumerate(smallAnimal_accessories):
                self.make_group('smallAnimal_accessories', (col, row), f'acc_smallAnimal{smallAnimal_accessory}')

        for row, tail2_accessories in enumerate(tail2_data):
            for col, tail2_accessory in enumerate(tail2_accessories):
                self.make_group('tail2_accessories', (col, row), f'acc_tail2{tail2_accessory}')

        # bones
        for row, bones in enumerate(bones_data):
            for col, bone in enumerate(bones):
                self.make_group('bonesacc', (col, row), f'acc_bones{bone}')

        # butterflies and moths
        for row, butterflymoth in enumerate(butterflymoth_data):
            for col, butterflies in enumerate(butterflymoth):
                self.make_group('butterflymothacc', (col, row), f'acc_butterflymoth{butterflies}')
        # twoleg stuff
        for row, twolegstuff in enumerate(twolegstuff_data):
            for col, stuff in enumerate(twolegstuff):
                self.make_group('twolegstuff', (col, row), f'acc_twolegstuff{stuff}')
        # bandanas
        for row, bandanas in enumerate(bandanas_data):
            for col, bandana in enumerate(bandanas):
                self.make_group('bandanas', (col, row), f'collars{bandana}')

        # colorsplash horn
        for row, horncollars in enumerate(colorsplash_horn_data):
            for col, horncollar in enumerate(horncollars):
                self.make_group('colorsplash_horn', (col, row), f'acc_colorsplash{horncollar}')

        # colorsplash kitsune
        for row, kitsunecollars in enumerate(colorsplash_kitsune_data):
            for col, kitsunecollar in enumerate(kitsunecollars):
                self.make_group('colorsplash_kitsune', (col, row), f'acc_colorsplash{kitsunecollar}')

        # colorsplash mermaid
        for row, mermaidcollars in enumerate(colorsplash_mermaid_data):
            for col, mermaidcollar in enumerate(mermaidcollars):
                self.make_group('colorsplash_mermaid', (col, row), f'acc_colorsplash{mermaidcollar}')

        # harnesses
        for row, harnesses in enumerate(harnesses_data):
            for col, harness in enumerate(harnesses):
                self.make_group('harnesses', (col, row), f'collars{harness}')
        # bows (on ear and tail) 
        for row, bows in enumerate(bows_data):
            for col, bow in enumerate(bows):
                self.make_group('bows', (col, row), f'bows{bow}')
        # dog teeth collars
        for row, teethcollars in enumerate(dog_teeth_collars_data):
            for col, teethcollar in enumerate(teethcollars):
                self.make_group('teethcollars', (col, row), f'collars{teethcollar}')
        # ties 
        for row, ties in enumerate(ties_data):
            for col, tie in enumerate(ties):
                self.make_group("ties", (col, row), f"collars{tie}")
        # french_scarves
        for row, frenchscarvess in enumerate(french_scarves_data):
            for col, frenchscarf in enumerate(frenchscarvess):
                self.make_group("french_scarves", (col, row), f"collars{frenchscarf}")

        # ster
        for row, sterflowers in enumerate(ster_data):
            for col, sterflower in enumerate(sterflowers):
                self.make_group("sterflowers", (col, row), f"acc_ster{sterflower}")

        # boosbandanas
        for row, boosbandanas_accessories in enumerate(boos_data):
            for col, boosbandana in enumerate(boosbandanas_accessories):
                self.make_group("boosbandanas_accessories", (col, row), f"collars{boosbandana}")

        # sailor moon
        for row, sailormoon in enumerate(sailormoon_data):
            for col, sailormoonacc in enumerate(sailormoon):
                self.make_group("sailormoon", (col, row), f"acc_sailor{sailormoonacc}")
        # random
        for row, randomaccessories in enumerate(random_data):
            for col, randomaccessory in enumerate(randomaccessories):
                self.make_group("randomaccessories", (col, row), f"acc_random{randomaccessory}")

        # beetles
        for row, beetle_accessories in enumerate(beetle_accessories_data):
            for col, beetleaccessory in enumerate(beetle_accessories):
                self.make_group("beetle_accessories", (col, row), f"acc_beetle{beetleaccessory}")
        for row, beetle_feathers in enumerate(beetle_feathers_data):
            for col, beetlefeather in enumerate(beetle_feathers):
                self.make_group("beetle_feathers", (col, row), f"acc_beetlefeathers{beetlefeather}")

        # chimes
        for row, chimes in enumerate(chime_data):
            for col, chimeaccessory in enumerate(chimes):
                self.make_group("star_chimes", (col, row), f"acc_chime{chimeaccessory}")

        # lantern
        for row, lanterns in enumerate(lantern_data):
            for col, lantern in enumerate(lanterns):
                self.make_group("lantern", (col, row), f"acc_lantern{lantern}")

        # moss's accessories
        for row, moss_accessories in enumerate(moss_data):
            for col, moss_accessory in enumerate(moss_accessories):
                self.make_group('moss_accs', (col, row), f'acc_herbs{moss_accessory}')

        for row, neckerchiefs in enumerate(neckerchief_data):
            for col, neckerchief in enumerate(neckerchiefs):
                self.make_group("colorsplash_neckerchief", (col, row), f"acc_neckerchief{neckerchief}")

        for row, hats in enumerate(witchhat_data):
            for col, hat in enumerate(hats):
                self.make_group("colorsplash_witchhat", (col, row), f"acc_witchhat{hat}")

        for row, mons in enumerate(pokemon_data):
            for col, mon in enumerate(mons):
                self.make_group("pokemon", (col, row), f"acc_pokemon{mon}")

    def load_symbols(self):
        """
        loads clan symbols
        """

        if os.path.exists("resources/dicts/clan_symbols.json"):
            with open(
                "resources/dicts/clan_symbols.json", encoding="utf-8"
            ) as read_file:
                self.symbol_dict = ujson.loads(read_file.read())

        # U and X omitted from letter list due to having no prefixes
        letters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "V",
            "W",
            "Y",
            "Z",
        ]

        # sprite names will format as "symbol{PREFIX}{INDEX}", ex. "symbolSPRING0"
        y_pos = 1
        for letter in letters:
            x_mod = 0
            for i, symbol in enumerate(
                [
                    symbol
                    for symbol in self.symbol_dict
                    if letter in symbol and self.symbol_dict[symbol]["variants"]
                ]
            ):
                if self.symbol_dict[symbol]["variants"] > 1 and x_mod > 0:
                    x_mod += -1
                for variant_index in range(self.symbol_dict[symbol]["variants"]):
                    x_pos = i + x_mod

                    if self.symbol_dict[symbol]["variants"] > 1:
                        x_mod += 1
                    elif x_mod > 0:
                        x_pos += -1

                    self.clan_symbols.append(f"symbol{symbol.upper()}{variant_index}")
                    self.make_group(
                        "symbols",
                        (x_pos, y_pos),
                        f"symbol{symbol.upper()}{variant_index}",
                        sprites_x=1,
                        sprites_y=1,
                        no_index=True,
                    )

            y_pos += 1

    def get_symbol(self, symbol: str, force_light=False):
        """Change the color of the symbol to match the requested theme, then return it
        :param Surface symbol: The clan symbol to convert
        :param force_light: Use to ignore dark mode and always display the light mode color
        """
        symbol = self.sprites.get(symbol)
        if symbol is None:
            logger.warning("%s is not a known Clan symbol! Using default.")
            symbol = self.sprites[self.clan_symbols[0]]

        recolored_symbol = copy(symbol)
        var = pygame.PixelArray(recolored_symbol)
        var.replace(
            (87, 76, 45),
            (
                pygame.Color(constants.CONFIG["theme"]["dark_mode_clan_symbols"])
                if not force_light and game_setting_get("dark mode")
                else pygame.Color(constants.CONFIG["theme"]["light_mode_clan_symbols"])
            ),
            distance=0,
        )
        del var

        return recolored_symbol


# CREATE INSTANCE
sprites = Sprites()
