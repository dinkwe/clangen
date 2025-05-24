from math import ceil
from random import choice

import i18n
import pygame.transform
from pygame import Rect
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.cat.pelts import Pelt
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from pygame_gui.elements import UIDropDownMenu, UITextBox
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
    adjust_list_text,
)
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon

""" Cat customization UI """

# generate UI elements
def create_text_box(text, pos, size, theme, anchors=None):
    return UITextBox(
        text,
        ui_scale(Rect(pos, size)),
        manager=MANAGER,
        object_id=get_text_box_theme(theme),
        anchors=anchors
    )


def create_button(pos, size, text, style, anchors=None, sound_id=None):
    return UISurfaceImageButton(
        ui_scale(Rect(pos, size)),
        text,
        get_button_dict(style, size),
        object_id=f"@buttonstyles_{style.name.lower()}",
        manager=MANAGER,
        anchors=anchors,
        sound_id=sound_id
    )


def create_dropdown(pos, size, options, selected_option, style=None):
    return UIDropDownMenu(
        options,
        selected_option,
        ui_scale(Rect(pos, size)),
        object_id=f"#{style}",
        manager=MANAGER
    )

# creates a list with display names and values of cat pelt attributes
def create_options_list(attribute, case):
    if case == "upper":
        return [(option.capitalize(), option.upper()) for option in attribute]
    elif case == "lower":
        return [(option.capitalize(), option.lower()) for option in attribute]
    else:
        return [(option.capitalize(), option) for option in attribute]

# returns the name and value; returns none if dropdown is disabled
def get_selected_option(attribute, case):
    if isinstance(attribute, list):
        if len(attribute) > 0:  # selects an option in scar dropdowns for any existing scars
            return attribute[0].capitalize(), attribute[0].upper()
        else:
            return "None", "NONE"
    if attribute:
        if case == "upper":
            return attribute.capitalize(), attribute.upper()
        elif case == "lower":
            return attribute.capitalize(), attribute.lower()
        else:
            return attribute.capitalize(), attribute
    else:
        if case == "upper":
            return "None", "NONE"
        elif case == "lower":
            return "None", "none"
        else:
            return "None", "None"
        
class GardenerScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.selected_gardener = None
        self.selected_cat = None
        self.search_bar = None
        self.search_bar_image = None
        self.gardener_elements = {}
        self.gardeners = []
        self.cat_buttons = []
        self.page = 1
        self.selected_cat_elements = {}
        self.current_listed_cats = None
        self.previous_search_text = ""
        self.garden = None
        self.selected_submenu = None
        
        self.accessories = []
        self.accessory_dropdown = None
        self.accessory_label = None
        self.acc_preview = None
        self.acc_bonuses = None
        self.acc_bonus_label = None
        self.acc_bonus_dropdown = None
        self.craft_button = None
        self.init_acc = None
        self.new_acc = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.last_med:
                self.selected_gardener -= 1
                self.update_gardener_info()
            elif event.ui_element == self.next_med:
                self.selected_gardener += 1
                self.update_gardener_info()
            elif event.ui_element == self.next_page:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page:
                self.page -= 1
                self.update_page()
            elif event.ui_element == self.deselect:
                if self.selected_submenu is not None:
                    self.acc_preview.kill()
                    self.selected_cat.pelt.accessory.remove(self.new_acc)
                    self.acc_bonus_label.kill()
                    self.acc_bonus_dropdown.kill()
                    self.accessory_label.kill()
                    self.accessory_dropdown.kill()
                    self.craft_button.kill()
                    self.selected_submenu = None
                self.selected_cat = None
                self.update_selected_cats()
            elif event.ui_element == self.farm_button:
                game.patrolled.append(self.gardeners[self.selected_gardener].ID)
                #lets get those herbs yippee
                list_of_herb_strs = []
                list_of_herb_strs, found_herbs = game.clan.herb_supply.get_found_herbs(
                    med_cat=self.gardeners[self.selected_gardener],
                    general_amount_bonus=False,
                    specific_quantity_bonus=1,
                )
                herb_string = adjust_list_text(list_of_herb_strs).capitalize()
                full_amount_count = sum(found_herbs.values())
                
                output = i18n.t("screens.patrol.herb_log", count=full_amount_count, herbs=herb_string)
                
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_gardener_info()
            elif event.ui_element == self.acc_button:
                self.selected_submenu = "accessory"
                self.setup_accessory()
                self.update_gardener_info()
            elif event.ui_element == self.random:
                if self.selected_submenu is not None:
                    self.acc_preview.kill()
                    self.selected_cat.pelt.accessory.remove(self.new_acc)
                    self.acc_bonus_label.kill()
                    self.acc_bonus_dropdown.kill()
                    self.accessory_label.kill()
                    self.accessory_dropdown.kill()
                    self.craft_button.kill()
                self.selected_cat = self.random_cat()
                self.update_selected_cats()
                if self.selected_submenu is not None:
                    self.setup_accessory()
            elif event.ui_element in self.cat_buttons:
                if self.selected_submenu is not None:
                    self.acc_preview.kill()
                    self.selected_cat.pelt.accessory.remove(self.new_acc)
                    self.acc_bonus_label.kill()
                    self.acc_bonus_dropdown.kill()
                    self.accessory_label.kill()
                    self.accessory_dropdown.kill()
                    self.craft_button.kill()
                self.selected_cat = event.ui_element.return_cat_object()
                self.update_selected_cats()
                if self.selected_submenu is not None:
                    self.setup_accessory()
            elif event.ui_element == self.craft_button:
                game.patrolled.append(self.gardeners[self.selected_gardener].ID)
                game.mediated.append(self.selected_cat.ID)
                output = str(self.selected_cat.name) + " recieved a new accessory!"
                if len(self.acc_bonuses) > 1:
                    #yay! bonuses
                    bonus_type = self.acc_bonus_dropdown.selected_option[1]
                    if bonus_type == "MATES":
                        output = str(self.selected_cat.name) + " recieved a new accessory, impressing their mate(s)!"
                        for mate_id in self.selected_cat.mate:
                            mate = Cat.fetch_cat(mate_id)
                            #just in case somehow they dont have a relationship
                            if self.selected_cat.ID in mate.relationships:
                                rel = mate.relationships[self.selected_cat.ID]
                            else:
                                rel = mate.create_one_relationship(self.selected_cat)
                                
                            if mate.ID in self.selected_cat.relationships:
                                rel2 = self.selected_cat.relationships[mate.ID]
                            else:
                                rel2 = self.selected_cat.create_one_relationship(mate)
                                
                            rel.admiration = Cat.effect_relation(rel.admiration,5)
                            rel.trust = Cat.effect_relation(rel.trust,5)
                            rel.trust = Cat.effect_relation(rel.romantic_love,5)
                            rel2.admiration = Cat.effect_relation(rel2.admiration,5)
                            rel2.trust = Cat.effect_relation(rel2.trust,5)
                            rel2.trust = Cat.effect_relation(rel2.romantic_love,5)
                            
                    elif bonus_type == "BEST FRIENDS":
                        output = str(self.selected_cat.name) + " recieved a new accessory, impressing their best friend(s)!"
                        for bestie_id in self.selected_cat.bestie:
                            bestie = Cat.fetch_cat(bestie_id)
                            #just in case somehow they dont have a relationship
                            if self.selected_cat.ID in bestie.relationships:
                                rel = bestie.relationships[self.selected_cat.ID]
                            else:
                                rel = bestie.create_one_relationship(self.selected_cat)
                                
                            if bestie.ID in self.selected_cat.relationships:
                                rel2 = self.selected_cat.relationships[bestie.ID]
                            else:
                                rel2 = self.selected_cat.create_one_relationship(bestie)
                                
                            rel.admiration = Cat.effect_relation(rel.admiration,5)
                            rel.trust = Cat.effect_relation(rel.trust,5)
                            rel.trust = Cat.effect_relation(rel.platonic_like,5)
                            rel2.admiration = Cat.effect_relation(rel2.admiration,5)
                            rel2.trust = Cat.effect_relation(rel2.trust,5)
                            rel2.trust = Cat.effect_relation(rel2.platonic_like,5)
                            
                    elif bonus_type == "ENEMIES":
                        output = str(self.selected_cat.name) + " recieved a new accessory, making their rival(s) jealous!"
                        for enemy_id in self.selected_cat.enemy:
                            enemy = Cat.fetch_cat(enemy_id)
                            #just in case somehow they dont have a relationship
                            if self.selected_cat.ID in enemy.relationships:
                                rel = enemy.relationships[self.selected_cat.ID]
                            else:
                                rel = enemy.create_one_relationship(self.selected_cat)
                                
                            if enemy.ID in self.selected_cat.relationships:
                                rel2 = self. selected_cat.relationships[enemy.ID]
                            else:
                                rel2 = self.selected_cat.create_one_relationship(enemy)
                                
                            rel.admiration = Cat.effect_relation(rel.jealousy,5)
                            rel.trust = Cat.effect_relation(rel.dislike,5)
                            rel.trust = Cat.effect_relation(rel.platonic_like,-5)
                            rel2.admiration = Cat.effect_relation(rel2.jealousy,5)
                            rel2.trust = Cat.effect_relation(rel2.dislike,5)
                            rel2.trust = Cat.effect_relation(rel2.platonic_like,-5)
                
                self.results.set_text(output)
                self.update_selected_cats()
                        
                    
                
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if self.selected_submenu == "accessory":
                if event.ui_element == self.accessory_dropdown:
                    #kill current picture, reset acc and redraw
                    self.acc_preview.kill()
                    self.selected_cat.pelt.accessory.remove(self.new_acc)
                    self.new_acc = event.ui_element.selected_option[1]
                    self.selected_cat.pelt.accessory.append(self.new_acc)
                    self.acc_preview = pygame_gui.elements.UIImage(
                        ui_scale(pygame.Rect((592, 167), (100, 100))),
                        pygame.transform.scale(self.selected_cat.sprite, ui_scale_dimensions((100, 100))),
                    )

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        # Gather the gardeners:
        self.gardeners = []
        for cat in Cat.all_cats_list:
            if cat.status in ["gardener", "gardener apprentice"] and not (
                cat.dead or cat.outside
            ):
                self.gardeners.append(cat)

        self.page = 1

        if self.gardeners:
            if Cat.fetch_cat(game.switches["cat"]) in self.gardeners:
                self.selected_gardener = self.gardeners.index(
                    Cat.fetch_cat(game.switches["cat"])
                )
            else:
                self.selected_gardener = 0
        else:
            self.selected_gardener = None

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.garden = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((250,-65), (300, 300))),
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/garden.png"
                        ).convert_alpha(),
                        (300, 300),
                    ),
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

        self.acc_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((330, 330), (135, 30))),
            "Craft Accessory",
            get_button_dict(ButtonStyles.SQUOVAL, (135, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.farm_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((330, 370), (135, 30))),
            "Farm Herbs",
            get_button_dict(ButtonStyles.SQUOVAL, (135, 30)),
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

        self.deselect = UISurfaceImageButton(
            ui_scale(pygame.Rect((68, 434), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.results = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 405), (229, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.error = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 25), (229, 57))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.random = UISurfaceImageButton(
            ui_scale(pygame.Rect((198, 432), (34, 34))),
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
        self.update_gardener_info()

    def random_cat(self):
        if self.selected_cat_list():
            random_list = [
                i for i in self.all_cats_list if i.ID not in self.selected_cat_list()
            ]
        else:
            random_list = self.all_cats_list
        return choice(random_list)
    
    def setup_accessory(self):
        self.accessories = list(
            dict.fromkeys(Pelt.plant_accessories + Pelt.flower_accessories + Pelt.bows_accessories + Pelt.plant2_accessories + Pelt.ster_accessories + Pelt.wild_accessories + Pelt.tail_accessories + Pelt.collars + Pelt.snake_accessories + Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories + Pelt.aliveInsect_accessories + Pelt.fruit_accessories + Pelt.crafted_accessories + Pelt.tail2_accessories + Pelt.bone_accessories + Pelt.butterflies_accessories + Pelt.stuff_accessories + Pelt.toy_accessories + Pelt.blankie_accessories + Pelt.flag_accessories + Pelt.wheels + Pelt.booties + Pelt.randomaccessories + Pelt.sailormoon + Pelt.beetle_feathers + Pelt.beetle_accessories + Pelt.chime_accessories))
        self.accessory_label = create_text_box("accessory", (560, 100), (135, 40), "#text_box_22_horizleft")
        
        if not isinstance(self.selected_cat.pelt.accessory, list):
            self.selected_cat.pelt.accessory = []
        self.init_acc = self.selected_cat.pelt.accessory
        self.new_acc = choice(self.accessories)
        self.selected_cat.pelt.accessory.append(self.new_acc)
        
        self.accessory_dropdown = create_dropdown((560, 125), (180, 40), create_options_list(self.accessories, "upper"),
                                                  get_selected_option(self.new_acc, "upper"), "dropdown")
        
        self.acc_preview = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((592, 167), (100, 100))),
            pygame.transform.scale(self.selected_cat.sprite, ui_scale_dimensions((100, 100))),
        )
        
        self.acc_bonuses = ["None"]
        self.acc_bonus_label = create_text_box("Boost relationships with:", (560, 260), (175, 40), "#text_box_22_horizleft")

        special_rel = False
        if len(self.selected_cat.mate) > 0:
            self.acc_bonuses.append("Mates")
            special_rel = True
        if len(self.selected_cat.bestie) > 0:
            self.acc_bonuses.append("Best Friends")
            special_rel = True
        if len(self.selected_cat.enemy) > 0:
            self.acc_bonuses.append("Enemies")
            special_rel = True
            
        self.acc_bonus_dropdown = create_dropdown((560, 285), (180, 40), create_options_list(self.acc_bonuses, "upper"),
                                                  get_selected_option("None", "upper"), "dropdown")
        if not special_rel:
            self.acc_bonus_dropdown.disable()
            
        self.craft_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((585, 350), (135, 30))),
            "Craft",
            get_button_dict(ButtonStyles.SQUOVAL, (135, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
    
    def setup_potion(self):
        return

    def update_gardener_info(self):
        for ele in self.gardener_elements:
            self.gardener_elements[ele].kill()
        self.gardener_elements = {}

        if (
            self.selected_gardener is not None
        ):  # It can be zero, so we must test for not None here.
            x_value = 315
            gardener = self.gardeners[self.selected_gardener]

            # Clear gardener as selected cat
            if gardener == self.selected_cat:
                self.selected_cat = None
                self.update_selected_cats()

            self.gardener_elements["gardener_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_value, 90), (150, 150))),
                pygame.transform.scale(
                    gardener.sprite, ui_scale_dimensions((150, 150))
                ),
            )

            name = str(gardener.name)
            short_name = shorten_text_to_fit(name, 120, 11)
            self.gardener_elements["name"] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x_value - 5, 240), (160, -1))),
                short_name,
                object_id=get_text_box_theme(),
            )

            text = gardener.personality.trait + "\n" + gardener.experience_level

            if gardener.not_working():
                text += "\n" + i18n.t("general.cant_work")
                self.acc_button.disable()
                self.farm_button.disable()
            else:
                text += "\n" + i18n.t("general.can_work")
                self.acc_button.enable()
                self.farm_button.enable()

            self.gardener_elements["details"] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(pygame.Rect((x_value, 260), (155, 60))),
                object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                manager=MANAGER,
            )

            gardener_number = len(self.gardeners)
            if self.selected_gardener < gardener_number - 1:
                self.next_med.enable()
            else:
                self.next_med.disable()

            if self.selected_gardener > 0:
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
            if (i.ID != self.gardeners[self.selected_gardener].ID)
            and not (i.dead or i.outside)
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
                if game.clan.clan_settings["show fav"] and cat.favourite:
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

        self.draw_info_block(self.selected_cat, (50, 80))

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
        
        col1 = i18n.t(f"general.{cat.status.lower()}", count=1) + "\n" + i18n.t("general.moons_age", count=cat.moons)
        trait_text = i18n.t(f"cat.personality.{cat.personality.trait}")
        if cat.personality.trait != cat.personality.trait2:
            trait_text += " & " + i18n.t(f"cat.personality.{cat.personality.trait2}")    
        col1 +=  "\n" + trait_text
        col1 += "\n" + cat.skills.skill_string()
        
        col1 += "\n"
        
        if len(cat.mate) > 0:
            col1 += "\n"

            mate_names = []
            # Grab the names of only the first two, since that's all we will display
            for _m in cat.mate[:2]:
                mate_ob = Cat.fetch_cat(_m)
                if not isinstance(mate_ob, Cat):
                    continue
                if mate_ob.dead != cat.dead:
                    if cat.dead:
                        former_indicate = "general.mate_living"
                    else:
                        former_indicate = "general.mate_dead"

                    mate_names.append(f"{str(mate_ob.name)} {i18n.t(former_indicate)}")
                elif mate_ob.outside != cat.outside:
                    mate_names.append(
                        f"{str(mate_ob.name)} {i18n.t('general.mate_away')}"
                    )
                else:
                    mate_names.append(f"{str(mate_ob.name)}")

            mate_block = ", ".join(mate_names)

            if len(cat.mate) > 2:
                mate_block = i18n.t(
                    "utility.items",
                    count=2,
                    item1=mate_block,
                    item2=i18n.t("general.mate_extra", count=len(cat.mate) - 2),
                )

            col1 += i18n.t(
                "general.mate_label", count=len(mate_names), mates=mate_block
            )
        else:
            col1 += "\n" + "mates: none"
        
        # BESTIE
        if len(cat.bestie) > 0:
            col1 += "\n"
            bestie_names = []
            # Grab the names of only the first two, since that's all we will display
            for _b in cat.bestie[:2]:
                bestie_ob = Cat.fetch_cat(_b)
                if not isinstance(bestie_ob, Cat):
                    continue
                if bestie_ob.dead != cat.dead:
                    if cat.dead:
                        former_indicate = "general.bestie_living"
                    else:
                        former_indicate = "general.bestie_dead"

                    bestie_names.append(f"{str(bestie_ob.name)} {i18n.t(former_indicate)}")
                elif bestie_ob.outside != cat.outside:
                    bestie_names.append(
                        f"{str(bestie_ob.name)} {i18n.t('general.bestie_away')}"
                    )
                else:
                    bestie_names.append(f"{str(bestie_ob.name)}")

            bestie_block = ", ".join(bestie_names)

            if len(cat.bestie) > 2:
                bestie_block = i18n.t(
                    "utility.items",
                    count=2,
                    item1=bestie_block,
                    item2=i18n.t("general.bestie_extra", count=len(cat.bestie) - 2),
                )

            col1 += i18n.t(
                "general.bestie_label", count=len(bestie_names), besties=bestie_block
            )
        else:
            col1 += "\n" + "best friends: none"
        
        # ENEMY
        if len(cat.enemy) > 0:
            col1 += "\n"

            enemy_names = []
            # Grab the names of only the first two, since that's all we will display
            for _b in cat.enemy[:2]:
                enemy_ob = Cat.fetch_cat(_b)
                if not isinstance(enemy_ob, Cat):
                    continue
                if enemy_ob.dead != cat.dead:
                    if cat.dead:
                        former_indicate = "general.enemy_living"
                    else:
                        former_indicate = "general.enemy_dead"

                    enemy_names.append(f"{str(enemy_ob.name)} {i18n.t(former_indicate)}")
                elif enemy_ob.outside != cat.outside:
                    enemy_names.append(
                        f"{str(enemy_ob.name)} {i18n.t('general.enemy_away')}"
                    )
                else:
                    enemy_names.append(f"{str(enemy_ob.name)}")

            enemy_block = ", ".join(enemy_names)

            if len(cat.enemy) > 2:
                enemy_block = i18n.t(
                    "utility.items",
                    count=2,
                    item1=enemy_block,
                    item2=i18n.t("general.enemy_extra", count=len(cat.enemy) - 2),
                )

            col1 += i18n.t(
                "general.enemy_label", count=len(enemy_names), enemies=enemy_block
            )
        else:
            col1 += "\n" + "enemies: none"
        
        
        self.selected_cat_elements["col1" + tag] = pygame_gui.elements.UITextBox(
            col1,
            ui_scale(pygame.Rect((x + 21, y + 126), (150, -1))),
            object_id="#text_box_22_horizcenter_spacing_95",
            manager=MANAGER,
        )

    def selected_cat_list(self):
        output = []
        if self.selected_cat:
            output.append(self.selected_cat.ID)

        return output

    def update_buttons(self):
        error_message = ""

        invalid_gardener = False
        if self.selected_gardener is not None:
            if self.gardeners[self.selected_gardener].not_working():
                invalid_gardener = True
                error_message += i18n.t("screens.mediation.gar_cant_work")
            elif self.gardeners[self.selected_gardener].ID in game.patrolled:
                invalid_gardener = True
                error_message += i18n.t("screens.mediation.gar_already_worked")
        else:
            invalid_gardener = True

        invalid_selection = False
        if not self.selected_cat:
            invalid_selection = True
        
        self.error.set_text(error_message)

        if invalid_gardener:
            self.acc_button.disable()
            self.farm_button.disable()
        elif invalid_selection:
            self.acc_button.disable()
            self.farm_button.enable()
        else:
            self.acc_button.enable()
            self.farm_button.disable()


    def update_search_cats(self, search_text):
        """Run this function when the search text changes, or when the screen is switched to."""
        self.current_listed_cats = []
        Cat.sort_cats(self.all_cats_list)

        search_text = search_text.strip()
        if search_text not in [""]:
            for cat in self.all_cats_list:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = self.all_cats_list.copy()

        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )

        Cat.ordered_cat_list = self.current_listed_cats
        self.update_page()

    def exit_screen(self):
        self.selected_cat = None

        for ele in self.gardener_elements:
            self.gardener_elements[ele].kill()
        self.gardener_elements = {}

        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.gardeners = []
        self.back_button.kill()
        del self.back_button
        self.selected_frame_1.kill()
        del self.selected_frame_1
        self.selected_frame_2.kill()
        del self.selected_frame_2
        self.cat_bg.kill()
        del self.cat_bg
        self.acc_button.kill()
        del self.acc_button
        self.farm_button.kill()
        del self.farm_button
        self.last_med.kill()
        del self.last_med
        self.next_med.kill()
        del self.next_med
        self.deselect.kill()
        del self.deselect
        self.next_page.kill()
        del self.next_page
        self.previous_page.kill()
        del self.previous_page
        self.results.kill()
        del self.results
        self.random.kill()
        del self.random
        self.error.kill()
        del self.error
        self.search_bar_image.kill()
        del self.search_bar_image
        self.search_bar.kill()
        del self.search_bar
        self.garden.kill()
        del self.garden
        
        if self.selected_submenu is not None:
            self.acc_bonus_label.kill()
            del self.acc_bonus_label
            self.acc_bonus_dropdown.kill()
            del self.acc_bonus_dropdown
            self.accessory_label.kill()
            del self.accessory_label
            self.accessory_dropdown.kill()
            del self.accessory_dropdown
            self.craft_button.kill()
            del self.craft_button
            self.acc_preview.kill()
            del self.acc_preview

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

