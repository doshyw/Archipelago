# noqa # pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring, fixme, unnecessary-lambda-assignment
from typing import List

from BaseClasses import MultiWorld, Region

from .access_rules import (
    LocationAccessor,
    LocationAccessorFactory,
    RegionAccessor,
    RegionAccessorFactory,
)
from .data import BaseData, CelesteItem, CelesteItemType, CelesteLocation
from .items import ItemGenerator, ItemGeneratorFactory
from .locations import LocationGenerator, LocationGeneratorFactory
from .options import CelesteGameOptions


class GameLogic:
    _options: CelesteGameOptions

    _location_accessor: LocationAccessor
    _region_accessor: RegionAccessor
    _item_generator: ItemGenerator
    _location_generator: LocationGenerator

    def __init__(self, player: int, multiworld: MultiWorld, options: CelesteGameOptions):
        self._options = options
        self._location_accessor = LocationAccessorFactory.get_location_accessor(player, options)
        self._region_accessor = RegionAccessorFactory.get_region_accessor(player, options)
        self._item_generator = ItemGeneratorFactory.get_item_generator(player, options)
        self._location_generator = LocationGeneratorFactory.get_location_generator(
            player, multiworld, options, self._location_accessor, self._region_accessor
        )

    def get_item(self, uuid: int) -> CelesteItem:
        item_dict = self._item_generator.generate_item_dict()
        return item_dict[uuid]

    def get_victory_location(self) -> CelesteLocation:
        goal_level = self._options.get_goal_level()
        uuid = BaseData.item_hash(CelesteItemType.COMPLETION, goal_level.chapter, goal_level.side, 0)
        return self._location_generator.generate_locations()[uuid]

    def get_items(self) -> List[CelesteItem]:
        return self._item_generator.generate_items()

    def get_regions(self) -> List[Region]:
        return self._location_generator.generate_regions()
