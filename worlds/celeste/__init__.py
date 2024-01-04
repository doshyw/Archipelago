# pylint: disable=missing-class-docstring, missing-module-docstring, fixme
from copy import deepcopy
from typing import List

from BaseClasses import Item, ItemClassification, MultiWorld, Tutorial
from worlds.AutoWorld import WebWorld, World

from .items import (
    CelesteItem,
    CelesteItemFactory,
    CelesteItemType,
    CelesteLocationFactory,
)
from .options import VictoryConditionEnum, celeste_options, get_option_value
from .regions import CelesteRegionFactory


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

    victory_condition: VictoryConditionEnum
    completion_level: int

    item_factory: CelesteItemFactory
    location_factory: CelesteLocationFactory
    region_factory: CelesteRegionFactory

    item_name_to_id = CelesteItemFactory.get_name_to_id()
    location_name_to_id = CelesteLocationFactory.get_name_to_id()

    required_client_version = (0, 4, 3)

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)
        self.completion_level = 10
        self.item_factory = CelesteItemFactory(self)
        self.location_factory = CelesteLocationFactory()
        self.region_factory = CelesteRegionFactory()

    def generate_early(self) -> None:
        self.victory_condition = VictoryConditionEnum(
            get_option_value(self.multiworld, self.player, "victory_condition")
        )
        if self.victory_condition == VictoryConditionEnum.CHAPTER_9_FAREWELL:
            self.completion_level = 10
        elif self.victory_condition == VictoryConditionEnum.CHAPTER_8_CORE:
            self.completion_level = 9
        elif self.victory_condition == VictoryConditionEnum.CHAPTER_7_SUMMIT:
            self.completion_level = 7

    def create_item(self, name: str) -> Item:
        return self.item_factory.create_item(name)

    def create_regions(self):
        self.region_factory.activate(self)

    def create_items(self):
        item_table = self.item_factory.get_table(self)

        for item in item_table:
            if item.level > self.completion_level:
                continue
            if item.level == self.completion_level and item.side == 0 and item.item_type == CelesteItemType.COMPLETION:
                continue
            self.multiworld.itempool.append(deepcopy(item))

        self.item_name_groups = {
            "cassettes": [item.name for item in item_table if item.item_type == CelesteItemType.CASSETTE],
            "completions": [item.name for item in item_table if item.item_type == CelesteItemType.COMPLETION],
            "gemhearts": [item.name for item in item_table if item.item_type == CelesteItemType.GEMHEART],
            "strawberries": [item.name for item in item_table if item.item_type == CelesteItemType.STRAWBERRY],
        }

    def generate_basic(self) -> None:
        if self.victory_condition == VictoryConditionEnum.CHAPTER_9_FAREWELL:
            self.multiworld.completion_condition[self.player] = lambda state: state.has(
                "Completion (Chapter 9: Farewell)", self.player
            )
        elif self.victory_condition == VictoryConditionEnum.CHAPTER_8_CORE:
            self.multiworld.completion_condition[self.player] = lambda state: state.has(
                "Completion (Chapter 8: Core A-Side)", self.player
            )
        elif self.victory_condition == VictoryConditionEnum.CHAPTER_7_SUMMIT:
            self.multiworld.completion_condition[self.player] = lambda state: state.has(
                "Completion (Chapter 7: The Summit A-Side)", self.player
            )

    def pre_fill(self):
        item_table = self.item_factory.get_table(self)
        for item in item_table:
            if item.level > self.completion_level or (
                item.level == self.completion_level and item.side == 0 and item.item_type == CelesteItemType.COMPLETION
            ):
                self.multiworld.get_location(item.name, self.player).place_locked_item(deepcopy(item))

    def fill_slot_data(self):
        slot_data = {}
        for option_name in celeste_options:
            slot_data[option_name] = get_option_value(self.multiworld, self.player, option_name)
        return slot_data
