# noqa # pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring, fixme, unnecessary-lambda-assignment
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional

from BaseClasses import CollectionState, ItemClassification, MultiWorld, Region
from worlds.celeste.data import (
    STRAWBERRY_UUID,
    BaseData,
    CelesteItem,
    CelesteItemType,
    CelesteLevel,
    CelesteLocation,
    CelesteSide,
)
from worlds.celeste.options import VictoryConditionEnum


class BaseProgression(ABC):
    _options: Dict[str, int | bool]

    _regions: List[Region]
    _items: Dict[int, CelesteItem]
    _locations: Dict[int, CelesteLocation]

    _item_name_to_id: Dict[str, int]
    _location_name_to_id: Dict[str, int]

    def __init__(self, options: Dict[str, int | bool]):
        self._options = options

        self._regions = None
        self._items = None
        self._locations = None

        self._item_name_to_id = None
        self._location_name_to_id = None

    def _goal_level(self) -> CelesteLevel:
        victory_condition = self.get_option("victory_condition")
        if victory_condition == VictoryConditionEnum.CHAPTER_9_FAREWELL.value:
            return CelesteLevel.FAREWELL
        elif victory_condition == VictoryConditionEnum.CHAPTER_8_CORE.value:
            return CelesteLevel.CORE
        elif victory_condition == VictoryConditionEnum.CHAPTER_7_SUMMIT.value:
            return CelesteLevel.THE_SUMMIT

    def _goal_side(self) -> CelesteLevel:
        return CelesteSide.A_SIDE

    def get_option(self, name: str) -> int | bool:
        return self._options[name]

    def item_name_to_id(self) -> Dict[str, int]:
        return {}

    @abstractmethod
    def victory_item_name(self) -> str:
        return ""

    @abstractmethod
    def regions(self, player: int, multiworld: MultiWorld) -> List[Region]:
        return []

    @abstractmethod
    def items(self, player: int, multiworld: MultiWorld) -> Dict[int, CelesteItem]:
        return []

    @abstractmethod
    def locations(self, player: int, multiworld: MultiWorld) -> Dict[int, CelesteLocation]:
        return []


class DefaultProgression(BaseProgression):
    @staticmethod
    def _region_access_rule(
        player: int, level: CelesteLevel, side: CelesteSide
    ) -> Optional[Callable[[CollectionState], bool]]:
        if side == 0:
            if level == 1:
                return None
            return lambda state: state.has_any(
                {
                    BaseData.item_name(CelesteItemType.COMPLETION, level.previous(), CelesteSide.A_SIDE),
                    BaseData.item_name(CelesteItemType.COMPLETION, level.previous(), CelesteSide.B_SIDE),
                    BaseData.item_name(CelesteItemType.COMPLETION, level.previous(), CelesteSide.C_SIDE),
                },
                player,
            )
        elif side == 1:
            return lambda state: state.has(
                BaseData.item_name(CelesteItemType.CASSETTE, level, CelesteSide.A_SIDE), player
            )
        elif side == 2:
            return lambda state: state.has_all(
                {
                    BaseData.item_name(CelesteItemType.COMPLETION, level, CelesteSide.A_SIDE),
                    BaseData.item_name(CelesteItemType.COMPLETION, level, CelesteSide.B_SIDE),
                },
                player,
            )
        else:
            return None

    def _location_access_rule(
        self, player: int, level: CelesteLevel, side: CelesteSide
    ) -> Optional[Callable[[CollectionState], bool]]:
        access_rule = lambda state: True

        if level == CelesteLevel.CORE:
            if side == CelesteSide.A_SIDE:
                access_rule = lambda state: access_rule(state) and state.has_group("gemhearts", player, 4)
            elif side == CelesteSide.B_SIDE:
                access_rule = lambda state: access_rule(state) and state.has_group("gemhearts", player, 15)
            elif side == CelesteSide.C_SIDE:
                access_rule = lambda state: access_rule(state) and state.has_group("gemhearts", player, 23)

        if level == self._goal_level() and side == self._goal_side():
            access_rule = lambda state: (
                access_rule
                and state.has_group(
                    "hearts",
                    player,
                    self.get_option("hearts_required"),
                )
                and state.has_group(
                    "berries",
                    player,
                    self.get_option("berries_required"),
                )
                and state.has_group(
                    "levels",
                    player,
                    self.get_option("levels_required"),
                )
                and state.has_group(
                    "cassettes",
                    player,
                    self.get_option("cassettes_required"),
                )
            )

        return access_rule

    def victory_item_name(self) -> str:
        return BaseData.item_name(CelesteItemType.COMPLETION, self._goal_level(), self._goal_side())

    def regions(self, player: int, multiworld: MultiWorld) -> List[Region]:
        if self._regions is not None:
            return self._regions
        self._regions = []

        if self._locations is None:
            self.locations(player, multiworld)

        menu_region = Region("Menu", player, multiworld)
        self._regions.append(menu_region)
        map_region = Region("Map", player, multiworld)
        self._regions.append(map_region)
        menu_region.connect(map_region)

        for level, side, name in BaseData.regions(self._goal_level(), self._goal_side()):
            level_region = Region(name, player, multiworld)
            self._regions.append(level_region)
            map_region.connect(
                level_region, f"Load {name}", DefaultProgression._region_access_rule(player, level, side)
            )
            native_locations = [
                location for location in self._locations.values() if location.level == level and location.side == side
            ]
            for location in native_locations:
                level_region.locations.append(location)
                location.parent_region = level_region

        return self._regions

    def items(self, player: int, multiworld: MultiWorld) -> Dict[int, CelesteItem]:
        if self._items is not None:
            return self._items
        self._items = {}

        item_count = {
            CelesteItemType.CASSETTE: 0,
            CelesteItemType.COMPLETION: 0,
            CelesteItemType.GEMHEART: 0,
            CelesteItemType.STRAWBERRY: 0,
        }

        for item_type in [elem[0] for elem in BaseData.items(self._goal_level(), self._goal_side(), False)]:
            item_count[item_type] += 1

        self._options["berries_required"] = min(
            self.get_option("berries_required"), item_count[CelesteItemType.STRAWBERRY]
        )
        self._options["cassettes_required"] = min(
            self.get_option("cassettes_required"), item_count[CelesteItemType.CASSETTE]
        )
        self._options["hearts_required"] = min(self.get_option("hearts_required"), item_count[CelesteItemType.GEMHEART])
        self._options["levels_required"] = min(
            self.get_option("levels_required"), item_count[CelesteItemType.COMPLETION]
        )

        required_strawberries = self.get_option("berries_required")
        strawberry_count = 0
        for item_type, level, side, name, uuid in BaseData.items(self._goal_level(), self._goal_side()):
            classification = ItemClassification.progression
            if item_type == CelesteItemType.STRAWBERRY:
                uuid = STRAWBERRY_UUID
                if strawberry_count >= required_strawberries:
                    classification = ItemClassification.filler
                strawberry_count += 1

            item = CelesteItem(
                name=name,
                classification=classification,
                code=uuid,
                player=player,
                item_type=item_type,
                level=level,
                side=side,
            )
            self._items[uuid] = item

        return self._items

    def locations(self, player: int, multiworld: MultiWorld) -> Dict[int, CelesteLocation]:
        if self._locations is not None:
            return self._locations
        self._locations = {}

        if self._items is None:
            self.items(player, multiworld)

        for level, side, name, uuid in BaseData.locations(self._goal_level(), self._goal_side()):
            location = CelesteLocation(player, level, side, name, uuid)
            location.access_rule = self._location_access_rule(player, level, side)
            self._locations[uuid] = location

        return self._locations

    def item_name_to_id(self) -> Dict[str, int]:
        if self._item_name_to_id is not None:
            return self._item_name_to_id
        self._item_name_to_id = {}

        if self._items is None:
            raise RuntimeError("[Celeste] Items have not yet been initialised for this system.")

        for uuid, item in self._items.items():
            if item.item_type != CelesteItemType.STRAWBERRY:
                self._item_name_to_id[item.name] = uuid

        self._item_name_to_id["Strawberry"] = STRAWBERRY_UUID

        return self._item_name_to_id

    def location_name_to_id(self) -> Dict[str, int]:
        if self._location_name_to_id is not None:
            return self._location_name_to_id
        self._location_name_to_id = {}

        if self._locations is None:
            raise RuntimeError("[Celeste] Locations have not yet been initialised for this system.")

        for uuid, location in self._locations.items():
            self._location_name_to_id[location.name] = uuid

        return self._location_name_to_id
