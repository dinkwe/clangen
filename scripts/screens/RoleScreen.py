#!/usr/bin/env python3
# -*- coding: ascii -*-
import os

import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.cat.enums import CatAgeEnum
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UITextBoxTweaked,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale,
    adjust_list_text,
)
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles


class RoleScreen(Screens):
    the_cat = None
    selected_cat_elements = {}
    buttons = {}
    next_cat = None
    previous_cat = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.update_selected_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_selected_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.promote_leader:
                if self.the_cat == game.clan.deputy:
                    game.clan.deputy = None
                game.clan.new_leader(self.the_cat)
                if game.sort_type == "rank":
                    Cat.sort_cats()
                self.update_selected_cat()
            elif event.ui_element == self.promote_deputy:
                game.clan.deputy = self.the_cat
                self.the_cat.status_change("deputy", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_warrior:
                self.the_cat.status_change("warrior", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_med_cat:
                self.the_cat.status_change("medicine cat", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.retire:
                self.the_cat.status_change("elder", resort=True)
                # Since you can't "unretire" a cat, apply the skill and trait change
                # here
                self.update_selected_cat()
            elif event.ui_element == self.switch_mediator:
                self.the_cat.status_change("mediator", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_caretaker:
                self.the_cat.status_change("caretaker", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_denkeeper:
                self.the_cat.status_change("denkeeper", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_messenger:
                self.the_cat.status_change("messenger", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_gardener:
                self.the_cat.status_change("gardener", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_storyteller:
                self.the_cat.status_change("storyteller", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_warrior_app:
                self.the_cat.status_change("apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_med_app:
                self.the_cat.status_change("medicine cat apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_mediator_app:
                self.the_cat.status_change("mediator apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_caretaker_app:
                self.the_cat.status_change("caretaker apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_denkeeper_app:
                self.the_cat.status_change("denkeeper apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_messenger_app:
                self.the_cat.status_change("messenger apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_gardener_app:
                self.the_cat.status_change("gardener apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_storyteller_app:
                self.the_cat.status_change("storyteller apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.rekit:
                self.the_cat.status_change("kitten", resort=True)
                self.update_selected_cat()

        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if event.key == pygame.K_ESCAPE:
                self.change_screen("profile screen")
            elif event.key == pygame.K_RIGHT:
                game.switches["cat"] = self.next_cat
                self.update_selected_cat()
            elif event.key == pygame.K_LEFT:
                game.switches["cat"] = self.previous_cat
                self.update_selected_cat()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

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

        # Create the buttons
        self.bar = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((48, 350), (704, 10))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/bar.png"),
                ui_scale_dimensions((704, 10)),
            ),
            manager=MANAGER,
        )

        self.blurb_background = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 195), (700, 150))),
            get_box(BoxStyles.ROUNDED_BOX, (700, 150)),
        )

        # PROMOTION AND DEMOTION
        self.promote_leader = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "screens.role.promote_leader",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_top",
            anchors={"top_target": self.bar},
        )
        self.promote_deputy = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "screens.role.promote_deputy",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.promote_leader},
        )
        self.retire = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "screens.role.retire",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.promote_deputy},
        )
        self.rekit = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "screens.role.rekit",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.retire},
        )

        # WARRIOR ROLES
        self.switch_warrior = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 36))),
            "screens.role.switch_warrior",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
        )
        self.switch_denkeeper = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 36))),
            "screens.role.switch_denkeeper",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_warrior},
        )
        self.switch_messenger = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 36))),
            "screens.role.switch_messenger",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_denkeeper},
        )
        self.switch_warrior_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 52))),
            "screens.role.switch_app",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_messenger},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_denkeeper_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 52))),
            "screens.role.switch_denkeeper_app",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_warrior_app},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_messenger_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 52))),
            "screens.role.switch_messenger_app",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_denkeeper_app},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )

        #HEALER ROLES
        self.switch_med_cat = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 52))),
            "screens.role.switch_medicine_cat",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_caretaker = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 36))),
            "screens.role.switch_caretaker",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_med_cat},
        )
        self.switch_gardener = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 36))),
            "screens.role.switch_gardener",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_caretaker},
        )
        self.switch_med_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 52))),
            "screens.role.switch_medcat_app",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_gardener},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_caretaker_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 52))),
            "screens.role.switch_caretaker_app",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_med_app},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_gardener_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 52))),
            "screens.role.switch_gardener_app",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_caretaker_app},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )

        #SOCIAL ROLES
        self.switch_mediator = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 36))),
            "screens.role.switch_mediator",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
        )
        self.switch_storyteller = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 36))),
            "screens.role.switch_storyteller",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_mediator},
        )
        self.switch_mediator_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 52))),
            "screens.role.switch_mediator_app",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_storyteller},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_storyteller_app = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 52))),
            "screens.role.switch_storyteller_app",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_mediator_app},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )

        self.update_selected_cat()

    def update_selected_cat(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.the_cat = Cat.fetch_cat(game.switches["cat"])
        if not self.the_cat:
            return

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((245, 40), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 150, 13)
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((387, 70), (175, -1))),
            short_name,
            object_id=get_text_box_theme("#text_box_30"),
        )
        
        trait_text = i18n.t(f"cat.personality.{self.the_cat.personality.trait}")
        if self.the_cat.personality.trait != self.the_cat.personality.trait2:
            trait_text += " & " + i18n.t(f"cat.personality.{self.the_cat.personality.trait2}")
        text = [
            "<b>" + i18n.t(f"general.{self.the_cat.status}", count=1) + "</b>",
            trait_text,
            i18n.t("general.moons_age", count=self.the_cat.moons)
            + "  |  "
            + self.the_cat.genderalign,
        ]

        if self.the_cat.mentor:
            mentor = Cat.fetch_cat(self.the_cat.mentor)
            text.append(
                i18n.t(
                    "general.mentor_label",
                    mentor=mentor.name if mentor else i18n.t("general.none"),
                )
            )

        if self.the_cat.apprentice:
            apprentices = adjust_list_text(
                [
                    str(Cat.fetch_cat(x).name)
                    for x in self.the_cat.apprentice
                    if Cat.fetch_cat(x)
                ]
            )
            text.append(
                i18n.t(
                    "general.apprentice_label",
                    count=len(self.the_cat.apprentice),
                    apprentices=apprentices,
                )
            )

        self.selected_cat_elements["cat_details"] = UITextBoxTweaked(
            "\n".join(text),
            ui_scale(pygame.Rect((395, 100), (160, 94))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            manager=MANAGER,
            line_spacing=0.95,
        )

        self.selected_cat_elements["role_blurb"] = pygame_gui.elements.UITextBox(
            self.get_role_blurb(),
            ui_scale(pygame.Rect((170, 200), (560, 135))),
            object_id="#text_box_26_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        main_dir = "resources/images/"
        paths = {
            "leader": "leader_icon.png",
            "deputy": "deputy_icon.png",
            "medicine cat": "medic_icon.png",
            "medicine cat apprentice": "medic_app_icon.png",
            "mediator": "mediator_icon.png",
            "mediator apprentice": "mediator_app_icon.png",
            "warrior": "warrior_icon.png",
            "apprentice": "warrior_app_icon.png",
            "kitten": "kit_icon.png",
            "newborn": "kit_icon.png",
            "elder": "elder_icon.png",
            "caretaker": "care_icon.png",
            "caretaker apprentice": "care_app_icon.png",
            "messenger": "messenger_icon.png",
            "messenger apprentice": "messenger_app_icon.png",
            "denkeeper": "denkeeper_icon.png",
            "denkeeper apprentice": "denkeeper_app_icon.png",
            "gardener": "gardener_icon.png",
            "gardener apprentice": "garden_app_icon.png",
            "storyteller": "story_icon.png",
            "storyteller apprentice": "story_app_icon.png",
        }

        if self.the_cat.status in paths:
            icon_path = os.path.join(main_dir, paths[self.the_cat.status])
        else:
            icon_path = os.path.join(main_dir, "buttonrank.png")

        self.selected_cat_elements["role_icon"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((82, 231), (78, 78))),
            pygame.transform.scale(
                image_cache.load_image(icon_path),
                ui_scale_dimensions((78, 78)),
            ),
        )

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()
        self.update_disabled_buttons()

    def update_disabled_buttons(self):

        self.update_previous_next_cat_buttons()

        if game.clan.leader:
            leader_invalid = game.clan.leader.dead or game.clan.leader.outside
        else:
            leader_invalid = True

        if game.clan.deputy:
            deputy_invalid = game.clan.deputy.dead or game.clan.deputy.outside
        else:
            deputy_invalid = True
            
        #start by disabling all
        self.promote_leader.disable()
        self.promote_deputy.disable()
        
        self.switch_warrior.disable()
        self.switch_med_cat.disable()
        self.switch_mediator.disable()
        self.switch_caretaker.disable()
        self.switch_messenger.disable()
        self.switch_denkeeper.disable()
        self.switch_gardener.disable()
        self.switch_storyteller.disable()
        self.retire.disable()
        self.rekit.disable()
        
        self.switch_med_app.disable()
        self.switch_warrior_app.disable()
        self.switch_mediator_app.disable()
        self.switch_caretaker_app.disable()
        self.switch_messenger_app.disable()
        self.switch_denkeeper_app.disable()
        self.switch_gardener_app.disable()
        self.switch_storyteller_app.disable()

        #first check for training
        if self.the_cat.status in ["apprentice", "medicine cat apprentice", "mediator apprentice", "denkeeper apprentice", "caretaker apprentice", "messenger apprentice", "storyteller apprentice", "gardener apprentice"]:
            
            #ENABLE ALL TRAININGS
            self.switch_med_app.enable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.enable()
            self.switch_caretaker_app.enable()
            self.switch_messenger_app.enable()
            self.switch_denkeeper_app.enable()
            self.switch_gardener_app.enable()
            self.switch_storyteller_app.enable()
            self.rekit.enable()
            
            if self.the_cat.status == "apprentice":
                self.switch_warrior_app.disable(),self.switch_warrior.enable()
            elif self.the_cat.status == "medicine cat apprentice":
                self.switch_med_app.disable(),self.switch_med_cat.enable()
            elif self.the_cat.status == "mediator apprentice":
                self.switch_mediator_app.disable(),self.switch_mediator.enable()
            elif self.the_cat.status == "caretaker apprentice":
                self.switch_caretaker_app.disable(),self.switch_caretaker.enable()
            elif self.the_cat.status == "messenger apprentice":
                self.switch_messenger_app.disable(),self.switch_messenger.enable()
            elif self.the_cat.status == "denkeeper apprentice":
                self.switch_denkeeper_app.disable(),self.switch_denkeeper.enable()
            elif self.the_cat.status == "gardener apprentice":
                self.switch_gardener_app.disable(),self.switch_gardener.enable()
            elif self.the_cat.status == "storyteller apprentice":
                self.switch_storyteller_app.disable(),self.switch_storyteller.enable()
        #next we check if they're a kit
        elif self.the_cat.status in ["kitten"]:
            #ENABLE ALL TRAININGS
            self.switch_med_app.enable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.enable()
            self.switch_caretaker_app.enable()
            self.switch_messenger_app.enable()
            self.switch_denkeeper_app.enable()
            self.switch_gardener_app.enable()
            self.switch_storyteller_app.enable()
            self.rekit.disable()
    
        #now we check for leader/deputy eligible roles
        elif self.the_cat.status in ["elder","warrior", "mediator", "messenger", "caretaker", "denkeeper", "storyteller", "gardener"]:
            if leader_invalid:
                self.promote_leader.enable()

            if deputy_invalid:
                self.promote_deputy.enable()
            
            self.switch_warrior.enable()
            self.switch_med_cat.enable()
            self.switch_mediator.enable()
            self.switch_caretaker.enable()
            self.switch_messenger.enable()
            self.switch_denkeeper.enable()
            self.switch_gardener.enable()
            self.switch_storyteller.enable()
            self.retire.enable()
            self.rekit.disable()

            #demote
            if self.the_cat.age in ["adolescent","kitten","newborn"]:
                if self.the_cat.status=="warrior":
                    self.switch_warrior_app.enable()
                if self.the_cat.status=="mediator":
                    self.switch_mediator_app.enable()
                if self.the_cat.status=="caretaker":
                    self.switch_caretaker_app.enable()
                if self.the_cat.status=="messenger":
                    self.switch_messenger_app.enable()
                if self.the_cat.status=="denkeeper":
                    self.switch_denkeeper_app.enable()
                if self.the_cat.status=="gardener":
                    self.switch_gardener_app.enable()
                if self.the_cat.status=="storyteller":
                    self.switch_storyteller_app.enable()
            
            if self.the_cat.status == "elder":
                self.retire.disable()
            elif self.the_cat.status == "warrior":
                self.switch_warrior.disable()
            elif self.the_cat.status == "mediator":
                self.switch_mediator.disable()
            elif self.the_cat.status == "caretaker":
                self.switch_caretaker.disable()
            elif self.the_cat.status == "messenger":
                self.switch_messenger.disable()
            elif self.the_cat.status == "denkeeper":
                self.switch_denkeeper.disable()
            elif self.the_cat.status == "storyteller":
                self.switch_storyteller.disable()
            elif self.the_cat.status == "gardener":
                self.switch_gardener.disable()
        
        elif self.the_cat.status == "medicine cat":
            self.switch_warrior.enable()
            self.switch_mediator.enable()
            self.switch_caretaker.enable()
            self.switch_messenger.enable()
            self.switch_denkeeper.enable()
            self.switch_storyteller.enable()
            self.switch_gardener.enable()
            self.retire.enable()
            self.rekit.disable()
            if self.the_cat.age in ["adolescent","kitten","newborn"]:
                self.switch_med_app.enable()
        
        elif self.the_cat.status == "deputy":
            self.switch_warrior.enable()
            self.retire.enable()
            
            if leader_invalid:
                self.promote_leader.enable()
                
        elif self.the_cat.status == "leader":
            self.switch_warrior.enable()
            self.retire.enable()
            

    def get_role_blurb(self):
        #the one word fellas are easily
        if self.the_cat.status in ["warrior", "leader", "deputy", "mediator", "elder", "kitten", "newborn", "apprentice",  "caretaker", "denkeeper", "messenger", "gardener", "storyteller"]:
            output = "screens.role.blurb_" + self.the_cat.status
        elif self.the_cat.status == "medicine cat":
            output = "screens.role.blurb_medicine_cat"
        elif self.the_cat.status == "medicine cat apprentice":
            output = "screens.role.blurb_medcat_app"
        elif self.the_cat.status == "mediator apprentice":
            output = "screens.role.blurb_mediator_app"
        elif self.the_cat.status == "messenger apprentice":
            output = "screens.role.blurb_messenger_app"
        elif self.the_cat.status == "denkeeper apprentice":
            output = "screens.role.blurb_denkeeper_app"
        elif self.the_cat.status == "caretaker apprentice":
            output = "screens.role.blurb_caretaker_app"
        elif self.the_cat.status == "gardener apprentice":
            output = "screens.role.blurb_gardener_app"
        elif self.the_cat.status == "storyteller apprentice":
            output = "screens.role.blurb_storyteller_app"
        else:
            output = "screens.role.blurb_unknown"

        return i18n.t(output, name=self.the_cat.name, clan=game.clan.name)

    def exit_screen(self):
        self.back_button.kill()
        del self.back_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.bar.kill()
        del self.bar
        self.promote_leader.kill()
        del self.promote_leader
        self.promote_deputy.kill()
        del self.promote_deputy
        self.switch_warrior.kill()
        del self.switch_warrior
        self.switch_messenger.kill()
        del self.switch_messenger
        self.switch_caretaker.kill()
        del self.switch_caretaker
        self.switch_denkeeper.kill()
        del self.switch_denkeeper
        self.switch_med_cat.kill()
        del self.switch_med_cat
        self.switch_mediator.kill()
        del self.switch_mediator
        self.switch_gardener.kill()
        del self.switch_gardener
        self.switch_storyteller.kill()
        del self.switch_storyteller
        self.retire.kill()
        del self.retire
        self.switch_med_app.kill()
        del self.switch_med_app
        self.switch_warrior_app.kill()
        del self.switch_warrior_app
        self.switch_mediator_app.kill()
        del self.switch_mediator_app
        self.switch_gardener_app.kill()
        del self.switch_gardener_app
        self.switch_storyteller_app.kill()
        del self.switch_storyteller_app
        self.switch_messenger_app.kill()
        del self.switch_messenger_app
        self.switch_caretaker_app.kill()
        del self.switch_caretaker_app
        self.switch_denkeeper_app.kill()
        del self.switch_denkeeper_app
        self.rekit.kill()
        del self.rekit
        self.blurb_background.kill()
        del self.blurb_background

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}
