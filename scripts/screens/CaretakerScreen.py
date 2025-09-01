from math import ceil
from random import choice, randint

import i18n
import pygame.transform
import pygame_gui.elements

from scripts.cat.cats import Cat
from ..cat.enums import CatAge, CatRank, CatGroup
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UIRelationStatusBar,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    shorten_text_to_fit,
    ui_scale_dimensions,
)
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon
from ..game_structure.game.switches import switch_get_value, Switch
from ..clan_package.settings import get_clan_setting
from ..game_structure.game.settings import game_setting_get


class CaretakerScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.selected_caretaker = None
        self.selected_cat_1 = None
        self.selected_cat_2 = None
        self.search_bar = None
        self.search_bar_image = None
        self.caretaker_elements = {}
        self.caretakers = []
        self.cat_buttons = []
        self.page = 1
        self.selected_cat_elements = {}
        self.current_listed_cats = None
        self.previous_search_text = ""
        
        
        self.mental_skills = ["TEACHER", "STORY", "PATIENT", "LANGUAGE", "SCHOLAR", "THINKER",
                              "INSIGHTFUL", "MEDIATOR", "GRACE", "MEMORY", "SWIMMER", "RUNNER",
                              "AGILE", "SPEAKER", "CLEVER", "SENSE", "LORE", "HISTORIAN", "INNOVATOR",
                              "TIME", "ASSIST","COOPERATIVE"]
        self.physical_skills = ["FIGHTER", "GUARDIAN", "CLIMBER","HUNTER", "TRACKER","TUNNELER",
                                "EXPLORER", "FISHER", "NAVIGATOR","HIDER", "CAMP", "STEALTHY",
                                "MESSENGER", "STRONG"]
        self.spirit_skills = ["STAR", "CLAIRVOYANT","OMEN", "GHOST", "DARK", "PROPHET", "DREAM",
                              "UNKNOWN", "LEADERSHIP", "VIBES", "AURAVIBES","COMFORTER", "PRODIGY",
                              "ANIMAL MAGNET", "LUCK"]
        self.activity_skills = ["HYDRO", "CLEAN", "SONG", "ARTISAN", "CHEF", "DETECTIVE", "BOOKMAKER",
                                "DECORATOR", "DELIVERER", "ANIMALTAKER", "VET","MATCHMAKER", "STARGAZER",
                                "WAKEFUL", "GARDENER","PYRO", "HERBALIST", "DISGUISE", "TREASURE", "HEALER",
                                "KIT","SLEEPER", "WEATHER", "IMMUNE", "MUSICVIBES","GIFTGIVER", "BONES", "BUG"]

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.last_med:
                self.selected_caretaker -= 1
                self.update_caretaker_info()
            elif event.ui_element == self.next_med:
                self.selected_caretaker += 1
                self.update_caretaker_info()
            elif event.ui_element == self.next_page:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page:
                self.page -= 1
                self.update_page()
            elif event.ui_element == self.deselect_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            elif event.ui_element == self.deselect_2:
                self.selected_cat_2 = None
                self.update_selected_cats()
            elif event.ui_element == self.mediate_button:
                game.mediated.append([self.selected_cat_1.ID, self.selected_cat_2.ID])
                game.patrolled.append(self.caretakers[self.selected_caretaker].ID)
                output = Cat.mediate_relationship(
                    self.caretakers[self.selected_caretaker],
                    self.selected_cat_1,
                    self.selected_cat_2,
                    False,
                )
                new_skill_chance1 = randint(1,8)
                new_skill_chance2 = randint(1,8)
                if new_skill_chance1 == 1 and not self.selected_cat_1.skills.secondary:
                    self.selected_cat_1.skills.gain_new_skill_as_kit(choice([choice(self.mental_skills),choice(self.mental_skills),choice(self.spirit_skills)]),"secondary")
                    output += str(self.selected_cat_1.name) + " gained a new skill!"
                elif new_skill_chance1 == 1 and not self.selected_cat_1.skills.tertiary:   
                    self.selected_cat_1.skills.gain_new_skill_as_kit(choice([choice(self.mental_skills),choice(self.mental_skills),choice(self.spirit_skills)]),"tertiary")
                    output += str(self.selected_cat_1.name) + " gained a new skill!"
                if new_skill_chance2 == 1 and not self.selected_cat_2.skills.secondary:
                    self.selected_cat_2.skills.gain_new_skill_as_kit(choice([choice(self.mental_skills),choice(self.mental_skills),choice(self.spirit_skills)]),"secondary")
                    output += str(self.selected_cat_2.name) + " gained a new skill!"
                elif new_skill_chance2 == 1 and not self.selected_cat_2.skills.tertiary:   
                    self.selected_cat_2.skills.gain_new_skill_as_kit(choice([choice(self.mental_skills),choice(self.mental_skills),choice(self.spirit_skills)]),"tertiary")
                    output += str(self.selected_cat_2.name) + " gained a new skill!"
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_caretaker_info()
            elif event.ui_element == self.sabotage_button:
                game.mediated.append([self.selected_cat_1.ID, self.selected_cat_2.ID])
                game.patrolled.append(self.caretakers[self.selected_caretaker].ID)
                output = Cat.mediate_relationship(
                    self.caretakers[self.selected_caretaker],
                    self.selected_cat_1,
                    self.selected_cat_2,
                    False,
                )
                new_skill_chance1 = randint(1,8)
                new_skill_chance2 = randint(1,8)
                
                if new_skill_chance1 == 1 and not self.selected_cat_1.skills.secondary:
                    self.selected_cat_1.skills.gain_new_skill_as_kit(choice([choice(self.physical_skills),choice(self.physical_skills),choice(self.activity_skills)]),"secondary")
                    output += str(self.selected_cat_1.name) + " gained a new skill!"
                elif new_skill_chance1 == 1 and not self.selected_cat_1.skills.tertiary:   
                    self.selected_cat_1.skills.gain_new_skill_as_kit(choice([choice(self.physical_skills),choice(self.physical_skills),choice(self.activity_skills)]),"tertiary")
                    output += str(self.selected_cat_1.name) + " gained a new skill!"
                if new_skill_chance2 == 1 and not self.selected_cat_2.skills.secondary:
                    self.selected_cat_2.skills.gain_new_skill_as_kit(choice([choice(self.physical_skills),choice(self.physical_skills),choice(self.activity_skills)]),"secondary")
                    output += str(self.selected_cat_2.name) + " gained a new skill!"
                elif new_skill_chance2 == 1 and not self.selected_cat_2.skills.tertiary:   
                    self.selected_cat_2.skills.gain_new_skill_as_kit(choice([choice(self.physical_skills),choice(self.physical_skills),choice(self.activity_skills)]),"tertiary")
                    output += str(self.selected_cat_2.name) + " gained a new skill!"
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_caretaker_info()
            elif event.ui_element == self.random1:
                self.selected_cat_1 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_2 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element == self.random2:
                self.selected_cat_2 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_1 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element in self.cat_buttons:
                if event.ui_element.return_cat_object() not in [
                    self.selected_cat_1,
                    self.selected_cat_2,
                ]:
                    if (
                        pygame.key.get_mods() & pygame.KMOD_SHIFT
                        or not self.selected_cat_1
                    ):
                        self.selected_cat_1 = event.ui_element.return_cat_object()
                    else:
                        self.selected_cat_2 = event.ui_element.return_cat_object()
                    self.update_selected_cats()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        # Gather the caretakers:
        self.caretakers = []
        for cat in Cat.all_cats_list:
            if cat.status.rank in [CatRank.CARETAKER, CatRank.CARETAKER_APPRENTICE] and cat.status.alive_in_player_clan:
                self.caretakers.append(cat)

        self.page = 1

        if self.caretakers:
            if Cat.fetch_cat(switch_get_value(Switch.cat)) in self.caretakers:
                self.selected_caretaker = self.caretakers.index(
                    Cat.fetch_cat(switch_get_value(Switch.cat))
                )
            else:
                self.selected_caretaker = 0
        else:
            self.selected_caretaker = None

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.selected_frame_1 = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 80), (200, 350))),
            get_box(BoxStyles.ROUNDED_BOX, (200, 350)),
        )
        self.selected_frame_1.disable()
        self.selected_frame_2 = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((550, 80), (200, 350))),
            get_box(BoxStyles.ROUNDED_BOX, (200, 350)),
        )
        self.selected_frame_2.disable()

        self.cat_bg = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 470), (700, 150))),
            get_box(BoxStyles.ROUNDED_BOX, (700, 150)),
        )
        self.cat_bg.disable()

        # Will be overwritten

        self.mediate_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((280, 350), (105, 30))),
            "Tell Story",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.sabotage_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((400, 350), (109, 30))),
            "Play Game",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.next_med = UISurfaceImageButton(
            ui_scale(pygame.Rect((476, 270), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )
        self.last_med = UISurfaceImageButton(
            ui_scale(pygame.Rect((280, 270), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )

        self.next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((433, 619), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.previous_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((333, 619), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )

        self.deselect_1 = UISurfaceImageButton(
            ui_scale(pygame.Rect((68, 434), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.deselect_2 = UISurfaceImageButton(
            ui_scale(pygame.Rect((605, 434), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.results = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 385), (229, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.error = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 37), (229, 57))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.random1 = UISurfaceImageButton(
            ui_scale(pygame.Rect((198, 432), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        self.random2 = UISurfaceImageButton(
            ui_scale(pygame.Rect((568, 432), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )

        self.search_bar_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((55, 625), (118, 34))),
            pygame.image.load("resources/images/search_bar.png").convert_alpha(),
            manager=MANAGER,
        )
        self.search_bar = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((60, 629), (115, 27))),
            object_id="#search_entry_box",
            placeholder_text="general.name_search",
            manager=MANAGER,
        )

        self.update_buttons()
        self.update_caretaker_info()

    def random_cat(self):
        if self.selected_cat_list():
            random_list = [
                i for i in self.all_cats_list if i.ID not in self.selected_cat_list()
            ]
        else:
            random_list = self.all_cats_list
        return choice(random_list)

    def update_caretaker_info(self):
        for ele in self.caretaker_elements:
            self.caretaker_elements[ele].kill()
        self.caretaker_elements = {}

        if (
            self.selected_caretaker is not None
        ):  # It can be zero, so we must test for not None here.
            x_value = 315
            caretaker = self.caretakers[self.selected_caretaker]

            # Clear caretaker as selected cat
            if caretaker == self.selected_cat_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            if caretaker == self.selected_cat_2:
                self.selected_cat_2 = None
                self.update_selected_cats()

            self.caretaker_elements["caretaker_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_value, 90), (150, 150))),
                pygame.transform.scale(
                    caretaker.sprite, ui_scale_dimensions((150, 150))
                ),
            )

            name = str(caretaker.name)
            short_name = shorten_text_to_fit(name, 120, 11)
            self.caretaker_elements["name"] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x_value - 5, 240), (160, -1))),
                short_name,
                object_id=get_text_box_theme(),
            )
            
            trait_text = caretaker.personality.trait
            if caretaker.personality.trait != caretaker.personality.trait2:
                trait_text += " & " + caretaker.personality.trait2

            text = trait_text + "\n" + caretaker.experience_level

            if caretaker.not_working():
                text += "\n" + i18n.t("general.cant_work")
                self.mediate_button.disable()
                self.sabotage_button.disable()
            else:
                text += "\n" + i18n.t("general.can_work")
                self.mediate_button.enable()
                self.sabotage_button.enable()

            self.caretaker_elements["details"] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(pygame.Rect((x_value, 260), (155, 60))),
                object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                manager=MANAGER,
            )

            caretaker_number = len(self.caretakers)
            if self.selected_caretaker < caretaker_number - 1:
                self.next_med.enable()
            else:
                self.next_med.disable()

            if self.selected_caretaker > 0:
                self.last_med.enable()
            else:
                self.last_med.disable()

        else:
            self.last_med.disable()
            self.next_med.disable()

        self.update_buttons()
        self.update_list_cats()

    def update_list_cats(self):
        self.all_cats_list = [
            i
            for i in Cat.all_cats_list
            if (i.ID != self.caretakers[self.selected_caretaker].ID)
            and i.status.alive_in_player_clan
            and i.status.rank == CatRank.KITTEN
        ]
        self.all_cats = self.chunks(self.all_cats_list, 24)
        self.current_listed_cats = self.all_cats_list
        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )
        self.update_page()

    def update_page(self):
        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []
        if self.page > self.all_pages:
            self.page = self.all_pages
        elif self.page < 1:
            self.page = 1

        if self.page >= self.all_pages:
            self.next_page.disable()
        else:
            self.next_page.enable()

        if self.page <= 1:
            self.previous_page.disable()
        else:
            self.previous_page.enable()

        x = 65
        y = 485
        chunked_cats = self.chunks(self.current_listed_cats, 24)
        if chunked_cats:
            for cat in chunked_cats[self.page - 1]:
                if get_clan_setting("show fav") and cat.favourite:
                    _temp = pygame.transform.scale(
                        pygame.image.load(
                            f"resources/images/fav_marker.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((50, 50)),
                    )

                    self.cat_buttons.append(
                        pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((x, y), (50, 50))), _temp
                        )
                    )
                    self.cat_buttons[-1].disable()

                self.cat_buttons.append(
                    UISpriteButton(
                        ui_scale(pygame.Rect((x, y), (50, 50))),
                        cat.sprite,
                        cat_object=cat,
                    )
                )
                x += 55
                if x > 700:
                    y += 55
                    x = 65

    def update_selected_cats(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.draw_info_block(self.selected_cat_1, (50, 80))
        self.draw_info_block(self.selected_cat_2, (550, 80))

        self.update_buttons()

    def draw_info_block(self, cat, starting_pos: tuple):
        if not cat:
            return

        other_cat = [Cat.fetch_cat(i) for i in self.selected_cat_list() if i != cat.ID]
        if other_cat:
            other_cat = other_cat[0]
        else:
            other_cat = None

        tag = str(starting_pos)

        x = starting_pos[0]
        y = starting_pos[1]

        self.selected_cat_elements["cat_image" + tag] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x + 50, y + 7), (100, 100))),
            pygame.transform.scale(cat.sprite, ui_scale_dimensions((100, 100))),
        )

        name = str(cat.name)
        short_name = shorten_text_to_fit(name, 62, 7)
        self.selected_cat_elements["name" + tag] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((x, y + 100), (200, 30))),
            short_name,
            object_id="#text_box_30_horizcenter",
        )

        # Gender
        if cat.genderalign == "female":
            gender_icon = image_cache.load_image(
                "resources/images/female_big.png"
            ).convert_alpha()
        elif cat.genderalign == "male":
            gender_icon = image_cache.load_image(
                "resources/images/male_big.png"
            ).convert_alpha()
        elif cat.gender == "intersex" and cat.genderalign == "trans female":
                gender_icon = image_cache.load_image(
                    "resources/images/transfem_intersex_big.png"
                ).convert_alpha()
        elif cat.gender == "intersex" and cat.genderalign == "trans male":
                gender_icon = image_cache.load_image(
                    "resources/images/transmasc_intersex_big.png"
                ).convert_alpha()
        elif cat.genderalign == "intersex":
                gender_icon = image_cache.load_image(
                    "resources/images/intersex_big.png"
                ).convert_alpha()
        elif cat.genderalign == "trans female":
            gender_icon = image_cache.load_image(
                "resources/images/transfem_big.png"
            ).convert_alpha()
        elif cat.genderalign == "trans male":
            gender_icon = image_cache.load_image(
                "resources/images/transmasc_big.png"
            ).convert_alpha()
        else:
            # Everyone else gets the nonbinary icon
            gender_icon = image_cache.load_image(
                "resources/images/nonbi_big.png"
            ).convert_alpha()

        self.selected_cat_elements["gender" + tag] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x + 160, y + 12), (25, 25))),
            pygame.transform.scale(gender_icon, ui_scale_dimensions((25, 25))),
        )

        related = False
        if other_cat:
            # FAMILY DOT
            # Only show family dot on cousins if first cousin mates are disabled.
            if get_clan_setting("first cousin mates"):
                check_cousins = False
            else:
                check_cousins = other_cat.is_cousin(cat)

            if (
                other_cat.is_uncle_aunt(cat)
                or cat.is_uncle_aunt(other_cat)
                or other_cat.is_grandparent(cat)
                or cat.is_grandparent(other_cat)
                or other_cat.is_parent(cat)
                or cat.is_parent(other_cat)
                or other_cat.is_sibling(cat)
                or check_cousins
            ):
                related = True
                self.selected_cat_elements[
                    "relation_icon" + tag
                ] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((x + 14, y + 14), (18, 18))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/dot_big.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((18, 18)),
                    ),
                )

        col2 = i18n.t("general.moons_age", count=cat.moons)
        col1 = i18n.t(f"cat.personality.{cat.personality.trait}")
        if cat.personality.trait != cat.personality.trait2:
            col1+= " & " + i18n.t(f"cat.personality.{cat.personality.trait2}")
        self.selected_cat_elements["col1" + tag] = pygame_gui.elements.UITextBox(
            col1,
            ui_scale(pygame.Rect((x + 21, y + 126), (90, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )
        # Relation info:
        if related and other_cat:
            col2 += "\n"
            if other_cat.is_uncle_aunt(cat):
                if cat.genderalign in ["female", "trans female"]:
                    col2 += i18n.t("general.niece")
                elif cat.genderalign in ["male", "trans male"]:
                    col2 += i18n.t("general.nephew")
                else:
                    col2 += i18n.t("general.siblings_child")
            elif cat.is_uncle_aunt(other_cat):
                if cat.genderalign in ["female", "trans female"]:
                    col2 += i18n.t("general.aunt")
                elif cat.genderalign in ["male", "trans male"]:
                    col2 += i18n.t("general.uncle")
                else:
                    col2 += i18n.t("general.parents_sibling")
            elif cat.is_grandparent(other_cat):
                col2 += i18n.t("general.grandparent")
            elif other_cat.is_grandparent(cat):
                col2 += i18n.t("general.grandchild")
            elif cat.is_parent(other_cat):
                col2 += i18n.t("general.parent")
            elif other_cat.is_parent(cat):
                col2 += i18n.t("general.child")
            elif cat.is_sibling(other_cat) or other_cat.is_sibling(cat):
                col2 += i18n.t("general.sibling")
            elif not game.clan.clan_settings[
                "first cousin mates"
            ] and other_cat.is_cousin(cat):
                col2 += i18n.t("general.cousin")

        self.selected_cat_elements["col2" + tag] = pygame_gui.elements.UITextBox(
            col2,
            ui_scale(pygame.Rect((x + 110, y + 126), (80, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        if other_cat:
            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 68, 11)

            self.selected_cat_elements[
                f"relation_heading{tag}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x + 20, y + 160), (160, -1))),
                "screens.mediation.cat_feelings",
                object_id="#text_box_22_horizcenter",
                text_kwargs={"name": short_name, "m_c": cat},
            )

            if other_cat.ID in cat.relationships:
                the_relationship = cat.relationships[other_cat.ID]
            else:
                the_relationship = cat.create_one_relationship(other_cat)

            barbar = 21
            bar_count = 0
            y_start = 177
            x_start = 25

            # PLATONIC
            self.selected_cat_elements[
                f"plantonic_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                "relationships.platonic_label",
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                text_kwargs={"count": 2 if the_relationship.platonic_like > 49 else 1},
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"platonic_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
                    )
                ),
                the_relationship.platonic_like,
                positive_trait=True,
                dark_mode=game_setting_get("dark mode"),
            )

            bar_count += 1

            # DISLIKE
            self.selected_cat_elements[
                f"dislike_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                "relationships.dislike_label",
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                text_kwargs={"count": 2 if the_relationship.dislike > 49 else 1},
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"dislike_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
                    )
                ),
                the_relationship.dislike,
                positive_trait=False,
                dark_mode=game_setting_get("dark mode"),
            )

            bar_count += 1

            # ADMIRE
            self.selected_cat_elements[
                f"admiration_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                "relationships.admire_label",
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
                text_kwargs={"count": 2 if the_relationship.admiration > 49 else 1},
            )
            self.selected_cat_elements[f"admiration_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
                    )
                ),
                the_relationship.admiration,
                positive_trait=True,
                dark_mode=game_setting_get("dark mode"),
            )

            bar_count += 1

            # COMFORTABLE
            self.selected_cat_elements[
                f"comfortable_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                "relationships.comfortable_label",
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
                text_kwargs={"count": 2 if the_relationship.comfortable > 49 else 1},
            )
            self.selected_cat_elements[f"comfortable_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
                    )
                ),
                the_relationship.comfortable,
                positive_trait=True,
                dark_mode=game_setting_get("dark mode"),
            )

            bar_count += 1

            # JEALOUS
            self.selected_cat_elements[
                f"jealous_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                "relationships.jealous_label",
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
                text_kwargs={"count": 2 if the_relationship.comfortable > 49 else 1},
            )
            self.selected_cat_elements[f"jealous_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
                    )
                ),
                the_relationship.jealousy,
                positive_trait=False,
                dark_mode=game_setting_get("dark mode"),
            )

            bar_count += 1

            # TRUST
            if the_relationship.trust > 49:
                text = "reliance:"
            else:
                text = "trust:"
            self.selected_cat_elements[
                f"trust_text{tag}"
            ] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + (barbar * bar_count) - 5),
                        (150, 30),
                    )
                ),
                object_id="#text_box_22_horizleft",
            )
            self.selected_cat_elements[f"trust_bar{tag}"] = UIRelationStatusBar(
                ui_scale(
                    pygame.Rect(
                        (x + x_start, y + y_start + 15 + (barbar * bar_count)),
                        (150, 9),
                    )
                ),
                the_relationship.trust,
                positive_trait=True,
                dark_mode=game_setting_get("dark mode"),
            )

    def selected_cat_list(self):
        output = []
        if self.selected_cat_1:
            output.append(self.selected_cat_1.ID)
        if self.selected_cat_2:
            output.append(self.selected_cat_2.ID)

        return output

    def update_buttons(self):
        error_message = ""

        invalid_caretaker = False
        if self.selected_caretaker is not None:
            if self.caretakers[self.selected_caretaker].not_working():
                invalid_caretaker = True
                error_message += i18n.t("screens.mediation.care_cant_work")
            elif self.caretakers[self.selected_caretaker].ID in game.patrolled:
                invalid_caretaker = True
                error_message += i18n.t("screens.mediation.care_already_worked")
        else:
            invalid_caretaker = True

        invalid_pair = False
        if self.selected_cat_1 and self.selected_cat_2:
            for x in game.mediated:
                if self.selected_cat_1.ID in x and self.selected_cat_2.ID in x:
                    invalid_pair = True
                    error_message += i18n.t("screens.mediation.pair_already_mediated")
                    break
        else:
            invalid_pair = True

        self.error.set_text(error_message)

        if invalid_caretaker or invalid_pair:
            self.mediate_button.disable()
            self.sabotage_button.disable()
        else:
            self.mediate_button.enable()
            self.sabotage_button.enable()

    def update_search_cats(self, search_text):
        """Run this function when the search text changes, or when the screen is switched to."""
        self.current_listed_cats = []
        Cat.sort_cats(self.all_cats_list)
        kittens_list = []
        for cat in self.all_cats_list:
            if cat.status.rank == CatRank.KITTEN:
                kittens_list.append(cat)

        search_text = search_text.strip()
        if search_text not in [""]:
            for cat in kittens_list:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = kittens_list.copy()

        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )

        Cat.ordered_cat_list = self.current_listed_cats
        self.update_page()

    def exit_screen(self):
        self.selected_cat_1 = None
        self.selected_cat_2 = None

        for ele in self.caretaker_elements:
            self.caretaker_elements[ele].kill()
        self.caretaker_elements = {}

        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.caretakers = []
        self.back_button.kill()
        del self.back_button
        self.selected_frame_1.kill()
        del self.selected_frame_1
        self.selected_frame_2.kill()
        del self.selected_frame_2
        self.cat_bg.kill()
        del self.cat_bg
        self.mediate_button.kill()
        del self.mediate_button
        self.sabotage_button.kill()
        del self.sabotage_button
        self.last_med.kill()
        del self.last_med
        self.next_med.kill()
        del self.next_med
        self.deselect_1.kill()
        del self.deselect_1
        self.deselect_2.kill()
        del self.deselect_2
        self.next_page.kill()
        del self.next_page
        self.previous_page.kill()
        del self.previous_page
        self.results.kill()
        del self.results
        self.random1.kill()
        del self.random1
        self.random2.kill()
        del self.random2
        self.error.kill()
        del self.error
        self.search_bar_image.kill()
        del self.search_bar_image
        self.search_bar.kill()
        del self.search_bar

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]

    def on_use(self):
        super().on_use()
        # Only update the positions if the search text changes
        if self.search_bar.is_focused and self.search_bar.get_text() == "name search":
            self.search_bar.set_text("")
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()
