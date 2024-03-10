# pylint: disable=missing-class-docstring, missing-module-docstring, fixme
from copy import deepcopy
from functools import partial
from typing import List

from BaseClasses import Item, ItemClassification, MultiWorld, Tutorial
from worlds.AutoWorld import WebWorld, World
from worlds.celeste.data import (
    BaseData,
    CelesteChapter,
    CelesteItem,
    CelesteItemType,
    CelesteLocation,
    CelesteSide,
)
from worlds.celeste.progression import GameLogic

from .options import CelesteGameOptions


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
    options_dataclass = CelesteGameOptions
    options: CelesteGameOptions
    topology_present = True
    web = CelesteWebWorld()

    item_name_to_id = BaseData.item_name_to_id()
    location_name_to_id = BaseData.location_name_to_id()

    game_logic: GameLogic

    required_client_version = (0, 4, 4)

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)
        self.game_logic = None

    def generate_early(self) -> None:
        self.game_logic = GameLogic(self.player, self.multiworld, self.options)

    def create_item(self, name: str) -> CelesteItem:
        uuid = self.item_name_to_id[name]

        # If the World is properly initialised, get the item from the GameLogic object.
        if self.game_logic is not None:
            return self.game_logic.get_item(uuid)

        # Otherwise, create a raw Filler item based on the base data.
        item_type, level, name, _ = BaseData.get_item(uuid)
        return CelesteItem(name, ItemClassification.filler, uuid, self.player, item_type, level)

    def create_regions(self):
        self.multiworld.regions.extend(self.game_logic.get_regions())

    def create_items(self):
        item_table = self.game_logic.get_items()

        for item in item_table:
            if item.name != "Victory (Celeste)":
                self.multiworld.itempool.append(item.copy())

        self.item_name_groups = {
            "cassettes": [item.name for item in item_table if item.item_type == CelesteItemType.CASSETTE],
            "levels": [item.name for item in item_table if item.item_type == CelesteItemType.COMPLETION],
            "hearts": [item.name for item in item_table if item.item_type == CelesteItemType.GEMHEART],
        }

    def generate_basic(self) -> None:
        self.multiworld.get_location(self.game_logic.get_victory_location().name, self.player).place_locked_item(
            self.create_item("Victory (Celeste)")
        )
        self.multiworld.completion_condition[self.player] = partial(
            lambda player, state: state.has("Victory (Celeste)", player), self.player
        )

    def fill_slot_data(self):
        return self.options.as_dict(
            "berries_required",
            "cassettes_required",
            "hearts_required",
            "levels_required",
            "goal_level",
            "progression_system",
            "disable_heart_gates",
        )
