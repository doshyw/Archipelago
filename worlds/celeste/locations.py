from abc import ABC, abstractmethod
from typing import Dict, List

from BaseClasses import MultiWorld, Region

from .access_rules import LocationAccessor, RegionAccessor
from .data import BaseData, CelesteLocation
from .options import CelesteGameOptions, ProgressionSystem


class LocationGeneratorFactory:
    """Factory used for retrieving a `LocationGenerator` for dependency injection in building a `ProgressionSystem`."""

    @staticmethod
    def get_location_generator(
        player: int,
        multiworld: MultiWorld,
        options: CelesteGameOptions,
        location_accessor: LocationAccessor,
        region_accessor: RegionAccessor,
    ) -> "LocationGenerator":
        """Retrieves a `LocationGenerator` sub-class based on the provided player options.

        Args:
            player (`int`): The number representing a player.
            options (`CelesteGameOptions`): The world options provided by the given player.

        Returns:
            `LocationGenerator`: Object for generating locations and regions to add to the MultiWorld.
        """
        if options.progression_system == ProgressionSystem.option_default_progression:
            return OriginalLocationGenerator(player, multiworld, options, location_accessor, region_accessor)


class LocationGenerator(ABC):
    """Abstract class for generating locations and regions to add to the MultiWorld."""

    _player: int
    _multiworld: MultiWorld
    _options: CelesteGameOptions
    _location_accessor: LocationAccessor
    _region_accessor: RegionAccessor

    def __init__(
        self,
        player: int,
        multiworld: MultiWorld,
        options: CelesteGameOptions,
        location_accessor: LocationAccessor,
        region_accessor: RegionAccessor,
    ):
        self._player = player
        self._multiworld = multiworld
        self._options = options
        self._location_accessor = location_accessor
        self._region_accessor = region_accessor

    @abstractmethod
    def generate_locations(self) -> Dict[int, CelesteLocation]:
        """Generates a mapping from UUID for locations that should be included in the MultiWorld for this player.

        Returns:
            `Dict[int, CelesteLocation]`: Mapping from UUID for locations that should be included in the MultiWorld.
        """

    @abstractmethod
    def generate_regions(self) -> List[Region]:
        """Generates a list of regions that should be included in the MultiWorld for this player.

        Returns:
            `List[Region]`: Regions that should be included in the MultiWorld.
        """


class OriginalLocationGenerator(LocationGenerator):
    """Class for generating locations and regions to add to the MultiWorld based on original Celeste requirements."""

    _locations: Dict[int, CelesteLocation]
    _regions: List[Region]

    def __init__(
        self,
        player: int,
        multiworld: MultiWorld,
        options: CelesteGameOptions,
        location_accessor: LocationAccessor,
        region_accessor: RegionAccessor,
    ):
        super().__init__(player, multiworld, options, location_accessor, region_accessor)
        self._locations = {}
        self._regions = []

    def generate_locations(self) -> List[CelesteLocation]:
        if len(self._locations) > 0:
            return self._locations

        goal_level = self._options.get_goal_level()
        for level, name, uuid in BaseData.locations():
            # Skip all locations that would come after the goal level
            if level > goal_level:
                continue
            location = CelesteLocation(self._player, level, name, uuid)
            location.access_rule = self._location_accessor.generate(location)
            self._locations[uuid] = location

        if len(self._regions) == 0:
            self.generate_regions()
        return self._locations

    def generate_regions(self) -> List[Region]:
        if len(self._locations) == 0:
            self.generate_locations()

        if len(self._regions) > 0:
            return self._regions

        menu_region = Region("Menu", self._player, self._multiworld)
        self._regions.append(menu_region)
        map_region = Region("Map", self._player, self._multiworld)
        self._regions.append(map_region)
        menu_region.connect(map_region)

        goal_level = self._options.get_goal_level()
        for level, name in BaseData.regions():
            # Skip all regions that would come after the goal level
            if level > goal_level:
                continue

            level_region = Region(name, self._player, self._multiworld)
            self._regions.append(level_region)

            map_region.connect(level_region, f"Load {name}", self._region_accessor.generate(level))
            native_locations = [location for location in self._locations.values() if location.level == level]
            for location in native_locations:
                level_region.locations.append(location)
                location.parent_region = level_region

        return self._regions
