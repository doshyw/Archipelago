from abc import ABC, abstractmethod
from functools import partial
from typing import Callable, Optional

from BaseClasses import CollectionState

from .data import (
    BaseData,
    CelesteChapter,
    CelesteItemType,
    CelesteLevel,
    CelesteLocation,
    CelesteSide,
)
from .options import CelesteGameOptions, ProgressionSystem


class RegionAccessorFactory:
    """Factory used for retrieving a `RegionAccessor` for dependency injection in building a `ProgressionSystem`."""

    @staticmethod
    def get_region_accessor(player: int, options: CelesteGameOptions) -> "RegionAccessor":
        """Retrieves a `RegionAccessor` sub-class based on the provided player options.

        Args:
            player (`int`): The number representing a player.
            options (`CelesteGameOptions`): The world options provided by the given player.

        Returns:
            `RegionAccessor`: Object for generating region access rules.
        """
        if options.progression_system == ProgressionSystem.option_default_progression:
            return OriginalRegionAccessor(player, options)


class LocationAccessorFactory:
    """Factory used for retrieving a `LocationAccessor` for dependency injection in building a `ProgressionSystem`."""

    @staticmethod
    def get_location_accessor(player: int, options: CelesteGameOptions) -> "LocationAccessor":
        """Retrieves a `LocationAccessor` sub-class based on the provided player options.

        Args:
            player (`int`): The number representing a player.
            options (`CelesteGameOptions`): The world options provided by the given player.

        Returns:
            `LocationAccessor`: Object for generating location access rules.
        """
        if options.progression_system == ProgressionSystem.option_default_progression:
            return OriginalLocationAccessor(player, options)


class RegionAccessor(ABC):
    """Abstract class for generating region access rules."""

    _player: int
    _options: CelesteGameOptions

    def __init__(self, player: int, options: CelesteGameOptions):
        self._player = player
        self._options = options

    @abstractmethod
    def generate(self, level: CelesteLevel) -> Optional[Callable[[CollectionState], bool]]:
        """Generates a lambda function that calculates a region's accessbility based on the player's items.

        Args:
            level (`CelesteLevel`): Level that the region is in.

        Returns:
            `Optional[Callable[[CollectionState], bool]]`: None if there are no access rules, and a callable otherwise.
        """
        return None


class OriginalRegionAccessor(RegionAccessor):
    """Class for generating region access rules based on original Celeste requirements."""

    def generate(self, level: CelesteLevel) -> Optional[Callable[[CollectionState], bool]]:
        if level.side == CelesteSide.A_SIDE:
            if level.chapter == CelesteChapter.FORSAKEN_CITY:
                return None
            if level.chapter.previous() == CelesteChapter.EPILOGUE:
                return lambda state: state.has(
                    BaseData.item_name(CelesteItemType.COMPLETION, level.chapter.previous(), CelesteSide.A_SIDE),
                    self._player,
                )
            return lambda state: state.has_any(
                {
                    BaseData.item_name(CelesteItemType.COMPLETION, level.chapter.previous(), CelesteSide.A_SIDE),
                    BaseData.item_name(CelesteItemType.COMPLETION, level.chapter.previous(), CelesteSide.B_SIDE),
                    BaseData.item_name(CelesteItemType.COMPLETION, level.chapter.previous(), CelesteSide.C_SIDE),
                },
                self._player,
            )
        elif level.side == CelesteSide.B_SIDE:
            return lambda state: state.has(
                BaseData.item_name(CelesteItemType.CASSETTE, level.chapter, CelesteSide.A_SIDE), self._player
            )
        elif level.side == CelesteSide.C_SIDE:
            return lambda state: state.has_all(
                {
                    BaseData.item_name(CelesteItemType.GEMHEART, level.chapter, CelesteSide.A_SIDE),
                    BaseData.item_name(CelesteItemType.GEMHEART, level.chapter, CelesteSide.B_SIDE),
                },
                self._player,
            )
        else:
            return None


class LocationAccessor(ABC):
    """Abstract class for generating location access rules."""

    _player: int
    _options: CelesteGameOptions

    def __init__(self, player: int, options: CelesteGameOptions):
        self._player = player
        self._options = options

    @abstractmethod
    def generate(self, location: CelesteLocation) -> Optional[Callable[[CollectionState], bool]]:
        """Generates a lambda function that calculates a location's accessbility based on the player's items.

        Args:
            location (`CelesteLocation`): In-game location to check accessibility for.

        Returns:
            `Optional[Callable[[CollectionState], bool]]`: None if there are no access rules, and a callable otherwise.
        """
        return None


class OriginalLocationAccessor(LocationAccessor):
    """Class for generating location access rules based on original Celeste requirements."""

    def generate(self, location: CelesteLocation) -> Optional[Callable[[CollectionState], bool]]:
        conditions = []
        if not self._options.disable_heart_gates:
            if location.level.chapter == CelesteChapter.CORE:
                if location.level.side == CelesteSide.A_SIDE:
                    conditions.append(partial(lambda player, state: state.has_group("hearts", player, 4), self._player))
                if location.level.side == CelesteSide.B_SIDE:
                    conditions.append(
                        partial(lambda player, state: state.has_group("hearts", player, 15), self._player)
                    )
                if location.level.side == CelesteSide.C_SIDE:
                    conditions.append(
                        partial(lambda player, state: state.has_group("hearts", player, 23), self._player)
                    )
            if location.level.chapter == CelesteChapter.FAREWELL:
                conditions.append(partial(lambda player, state: state.has_group("hearts", player, 15), self._player))

        if location.level == self._options.get_goal_level():
            conditions.append(
                partial(
                    lambda player, value, state: state.has_group(
                        "hearts",
                        player,
                        value,
                    ),
                    self._player,
                    self._options.hearts_required.value,
                )
            )
            conditions.append(
                partial(
                    lambda player, value, state: state.has(
                        "Strawberry",
                        player,
                        value,
                    ),
                    self._player,
                    self._options.berries_required.value,
                )
            )
            conditions.append(
                partial(
                    lambda player, value, state: state.has_group(
                        "levels",
                        player,
                        value,
                    ),
                    self._player,
                    self._options.levels_required.value,
                )
            )
            conditions.append(
                partial(
                    lambda player, value, state: state.has_group(
                        "cassettes",
                        player,
                        value,
                    ),
                    self._player,
                    self._options.cassettes_required.value,
                )
            )

        if len(conditions) == 0:
            return lambda state: True

        return partial(lambda conditions, state: all(func(state) for func in conditions), conditions)
