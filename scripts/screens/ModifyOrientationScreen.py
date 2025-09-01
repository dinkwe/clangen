#!/usr/bin/env python3
# -*- coding: ascii -*-
from re import sub
from typing import Dict, Union

import i18n
import pygame
import pygame_gui
from pygame_gui.core import ObjectID, UIContainer
from pygame_gui.elements import UIDropDownMenu

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game
from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure.ui_elements import (
    UIImageButton,
    CatButton,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale_value,
    ui_scale_offset,
    event_text_adjust,
)
from scripts.utility import ui_scale
from .Screens import Screens
from ..game_structure.game.switches import switch_get_value, switch_set_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_button import get_button_dict, ButtonStyles


class ModifyOrientationScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.gendered_attraction_list = None
        self.sexuality_sexual_list = None
        self.sexuality_romantic_list = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.back_button = None
        self.the_cat = None
        self.selected_cat_elements = {}
        self.buttons = {}
        self.next_cat = None
        self.previous_cat = None
        self.elements: Dict[
            str,
            Union[
                pygame_gui.elements.UIPanel,
                pygame_gui.core.UIElement,
                pygame_gui.core.IContainerLikeInterface,
            ],
        ] = {}
        self.removalboxes_text = {}
        self.removalbuttons = {}
        self.deletebuttons = {}
        self.addbuttons = {}
        self.removalboxes_text = {}
        self.boxes = {}
        self.current_container = None
        self.saved_container = None
        self.subpage_dropdown = None
        self.subpage = "Gender preference"
        self.display_dict = {
            "fem": "Fem-aligned cats",
            "masc": "Masc-aligned cats",
            "neu/other": "Non-aligned cats",
            "straight": "Straight",
            "lesbian": "Lesbian",
            "sapphic": "Sapphic",
            "multisexual": "Multisexual",
            "bisexual": "Bisexual",
            "polysexual": "Polysexual",
            "bi-lesbian": "Bi-lesbian",
            "bi-sapphic": "Bi-sapphic",
            "femmesexual": "Femmesexual",
            "mascsexual": "Mascsexual",
            "neusexual": "Neusexual",
            "pan-lesbian": "Pan-lesbian",
            "pan-sapphic": "Pan-sapphic",
            "pansexual": "Pansexual",
            "omnisexual": "Omnisexual",
            "gay": "Gay",
            "achillean": "Achillean",
            "bi-gay": "Bi-gay",
            "bi-achillean": "Bi-achillean",
            "pan-gay": "Pan-gay",
            "pan-achillean": "Pan-achillean",
            "unlabeled": "Unlabeled",
            "heteroromantic": "Heteroromantic",
            "lesbiromantic": "Lesbiromantic",
            "multiromantic": "Multiromantic",
            "biromantic": "Biromantic",
            "polyromantic": "Polyromantic",
            "bi-lesbiromantic": "Bi-lesbiromantic",
            "femmeromantic": "Femmeromantic",
            "mascromantic": "Mascromantic",
            "neuromantic": "Neuromantic",
            "pan-lesbiromantic": "Pan-lesbiromantic",
            "panromantic": "Panromantic",
            "omniromantic": "Omniromantic",
            "homoromantic": "Homoromantic",
            "bi-homoromantic": "Bi-homoromantic",
            "pan-homoromantic": "Pan-homoromantic",
            "asexual": "Asexual",
            "demisexual": "Demisexual",
            "fraysexual": "Fraysexual",
            "graysexual": "Graysexual",
            "black stripe asexual": "Black stripe asexual",
            "aceflux": "Aceflux",
            "aromantic": "Aromantic",
            "demiromantic": "Demiromantic",
            "frayromantic": "Frayromantic",
            "grayromantic": "Grayromantic",
            "green stripe aromantic": "Green stripe aromantic",
            "aroflux": "Aroflux",
        }

    @staticmethod
    def create_dropdown(pos, size, options, selected_option, style=None):
        return UIDropDownMenu(
            options,
            selected_option,
            ui_scale(pygame.Rect(pos, size)),
            object_id=f"#{style}",
            manager=MANAGER
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    self.update_selected_cat()
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    self.update_selected_cat()
            elif type(event.ui_element) is CatButton:
                if event.ui_element.cat_id == "add":
                    if self.subpage == "Gender preference":
                        if event.ui_element.cat_object not in self.the_cat.sexuality["gender"]:
                            self.the_cat.sexuality["gender"].append(event.ui_element.cat_object)
                    elif self.subpage in ["Display (-sexual)", "Display (-romantic)"]:
                        if event.ui_element.cat_object not in self.the_cat.sexuality["display"]:
                            self.the_cat.sexuality["display"].append(event.ui_element.cat_object)

                elif event.ui_element.cat_id == "remove":
                    if self.subpage == "Gender preference":
                        if event.ui_element.cat_object in self.the_cat.sexuality["gender"]:
                            self.the_cat.sexuality["gender"].remove(event.ui_element.cat_object)
                    elif self.subpage in ["Display (-sexual)", "Display (-romantic)"]:
                        if event.ui_element.cat_object in self.the_cat.sexuality["display"] and len(self.the_cat.sexuality["display"]) > 1:
                            self.the_cat.sexuality["display"].remove(event.ui_element.cat_object)

                self.update_selected_cat()
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.subpage_dropdown:
                if get_clan_setting("sexuality labels") is True:
                    self.subpage = self.subpage_dropdown.selected_option[1]
                    self.update_selected_cat()
                else:
                    self.subpage = "Gender preference"
                    self.update_selected_cat()
        #

    def screen_switches(self):
        super().screen_switches()
        self.gendered_attraction_list = [
            "fem", "masc", "neu/other"
        ]
        self.sexuality_sexual_list = [
            "straight", "lesbian", "sapphic", "multisexual", "bisexual", "polysexual", "bi-lesbian", "bi-sapphic",
            "femmesexual", "mascsexual", "neusexual", "pan-lesbian", "pan-sapphic", "pansexual", "omnisexual", "gay",
            "achillean", "bi-gay", "bi-achillean", "pan-gay", "pan-achillean", "unlabeled", "asexual", "demisexual",
            "fraysexual", "graysexual", "black stripe asexual", "aceflux",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
        ]
        self.sexuality_sexual_list.sort()

        self.sexuality_romantic_list = [
            "heteroromantic", "lesbiromantic", "sapphic", "multiromantic", "biromantic", "polyromantic",
            "bi-lesbiromantic", "bi-sapphic", "femmeromantic", "mascromantic", "neuromantic", "pan-lesbiromantic",
            "pan-sapphic", "panromantic", "omniromantic", "homoromantic", "achillean", "bi-homoromantic",
            "bi-achillean", "pan-homoromantic", "pan-achillean", "unlabeled", "aromantic", "demiromantic",
            "frayromantic", "grayromantic", "green stripe aromantic", "aroflux",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
        ]
        self.sexuality_romantic_list.sort()

        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "buttons.next_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.previous_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.current_container = UIContainer(
            ui_scale(pygame.Rect((50, 285), (350, 335))),
            manager=MANAGER,
            starting_height=5,
        )

        self.saved_container = UIContainer(
            ui_scale(pygame.Rect((0, 285), (350, 335))),
            manager=MANAGER,
            starting_height=5,
            anchors={"left": "left", "left_target": self.current_container},
        )

        self.update_selected_cat()
        self.set_cat_location_bg(self.the_cat)

    def update_selected_cat(self):
        self.reset_buttons_and_boxes()

        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        if not self.the_cat:
            return

        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 100), (699, 520))),
            pygame.transform.scale(
                pygame.image.load(
                    "resources/images/gender_framing.png"
                ).convert_alpha(),
                ui_scale_dimensions((699, 520)),
            ),
            manager=MANAGER,
        )
        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((180, 105), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        self.selected_cat_elements["header"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 62), (425, 37))),
            f"Change {self.the_cat.name}'s Orientation",
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            anchors={"centerx": "centerx"},
        )

        current_tab_blurb = "Choose "
        if self.subpage == "Gender preference":
            current_tab_blurb += "which genders m_c is attracted to."
        elif self.subpage in ["Display (-sexual)", "Display (-romantic)"]:
            current_tab_blurb += "how m_c's sexuality displays on {PRONOUN/m_c/poss} profile.\nThis does not affect gameplay."
        else:
            current_tab_blurb += "ERROR"
        current_tab_blurb = event_text_adjust(Cat, text=current_tab_blurb, main_cat=self.the_cat)

        self.selected_cat_elements["description"] = pygame_gui.elements.UITextBox(
            str(current_tab_blurb),
            ui_scale(pygame.Rect((332, 132), (290, 75))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
        )

        self.subpage_dropdown = self.create_dropdown(
            pos=(342, 239),
            size=(276, 40),
            options=[
                "Gender preference",
                "Display (-sexual)",
                "Display (-romantic)"
            ],
            selected_option=self.subpage,
            style="dropup",
        )
        if get_clan_setting("sexuality labels") is False:
            self.subpage_dropdown.hide()

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()
        self.pronoun_update()
        self.preset_update()
        self.update_previous_next_cat_buttons()

    def pronoun_update(self):
        insert = ""
        if self.subpage == "Gender preference":
            insert = f"{self.subpage.lower()}{'s' if len(self.the_cat.sexuality['gender']) > 1 else ''}"
        elif self.subpage in ["Display (-sexual)", "Display (-romantic)"]:
            insert = "sexuality"
        num = 250

        self.removalboxes_text["instr"] = pygame_gui.elements.UITextBox(
            f"Current {insert}",
            ui_scale(pygame.Rect((0, 10), (num, 55))),
            object_id=ObjectID("#text_box_34_horizcenter", "#dark"),
            manager=MANAGER,
            container=self.current_container,
            anchors={"centerx": "centerx"},
        )

        if self.subpage == "Gender preference":
            # List the various prefs
            self.removalboxes_text[
                "container_general"
            ] = pygame_gui.elements.UIScrollingContainer(
                ui_scale(pygame.Rect((0, 5), (337, 270))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
                allow_scroll_x=False,
                container=self.current_container,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.removalboxes_text["instr"],
                },
            )
            pronoun_frame = "resources/images/pronoun_frame.png"
            n = 0
            for pref in self.the_cat.sexuality["gender"]:
                display_name = self.display_dict.get(pref)
                short_name = shorten_text_to_fit(display_name, 170, 13)

                # Create block for each pref
                block_rect = ui_scale(pygame.Rect((0, 0), (272, 45)))
                self.elements[f"cat_gender_prefs_{n}"] = pygame_gui.elements.UIPanel(
                    block_rect,
                    container=self.removalboxes_text["container_general"],
                    manager=MANAGER,
                    anchors=(
                        {
                            "centerx": "centerx",
                            "top_target": self.elements[f"cat_gender_prefs_{n - 1}"],
                        }
                        if n > 0
                        else {"centerx": "centerx"}
                    ),
                    margins={"left": 0, "right": 0, "top": ui_scale_value(2), "bottom": 0},
                )
                self.elements[
                    f"cat_gender_prefs_{n}"
                ].background_image = pygame.transform.scale(
                    pygame.image.load(pronoun_frame).convert_alpha(),
                    ui_scale_dimensions((272, 44)),
                )
                self.elements[f"cat_gender_prefs_{n}"].rebuild()

                # Create remove button
                button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
                button_rect.topright = ui_scale_offset((-10, 0))
                self.removalbuttons[f"cat_gender_prefs_{n}"] = CatButton(
                    button_rect,
                    "",
                    cat_object=pref,
                    cat_id="remove",
                    container=self.elements[f"cat_gender_prefs_{n}"],
                    object_id="#exit_window_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={"centery": "centery", "right": "right"},
                )

                # Create UITextBox for pref display with clickable remove button
                text_box_rect = ui_scale(pygame.Rect((-20, 0), (200, -1)))
                self.removalboxes_text[f"cat_gender_prefs_{n}"] = pygame_gui.elements.UITextBox(
                    short_name,
                    text_box_rect,
                    container=self.elements[f"cat_gender_prefs_{n}"],
                    object_id="#text_box_30_horizleft_pad_0_8",
                    manager=MANAGER,
                    anchors={"center": "center"},
                )

                # check if the pref text had to be shortened, if it did then create a tooltip containing full
                # pref text
                self.buttons[f"{n}_tooltip_cat_gender_prefs"] = UIImageButton(
                    self.removalboxes_text[f"cat_gender_prefs_{n}"].rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.elements[f"cat_gender_prefs_{n}"],
                    tool_tip_text=display_name if short_name != display_name else None,
                    manager=MANAGER,
                    starting_height=2,
                )

                n += 1

            min_scrollable_height = ui_scale_value(max(100, n * 65))

            self.removalboxes_text["container_general"].set_scrollable_area_dimensions(
                ui_scale_dimensions((310, min_scrollable_height))
            )
        elif self.subpage == "Display (-sexual)":
            # List the various prefs
            self.removalboxes_text[
                "container_general"
            ] = pygame_gui.elements.UIScrollingContainer(
                ui_scale(pygame.Rect((0, 5), (337, 270))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
                allow_scroll_x=False,
                container=self.current_container,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.removalboxes_text["instr"],
                },
            )
            pronoun_frame = "resources/images/pronoun_frame.png"
            n = 0
            for sexuality in self.the_cat.sexuality["display"]:
                if sexuality in self.sexuality_romantic_list:
                    if sexuality not in ["sapphic", "bi-sapphic", "pan-sapphic", "achillean", "bi-achillean",
                                         "pan-achillean", "unlabeled"]:
                        continue

                display_name = self.display_dict.get(sexuality)
                short_name = shorten_text_to_fit(display_name, 170, 13)

                # Create block for each sexuality
                block_rect = ui_scale(pygame.Rect((0, 0), (272, 45)))
                self.elements[f"cat_sexuality_sexual_{n}"] = pygame_gui.elements.UIPanel(
                    block_rect,
                    container=self.removalboxes_text["container_general"],
                    manager=MANAGER,
                    anchors=(
                        {
                            "centerx": "centerx",
                            "top_target": self.elements[f"cat_sexuality_sexual_{n - 1}"],
                        }
                        if n > 0
                        else {"centerx": "centerx"}
                    ),
                    margins={"left": 0, "right": 0, "top": ui_scale_value(2), "bottom": 0},
                )
                self.elements[
                    f"cat_sexuality_sexual_{n}"
                ].background_image = pygame.transform.scale(
                    pygame.image.load(pronoun_frame).convert_alpha(),
                    ui_scale_dimensions((272, 44)),
                )
                self.elements[f"cat_sexuality_sexual_{n}"].rebuild()

                # Create remove button
                button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
                button_rect.topright = ui_scale_offset((-10, 0))
                self.removalbuttons[f"cat_sexuality_sexual_{n}"] = CatButton(
                    button_rect,
                    "",
                    cat_object=sexuality,
                    cat_id="remove",
                    container=self.elements[f"cat_sexuality_sexual_{n}"],
                    object_id="#exit_window_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={"centery": "centery", "right": "right"},
                )

                # Create UITextBox for sexuality display with clickable remove button
                text_box_rect = ui_scale(pygame.Rect((-20, 0), (200, -1)))
                self.removalboxes_text[f"cat_sexuality_sexual_{n}"] = pygame_gui.elements.UITextBox(
                    short_name,
                    text_box_rect,
                    container=self.elements[f"cat_sexuality_sexual_{n}"],
                    object_id="#text_box_30_horizleft_pad_0_8",
                    manager=MANAGER,
                    anchors={"center": "center"},
                )

                # check if the sexuality text had to be shortened, if it did then create a tooltip containing full
                # sexuality text
                self.buttons[f"{n}_tooltip_cat_sexuality_sexual"] = UIImageButton(
                    self.removalboxes_text[f"cat_sexuality_sexual_{n}"].rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.elements[f"cat_sexuality_sexual_{n}"],
                    tool_tip_text=display_name if short_name != display_name else None,
                    manager=MANAGER,
                    starting_height=2,
                )

                n += 1

            # Disable removing is a cat has only one sexuality.
            if n == 1:
                for button_id in self.removalbuttons:
                    self.removalbuttons[button_id].disable()

            min_scrollable_height = ui_scale_value(max(100, n * 65))

            self.removalboxes_text["container_general"].set_scrollable_area_dimensions(
                ui_scale_dimensions((310, min_scrollable_height))
            )
        elif self.subpage == "Display (-romantic)":
            if len(self.the_cat.sexuality["display"]) == 1:
                temp = self.the_cat.sexuality["display"][0]
                temp = temp.replace("straight", "heteroromantic")
                temp = temp.replace("lesbian", "lesbiromantic")
                temp = temp.replace("gay", "homoromantic")
                temp = temp.replace("ace", "aro")
                temp = temp.replace("sexual", "romantic")
                romantic_list = [temp]
                temp_turned_on = True
            else:
                romantic_list = self.the_cat.sexuality["display"].copy()
                temp_turned_on = False

            # List the various sexualities
            self.removalboxes_text[
                "container_general"
            ] = pygame_gui.elements.UIScrollingContainer(
                ui_scale(pygame.Rect((0, 5), (337, 270))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
                allow_scroll_x=False,
                container=self.current_container,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.removalboxes_text["instr"],
                },
            )
            pronoun_frame = "resources/images/pronoun_frame.png"
            n = 0
            for sexuality in romantic_list:
                if sexuality in self.sexuality_sexual_list:
                    if sexuality not in ["sapphic", "bi-sapphic", "pan-sapphic", "achillean", "bi-achillean",
                                         "pan-achillean", "unlabeled"]:
                        continue

                display_name = self.display_dict.get(sexuality)
                short_name = shorten_text_to_fit(display_name, 170, 13)

                # Create block for each sexuality
                block_rect = ui_scale(pygame.Rect((0, 0), (272, 45)))
                self.elements[f"cat_sexuality_romantic_{n}"] = pygame_gui.elements.UIPanel(
                    block_rect,
                    container=self.removalboxes_text["container_general"],
                    manager=MANAGER,
                    anchors=(
                        {
                            "centerx": "centerx",
                            "top_target": self.elements[f"cat_sexuality_romantic_{n - 1}"],
                        }
                        if n > 0
                        else {"centerx": "centerx"}
                    ),
                    margins={"left": 0, "right": 0, "top": ui_scale_value(2), "bottom": 0},
                )
                self.elements[
                    f"cat_sexuality_romantic_{n}"
                ].background_image = pygame.transform.scale(
                    pygame.image.load(pronoun_frame).convert_alpha(),
                    ui_scale_dimensions((272, 44)),
                )
                self.elements[f"cat_sexuality_romantic_{n}"].rebuild()

                # Create remove button
                button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
                button_rect.topright = ui_scale_offset((-10, 0))
                self.removalbuttons[f"cat_sexuality_romantic_{n}"] = CatButton(
                    button_rect,
                    "",
                    cat_object=sexuality,
                    cat_id="remove",
                    container=self.elements[f"cat_sexuality_romantic_{n}"],
                    object_id="#exit_window_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={"centery": "centery", "right": "right"},
                )

                # Create UITextBox for sexuality display with clickable remove button
                text_box_rect = ui_scale(pygame.Rect((-20, 0), (200, -1)))
                self.removalboxes_text[f"cat_sexuality_romantic_{n}"] = pygame_gui.elements.UITextBox(
                    short_name,
                    text_box_rect,
                    container=self.elements[f"cat_sexuality_romantic_{n}"],
                    object_id="#text_box_30_horizleft_pad_0_8",
                    manager=MANAGER,
                    anchors={"center": "center"},
                )

                # check if the sexuality text had to be shortened, if it did then create a tooltip containing full
                # sexuality text
                self.buttons[f"{n}_tooltip_cat_sexuality_romantic"] = UIImageButton(
                    self.removalboxes_text[f"cat_sexuality_romantic_{n}"].rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.elements[f"cat_sexuality_romantic_{n}"],
                    tool_tip_text=display_name if short_name != display_name else None,
                    manager=MANAGER,
                    starting_height=2,
                )

                n += 1

            # Disable removing if a cat doesn't have a romantic orientation.
            if temp_turned_on:
                for button_id in self.removalbuttons:
                    self.removalbuttons[button_id].disable()

            min_scrollable_height = ui_scale_value(max(100, n * 65))

            self.removalboxes_text["container_general"].set_scrollable_area_dimensions(
                ui_scale_dimensions((310, min_scrollable_height))
            )
        #

    def preset_update(self):
        insert = ""
        if self.subpage == "Gender preference":
            insert = self.subpage.lower() + "s"
        elif self.subpage in ["Display (-sexual)", "Display (-romantic)"]:
            insert = "sexualities"
        num = 225

        self.removalboxes_text["instr2"] = pygame_gui.elements.UITextBox(
            f"All {insert}",
            ui_scale(pygame.Rect((0, 10), (num, 55))),
            object_id=ObjectID("#text_box_34_horizleft", "#dark"),
            manager=MANAGER,
            container=self.saved_container,
            anchors={"centerx": "centerx"},
        )

        if self.subpage == "Gender preference":
            # List the various prefs
            self.removalboxes_text[
                "container_general2"
            ] = pygame_gui.elements.UIScrollingContainer(
                relative_rect=ui_scale(pygame.Rect((0, 5), (337, 270))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
                allow_scroll_x=False,
                container=self.saved_container,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.removalboxes_text["instr2"],
                },
            )

            n = 0
            pronoun_frame = "resources/images/pronoun_frame.png"

            for pref in self.gendered_attraction_list:
                display_name = self.display_dict.get(pref)
                short_name = shorten_text_to_fit(display_name, 140, 13)

                dict_name_core = f"default_gender_prefs_{n}"

                # Create block for each pref
                block_rect = ui_scale(pygame.Rect((0, 0), (272, 45)))
                self.elements[f"{n}"] = pygame_gui.elements.UIPanel(
                    block_rect,
                    container=self.removalboxes_text["container_general2"],
                    manager=MANAGER,
                    anchors=(
                        {
                            "centerx": "centerx",
                            "top_target": self.elements[f"{n - 1}"],
                        }
                        if n > 0
                        else {"centerx": "centerx"}
                    ),
                    margins={"left": 0, "right": 0, "top": ui_scale_value(2), "bottom": 0},
                )
                self.elements[f"{n}"].background_image = pygame.transform.scale(
                    pygame.image.load(pronoun_frame).convert_alpha(),
                    ui_scale_dimensions((272, 44)),
                )
                self.elements[f"{n}"].rebuild()

                # Create remove button for each pref with dynamic ycoor
                button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
                button_rect.topright = ui_scale_offset((-10, 0))
                self.deletebuttons[dict_name_core] = CatButton(
                    button_rect,
                    "",
                    cat_object=pref,
                    cat_id="delete",
                    container=self.elements[f"{n}"],
                    object_id="#exit_window_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={"centery": "centery", "right": "right"},
                )
                self.deletebuttons[dict_name_core].disable()

                # the "add" button
                button_rect = ui_scale(pygame.Rect((0, 0), (56, 28)))
                button_rect.topright = ui_scale_dimensions((-5, 0))
                # TODO: update this to use UISurfaceImageButton
                self.addbuttons[dict_name_core] = CatButton(
                    button_rect,
                    "",
                    cat_object=pref,
                    cat_id="add",
                    container=self.elements[f"{n}"],
                    object_id="#add_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={
                        "centery": "centery",
                        "right": "right",
                        "right_target": self.deletebuttons[dict_name_core],
                    },
                )

                if pref in self.the_cat.sexuality["gender"]:
                    self.addbuttons[dict_name_core].disable()

                # Create UITextBox for pref display and create tooltip for full pref display
                self.removalboxes_text[dict_name_core] = pygame_gui.elements.UITextBox(
                    short_name,
                    ui_scale(pygame.Rect((-20, 0), (200, -1))),
                    container=self.elements[f"{n}"],
                    object_id="#text_box_30_horizleft_pad_0_8",
                    manager=MANAGER,
                    anchors={"center": "center"},
                )

                self.removalboxes_text[dict_name_core].disable()

                # check if the pref text had to be shortened, if it did then create a tooltip containing full
                # pref text
                self.buttons["tooltip_" + dict_name_core] = UIImageButton(
                    self.removalboxes_text[dict_name_core].rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.elements[f"{n}"],
                    tool_tip_text=display_name if short_name != display_name else None,
                    manager=MANAGER,
                    starting_height=2,
                )

                n += 1

            min_scrollable_height = max(100, n * 65)

            self.removalboxes_text["container_general2"].set_scrollable_area_dimensions(
                (
                    self.removalboxes_text["container_general2"].rect[2],
                    ui_scale_value(min_scrollable_height),
                ),
            )
        elif self.subpage == "Display (-sexual)":
            # List the various sexualities
            self.removalboxes_text[
                "container_general2"
            ] = pygame_gui.elements.UIScrollingContainer(
                relative_rect=ui_scale(pygame.Rect((0, 5), (337, 270))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
                allow_scroll_x=False,
                container=self.saved_container,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.removalboxes_text["instr2"],
                },
            )

            n = 0
            pronoun_frame = "resources/images/pronoun_frame.png"

            for sexuality in self.sexuality_sexual_list:
                display_name = self.display_dict.get(sexuality)
                short_name = shorten_text_to_fit(display_name, 140, 13)

                dict_name_core = f"default_sexuality_sexual_{n}"

                # Create block for each sexuality
                block_rect = ui_scale(pygame.Rect((0, 0), (272, 45)))
                self.elements[f"{n}"] = pygame_gui.elements.UIPanel(
                    block_rect,
                    container=self.removalboxes_text["container_general2"],
                    manager=MANAGER,
                    anchors=(
                        {
                            "centerx": "centerx",
                            "top_target": self.elements[f"{n - 1}"],
                        }
                        if n > 0
                        else {"centerx": "centerx"}
                    ),
                    margins={"left": 0, "right": 0, "top": ui_scale_value(2), "bottom": 0},
                )
                self.elements[f"{n}"].background_image = pygame.transform.scale(
                    pygame.image.load(pronoun_frame).convert_alpha(),
                    ui_scale_dimensions((272, 44)),
                )
                self.elements[f"{n}"].rebuild()

                # Create remove button for each sexuality with dynamic ycoor
                button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
                button_rect.topright = ui_scale_offset((-10, 0))
                self.deletebuttons[dict_name_core] = CatButton(
                    button_rect,
                    "",
                    cat_object=sexuality,
                    cat_id="delete",
                    container=self.elements[f"{n}"],
                    object_id="#exit_window_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={"centery": "centery", "right": "right"},
                )
                self.deletebuttons[dict_name_core].disable()

                # the "add" button
                button_rect = ui_scale(pygame.Rect((0, 0), (56, 28)))
                button_rect.topright = ui_scale_dimensions((-5, 0))
                # TODO: update this to use UISurfaceImageButton
                self.addbuttons[dict_name_core] = CatButton(
                    button_rect,
                    "",
                    cat_object=sexuality,
                    cat_id="add",
                    container=self.elements[f"{n}"],
                    object_id="#add_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={
                        "centery": "centery",
                        "right": "right",
                        "right_target": self.deletebuttons[dict_name_core],
                    },
                )

                if sexuality in self.the_cat.sexuality["display"]:
                    self.addbuttons[dict_name_core].disable()

                # Create UITextBox for sexuality display and create tooltip for full sexuality display
                self.removalboxes_text[dict_name_core] = pygame_gui.elements.UITextBox(
                    short_name,
                    ui_scale(pygame.Rect((-20, 0), (200, -1))),
                    container=self.elements[f"{n}"],
                    object_id="#text_box_30_horizleft_pad_0_8",
                    manager=MANAGER,
                    anchors={"center": "center"},
                )

                self.removalboxes_text[dict_name_core].disable()

                # check if the sexuality text had to be shortened, if it did then create a tooltip containing full
                # sexuality text
                self.buttons["tooltip_" + dict_name_core] = UIImageButton(
                    self.removalboxes_text[dict_name_core].rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.elements[f"{n}"],
                    tool_tip_text=display_name if short_name != display_name else None,
                    manager=MANAGER,
                    starting_height=2,
                )

                n += 1

            min_scrollable_height = max(100, n * 65)

            self.removalboxes_text["container_general2"].set_scrollable_area_dimensions(
                (
                    self.removalboxes_text["container_general2"].rect[2],
                    ui_scale_value(min_scrollable_height),
                ),
            )
        elif self.subpage == "Display (-romantic)":
            # List the various sexualities
            self.removalboxes_text[
                "container_general2"
            ] = pygame_gui.elements.UIScrollingContainer(
                relative_rect=ui_scale(pygame.Rect((0, 5), (337, 270))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
                allow_scroll_x=False,
                container=self.saved_container,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.removalboxes_text["instr2"],
                },
            )

            n = 0
            pronoun_frame = "resources/images/pronoun_frame.png"

            for sexuality in self.sexuality_romantic_list:
                display_name = self.display_dict.get(sexuality)
                short_name = shorten_text_to_fit(display_name, 140, 13)

                dict_name_core = f"default_sexuality_romantic_{n}"

                # Create block for each sexuality
                block_rect = ui_scale(pygame.Rect((0, 0), (272, 45)))
                self.elements[f"{n}"] = pygame_gui.elements.UIPanel(
                    block_rect,
                    container=self.removalboxes_text["container_general2"],
                    manager=MANAGER,
                    anchors=(
                        {
                            "centerx": "centerx",
                            "top_target": self.elements[f"{n - 1}"],
                        }
                        if n > 0
                        else {"centerx": "centerx"}
                    ),
                    margins={"left": 0, "right": 0, "top": ui_scale_value(2), "bottom": 0},
                )
                self.elements[f"{n}"].background_image = pygame.transform.scale(
                    pygame.image.load(pronoun_frame).convert_alpha(),
                    ui_scale_dimensions((272, 44)),
                )
                self.elements[f"{n}"].rebuild()

                # Create remove button for each sexuality with dynamic ycoor
                button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
                button_rect.topright = ui_scale_offset((-10, 0))
                self.deletebuttons[dict_name_core] = CatButton(
                    button_rect,
                    "",
                    cat_object=sexuality,
                    cat_id="delete",
                    container=self.elements[f"{n}"],
                    object_id="#exit_window_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={"centery": "centery", "right": "right"},
                )
                self.deletebuttons[dict_name_core].disable()

                # the "add" button
                button_rect = ui_scale(pygame.Rect((0, 0), (56, 28)))
                button_rect.topright = ui_scale_dimensions((-5, 0))
                # TODO: update this to use UISurfaceImageButton
                self.addbuttons[dict_name_core] = CatButton(
                    button_rect,
                    "",
                    cat_object=sexuality,
                    cat_id="add",
                    container=self.elements[f"{n}"],
                    object_id="#add_button",
                    starting_height=2,
                    manager=MANAGER,
                    anchors={
                        "centery": "centery",
                        "right": "right",
                        "right_target": self.deletebuttons[dict_name_core],
                    },
                )

                if sexuality in self.the_cat.sexuality["display"]:
                    self.addbuttons[dict_name_core].disable()

                # Create UITextBox for sexuality display and create tooltip for full sexuality display
                self.removalboxes_text[dict_name_core] = pygame_gui.elements.UITextBox(
                    short_name,
                    ui_scale(pygame.Rect((-20, 0), (200, -1))),
                    container=self.elements[f"{n}"],
                    object_id="#text_box_30_horizleft_pad_0_8",
                    manager=MANAGER,
                    anchors={"center": "center"},
                )

                self.removalboxes_text[dict_name_core].disable()

                # check if the sexuality text had to be shortened, if it did then create a tooltip containing full
                # sexuality text
                self.buttons["tooltip_" + dict_name_core] = UIImageButton(
                    self.removalboxes_text[dict_name_core].rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.elements[f"{n}"],
                    tool_tip_text=display_name if short_name != display_name else None,
                    manager=MANAGER,
                    starting_height=2,
                )

                n += 1

            min_scrollable_height = max(100, n * 65)

            self.removalboxes_text["container_general2"].set_scrollable_area_dimensions(
                (
                    self.removalboxes_text["container_general2"].rect[2],
                    ui_scale_value(min_scrollable_height),
                ),
            )
        #

    def reset_buttons_and_boxes(self):
        # kills everything when switching cats
        for ele in self.elements:
            self.elements[ele].kill()
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        for ele in self.buttons:
            self.buttons[ele].kill()
        for ele in self.removalboxes_text:
            self.removalboxes_text[ele].kill()
        for ele in self.removalbuttons:
            self.removalbuttons[ele].kill()
        for ele in self.deletebuttons:
            self.deletebuttons[ele].kill()
        for ele in self.addbuttons:
            self.addbuttons[ele].kill()
        try:
            self.subpage_dropdown.kill()
        except AttributeError:
            pass

        self.selected_cat_elements = {}
        self.removalboxes_text = {}
        self.addbuttons = {}
        self.elements = {}
        self.removalbuttons = {}
        self.deletebuttons = {}

    def exit_screen(self):
        # kill everything
        self.back_button.kill()
        del self.back_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.elements["cat_frame"].kill()
        del self.elements["cat_frame"]
        self.subpage_dropdown.kill()
        del self.subpage_dropdown

        self.current_container.kill()
        self.saved_container.kill()
        self.reset_buttons_and_boxes()
