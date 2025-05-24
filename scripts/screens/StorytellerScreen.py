from math import ceil
from random import choice

import i18n
import pygame.transform
import pygame_gui.elements
import os.path
from random import choice, randint
import ujson

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
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
    event_text_adjust
)
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon


class StorytellerScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.selected_storyteller = None
        self.selected_cat = None
        self.search_bar = None
        self.search_bar_image = None
        self.storyteller_elements = {}
        self.storytellers = []
        self.cat_buttons = []
        self.page = 1
        self.selected_cat_elements = {}
        self.allow_romantic = True
        self.current_listed_cats = None
        self.previous_search_text = ""
        
        self.heroism = None
        self.scary = None
        self.caution = None
        self.love = None
        self.acceptance = None
        self.triumph = None
        self.story_selected = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.last_med:
                self.selected_storyteller -= 1
                self.update_storyteller_info()
            elif event.ui_element == self.next_med:
                self.selected_storyteller += 1
                self.update_storyteller_info()
            elif event.ui_element == self.next_page:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page:
                self.page -= 1
                self.update_page()
            elif event.ui_element == self.deselect:
                self.selected_cat = None
                self.update_selected_cats()
            elif event.ui_element == self.mediate_button:
                game.patrolled.append(self.storytellers[self.selected_storyteller].ID)
                output = self.story_results(self.story_selected)
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_storyteller_info()
            elif event.ui_element == self.random:
                self.selected_cat = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element in self.cat_buttons:
                if event.ui_element.return_cat_object() not in [
                    self.selected_cat
                ]:
                    self.selected_cat = event.ui_element.return_cat_object()
                    self.update_selected_cats()
            elif event.ui_element in [self.heroism, self.scary, self.caution, self.love, self.acceptance, self.triumph]:
                self.select_story(event.ui_element)
                self.update_buttons()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        # Gather the storytellers:
        self.storytellers = []
        for cat in Cat.all_cats_list:
            if cat.status in ["storyteller", "storyteller apprentice"] and not (
                cat.dead or cat.outside
            ):
                self.storytellers.append(cat)

        self.page = 1

        if self.storytellers:
            if Cat.fetch_cat(game.switches["cat"]) in self.storytellers:
                self.selected_storyteller = self.storytellers.index(
                    Cat.fetch_cat(game.switches["cat"])
                )
            else:
                self.selected_storyteller = 0
        else:
            self.selected_storyteller = None

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
            ui_scale(pygame.Rect((340, 320), (105, 30))),
            "Tell Story",
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

        self.deselect = UISurfaceImageButton(
            ui_scale(pygame.Rect((68, 434), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.results = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 360), (229, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        ) 

        self.error = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 37), (229, 57))),
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
        
        self.heroism = UISurfaceImageButton(
            ui_scale(pygame.Rect((590, 115), (125, 30))),
            "Tale of Heroism",
            get_button_dict(ButtonStyles.SQUOVAL, (125, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.scary = UISurfaceImageButton(
            ui_scale(pygame.Rect((590, 165), (125, 30))),
            "Scary Story",
            get_button_dict(ButtonStyles.SQUOVAL, (125, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.caution = UISurfaceImageButton(
            ui_scale(pygame.Rect((590, 215), (125, 30))),
            "Cautionary Tale",
            get_button_dict(ButtonStyles.SQUOVAL, (125, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.love = UISurfaceImageButton(
            ui_scale(pygame.Rect((590, 265), (125, 30))),
            "Love Story",
            get_button_dict(ButtonStyles.SQUOVAL, (125, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.acceptance = UISurfaceImageButton(
            ui_scale(pygame.Rect((590, 315), (125, 30))),
            "Sympathetic Tale",
            get_button_dict(ButtonStyles.SQUOVAL, (125, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.triumph = UISurfaceImageButton(
            ui_scale(pygame.Rect((590, 365), (125, 30))),
            "Triumph of War",
            get_button_dict(ButtonStyles.SQUOVAL, (125, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.update_buttons()
        self.update_storyteller_info()

    def random_cat(self):
        if self.selected_cat_list():
            random_list = [
                i for i in self.all_cats_list if i.ID not in self.selected_cat_list()
            ]
        else:
            random_list = self.all_cats_list
        return choice(random_list)

    def update_storyteller_info(self):
        for ele in self.storyteller_elements:
            self.storyteller_elements[ele].kill()
        self.storyteller_elements = {}

        if (
            self.selected_storyteller is not None
        ):  # It can be zero, so we must test for not None here.
            x_value = 315
            storyteller = self.storytellers[self.selected_storyteller]

            # Clear storyteller as selected cat
            if storyteller == self.selected_cat:
                self.selected_cat = None
                self.update_selected_cats()

            self.storyteller_elements["storyteller_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_value, 90), (150, 150))),
                pygame.transform.scale(
                    storyteller.sprite, ui_scale_dimensions((150, 150))
                ),
            )

            name = str(storyteller.name)
            short_name = shorten_text_to_fit(name, 120, 11)
            self.storyteller_elements["name"] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x_value - 5, 240), (160, -1))),
                short_name,
                object_id=get_text_box_theme(),
            )

            text = storyteller.personality.trait + "\n" + storyteller.experience_level

            if storyteller.not_working():
                text += "\n" + i18n.t("general.cant_work")
                self.mediate_button.disable()
            else:
                text += "\n" + i18n.t("general.can_work")
                self.mediate_button.enable()

            self.storyteller_elements["details"] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(pygame.Rect((x_value, 260), (155, 60))),
                object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                manager=MANAGER,
            )

            storyteller_number = len(self.storytellers)
            if self.selected_storyteller < storyteller_number - 1:
                self.next_med.enable()
            else:
                self.next_med.disable()

            if self.selected_storyteller > 0:
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
            if (i.ID != self.storytellers[self.selected_storyteller].ID)
        ]
        self.all_cats = self.chunks(self.all_cats_list, 24)
        self.current_listed_cats = self.all_cats_list
        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )
        self.update_page()
        
    def select_story(self,story):
        if story == self.heroism:
            self.story_selected = "heroism"
        elif story == self.scary:
            self.story_selected = "scary"
        elif story == self.caution:
            self.story_selected = "caution"
        elif story == self.love:
            self.story_selected = "love"
        elif story == self.acceptance:
            self.story_selected = "acceptance"
        elif story == self.triumph:
            self.story_selected = "triumph"

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
        
    def story_results(self, story_type):
        # first we get the story
        results = "ERROR: no stories found"
        storyteller = self.storytellers[self.selected_storyteller]
        if os.path.exists('resources/dicts/stories.json'):
                with open('resources/dicts/stories.json') as read_file:
                    story_dict = ujson.loads(read_file.read())
        results = choice(story_dict[story_type])
        results = event_text_adjust(Cat, results, main_cat = storyteller, random_cat = self.selected_cat)
        
        #now we check if they did well
        if storyteller.experience_level == "untrained":
            chance = 15
        elif storyteller.experience_level == "trainee":
            # Negative bonus for very low.
            chance = 20
        elif storyteller.experience_level == "prepared":
            chance = 35
        elif storyteller.experience_level == "proficient":
            chance = 55
        elif storyteller.experience_level == "expert":
            chance = 70
        elif storyteller.experience_level == "master":
            chance = 100
        else:
            chance = 40
        
        success = True
        bonus = 0
        if randint(1,chance) == 1:
            success = False
            results += "The Clan is not impressed."
        else:
            if chance > 50:
                bonus = randint(1,3)
            else:
                bonus = 1
        
        #now we do the bonuses!
        if self.selected_cat.dead and success:
            #reset fading! the cats no longer forgor
            if self.selected_cat.pelt.opacity < 50:
                self.selected_cat.pelt.opacity = int(self.selected_cat.pelt.opacity*2)
            else:
                self.selected_cat.pelt.opacity = 100
            results += "\n" + "Fading reduced!"
        
        if success:
            results +=  "\n" + "The Clan's opinion of " + str(self.selected_cat.name) + " has shifted."
            for kitty in self.all_cats_list:
                if not (kitty.dead or kitty.outside):
                    if self.selected_cat.ID in kitty.relationships:
                        rel = kitty.relationships[self.selected_cat.ID]
                    else:
                        rel = kitty.create_one_relationship(self.selected_cat)
                    if rel:
                        if story_type == "heroism":
                            rel.admiration = Cat.effect_relation(
                                rel.admiration,
                                bonus
                            )
                            rel.trust = Cat.effect_relation(
                                rel.trust,
                                bonus
                            )
                        elif story_type == "acceptance":
                            rel.trust = Cat.effect_relation(
                                rel.trust,
                                bonus
                            )
                            rel.platonic_like = Cat.effect_relation(
                                rel.platonic_like,
                                bonus
                            )
                        elif story_type == "love":
                            rel.platonic_like = Cat.effect_relation(
                                rel.platonic_like,
                                bonus
                            )
                            rel.comfortable = Cat.effect_relation(
                                rel.comfortable,
                                bonus
                            )
                        elif story_type == "triumph":
                            rel.jealousy = Cat.effect_relation(
                                rel.jealousy,
                                bonus
                            )
                            rel.admiration = Cat.effect_relation(
                                rel.admiration,
                                bonus
                            )
                        elif story_type == "scary":
                            rel.dislike = Cat.effect_relation(
                                rel.dislike,
                                bonus
                            )
                            rel.jealousy = Cat.effect_relation(
                                rel.jealousy,
                                bonus
                            )
                        else:
                            rel.comfortable = Cat.effect_relation(
                                rel.comfortable,
                                bonus
                            )
                            rel.trust = Cat.effect_relation(
                                rel.trust,
                                bonus
                            )
                    
            
        
        return results

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
        col1 = ""
        if cat.dead:
            col1 += "former "
        col1 += i18n.t(f"general.{cat.status.lower()}", count=1) + "\n" + i18n.t("general.moons_age", count=cat.moons)
        trait_text = i18n.t(f"cat.personality.{cat.personality.trait}")
        if cat.personality.trait != cat.personality.trait2:
            trait_text += " & " + i18n.t(f"cat.personality.{cat.personality.trait2}")    
        col1 +=  "\n" + trait_text
        col1 += "\n" + cat.skills.skill_string()
        col1 += "\n \n" + event_text_adjust(
            Cat, i18n.t(f"cat.backstories.{cat.backstory}"), main_cat=cat
        )
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

        invalid_storyteller = False
        if self.selected_storyteller is not None:
            if self.storytellers[self.selected_storyteller].not_working():
                invalid_storyteller = True
                error_message += i18n.t("screens.mediation.story_cant_work")
            elif self.storytellers[self.selected_storyteller].ID in game.patrolled:
                invalid_storyteller = True
                error_message += i18n.t("screens.mediation.story_already_worked")
        else:
            invalid_storyteller = True
            
        invalid_selection = False
        if not self.selected_cat:
            invalid_selection = False

        self.error.set_text(error_message)
        
        invalid_story = True
        self.heroism.enable()
        self.scary.enable()
        self.love.enable()
        self.acceptance.enable()
        self.triumph.enable()
        self.caution.enable()
        
        if self.story_selected:
            invalid_story = False
            if self.story_selected == "heroism":
                self.heroism.disable()
            elif self.story_selected == "scary":
                self.scary.disable()
            elif self.story_selected == "love":
                self.love.disable()
            elif self.story_selected == "acceptance":
                self.acceptance.disable()
            elif self.story_selected == "triumph":
                self.triumph.disable()
            elif self.story_selected == "caution":
                self.caution.disable()
            

        if invalid_storyteller or invalid_story or invalid_selection:
            self.mediate_button.disable()
        else:
            self.mediate_button.enable()
            if self.story_selected == "love" and self.selected_cat.status in ["newborn", "kitten"]:
                self.mediate_button.disable()
            elif self.story_selected == "love" and "apprentice" in self.selected_cat.status:
                self.mediate_button.disable()
            
        

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

        for ele in self.storyteller_elements:
            self.storyteller_elements[ele].kill()
        self.storyteller_elements = {}

        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.storytellers = []
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
        self.heroism.kill()
        del self.heroism
        self.scary.kill()
        del self.scary
        self.caution.kill()
        del self.caution
        self.love.kill()
        del self.love
        self.acceptance.kill()
        del self.acceptance
        self.triumph.kill()
        del self.triumph

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
