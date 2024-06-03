import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat
from scripts.screens.Screens import Screens
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from scripts.utility import scale, get_text_box_theme

class NurseryScreen(Screens):
    """
    Screen for the Nursery, in which play-sessions can be held for kittens, functioning similarly to patrols.
    """

    def __init__(self, name=None):
        super().__init__(name)
        self.chosen_kits = []
        self.partaking_adult = None

        self.screen_elements = {}

    def screen_switches(self):
        """Runs when this screen is switched to."""

        self.hide_menu_buttons()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        
        # BACKGROUND FLOWERS
        try:
            if game.settings["dark mode"]:
                self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((0, 0), (1600, 1400))),
                    pygame.image.load(
                        f"resources/images/nursery_flowers_dark.png").convert_alpha(),
                    object_id="#nursery_flowers_bg",
                    starting_height=1,
                    manager=MANAGER)
            else:
                self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((0, 0), (1600, 1400))),
                    pygame.image.load(
                        f"resources/images/nursery_flowers_light.png").convert_alpha(),
                    object_id="#nursery_flowers_bg",
                    starting_height=1,
                    manager=MANAGER)
        except FileNotFoundError:
            print("WARNING: Nursery background images not found.")

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here. """

        if game.switches['window_open']:
            pass
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)

    def exit_screen(self):
        """Runs when screen exits"""
        self.back_button.kill()

        for ele in self.screen_elements:
            self.screen_elements[ele].kill()
