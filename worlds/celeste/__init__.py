# pylint: disable=missing-class-docstring, missing-module-docstring, fixme
from copy import deepcopy
from typing import List

from BaseClasses import Item, ItemClassification, MultiWorld, Tutorial
from worlds.AutoWorld import WebWorld, World
from worlds.celeste.data import (
    BaseData,
    CelesteItem,
    CelesteItemType,
    CelesteLevel,
    CelesteLocation,
    CelesteSide,
)
from worlds.celeste.progression import BaseProgression, DefaultProgression

from .options import (
    ProgressionSystemEnum,
    VictoryConditionEnum,
    celeste_options,
    get_option_value,
)


class CelesteWebWorld(WebWorld):
    theme = "ice"
    tutorials = [
        Tutorial(
            "Multiworld Setup Tutorial",
            "A guide to setting up the Celeste randomiser connected to an Archipelago MultiWorld.",
            "English",
            "celeste_en.md",
            "celeste/en",
            ["doshyw"],
        )
    ]


class CelesteWorld(World):
    """
    Help Madeline survive her inner demons on her journey to the top of Celeste Mountain, in this super-tight,
    hand-crafted platformer from the creators of multiplayer classic TowerFall.
    """

    game = "Celeste"
    option_definitions = celeste_options
    topology_present = True
    web = CelesteWebWorld()

    progression_system: BaseProgression

    item_name_to_id = BaseData.item_name_to_id()
    location_name_to_id = BaseData.location_name_to_id()

    required_client_version = (0, 4, 3)

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)
        options = {x: get_option_value(self.multiworld, self.player, x) for x in celeste_options}

        if options["progression_system"] == ProgressionSystemEnum.DEFAULT_PROGRESSION.value:
            self.progression_system = DefaultProgression(options)

    def create_item(self, name: str) -> CelesteItem:
        uuid = self.item_name_to_id[name]
        return self.progression_system.items(self.player, self.multiworld)[uuid].copy()

    def create_regions(self):
        regions = self.progression_system.regions(self.player, self.multiworld)
        self.multiworld.regions.extend(regions)

    def create_items(self):
        item_table = self.progression_system.items(self.player, self.multiworld).values()

        for item in item_table:
            self.multiworld.itempool.append(item.copy())

        self.item_name_groups = {
            "cassettes": [item.name for item in item_table if item.item_type == CelesteItemType.CASSETTE],
            "levels": [item.name for item in item_table if item.item_type == CelesteItemType.COMPLETION],
            "hearts": [item.name for item in item_table if item.item_type == CelesteItemType.GEMHEART],
            "berries": [item.name for item in item_table if item.item_type == CelesteItemType.STRAWBERRY],
        }

    def generate_basic(self) -> None:
        self.multiworld.completion_condition[self.player] = lambda state: state.has(
            self.progression_system.victory_item_name(), self.player
        )

    def fill_slot_data(self):
        slot_data = {}
        for option_name in celeste_options:
            option = self.progression_system.get_option(option_name)
            if option != get_option_value(self.multiworld, self.player, option_name):
                print(f"[WARNING] [CELESTE] Options value {option_name} overridden as {option}.")
            slot_data[option_name] = option

        return slot_data
