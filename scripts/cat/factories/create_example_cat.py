from __future__ import annotations

from random import sample, choices, random, choice
from typing import TYPE_CHECKING

from scripts.cat.enums import CatRank
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.cat.pelts import Pelt

from scripts.cat.conditions.gain_conditions import (
    gain_permanent_condition,
)
from scripts.cat.constants import (
    PERMANENT_CONDITIONS,
)
from scripts.game_structure import constants

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


def create_example_cats(majority_rank: CatRank, rank_weights: dict) -> list["Cat"]:
    majority_rank_cats = sample(range(12), 3)

    chosen_cats = []
    for cat_index in range(12):
        if cat_index in majority_rank_cats:
            chosen_cats.append(NewCatFactory.create_cat(rank=majority_rank))
        else:
            random_rank = choices(
                list(rank_weights.keys()), list(rank_weights.values())
            )[0]
            chosen_cats.append(NewCatFactory.create_cat(rank=random_rank))
    #generate permanent conditions
    for created_cat in chosen_cats:
        chance = constants.CONFIG["cat_generation"]["base_permanent_condition"] + 10
        if not int(random() * chance):
            possible_conditions = []
            for condition in PERMANENT_CONDITIONS:
                if (
                    created_cat.age.is_baby()
                    and not PERMANENT_CONDITIONS[condition]["can_be_congenital"]
                ):
                    continue
                if condition in ["excess_testosterone", "testosterone_deficiency", "aneuploidy",
                                            "mosaicism", "chimerism"]:
                    continue
                possible_conditions.append(condition)

            if possible_conditions:
                chosen_condition = choice(possible_conditions)
                if PERMANENT_CONDITIONS[chosen_condition]["can_be_congenital"]:
                    gain_permanent_condition(created_cat, chosen_condition, True)
        if created_cat.gender == "intersex":
            intersex_condition = choice(["excess_testosterone", "testosterone_deficiency", "aneuploidy",
                                            "mosaicism", "chimerism"])
            gain_permanent_condition(created_cat, intersex_condition, is_congenital=True)
                    
    return chosen_cats


def create_option_preview_cat(scar: str = None, acc: str = None):
    """
    Creates a cat with the specified scar and/or accessory.
    :param scar: Desired scar (only one)
    :param acc: Desired accessory (only one)
    """
    new_cat = TestCatFactory.create_cat(
        moons=60,
        loading_cat=True,
        pelt=Pelt(
            name="SingleColour",
            colour="WHITE",
            length="medium",
            eye_color="SAGE",
            reverse=False,
            white_patches=None,
            vitiligo=None,
            points=None,
            tortie_marking=None,
            tortie_base=None,
            tortie_pattern=None,
            tortie_colour=None,
            tint="gray",
            skin="BLUE",
            scars=[scar] if scar else [],
            adult_sprite="8",
            accessory=[acc] if acc else [],
        ),
    )

    return new_cat
