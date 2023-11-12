# pylint: disable=missing-class-docstring, missing-module-docstring, fixme, unused-import

from typing import Dict, Union

from BaseClasses import MultiWorld
from Options import Choice, DefaultOnToggle, Range, Toggle


class BerriesRequired(Range):
    """Number of Strawberries required to access the final level for the World."""

    display_name = "Strawberry Requirement"
    range_start = 0
    range_end = 175
    default = 0


class CassettesRequired(Range):
    """Number of Cassettes required to access the final level for the World."""

    display_name = "Cassette Requirement"
    range_start = 0
    range_end = 8
    default = 0


class HeartsRequired(Range):
    """Number of Crystal Hearts required to access the final level for the World."""

    display_name = "Crystal Heart Requirement"
    range_start = 0
    range_end = 24
    default = 15


class LevelsRequired(Range):
    """Number of Level Completions required to access the final level for the World."""

    display_name = "Level Completion Requirement"
    range_start = 0
    range_end = 24
    default = 0


class CassettesRandomised(Toggle):
    """Selects whether Cassettes should have their Locations frozen from randomisation."""

    display_name = "Freeze B-Side Cassettes"
    option_false = 0
    option_true = 1
    default = 0


class HeartsRandomised(Toggle):
    """Selects whether Crystal Hearts should have their Locations frozen from randomisation."""

    display_name = "Freeze Crystal Hearts"
    option_false = 0
    option_true = 1
    default = 0


class VictoryCondition(Choice):
    """Selects the Chapter whose Completion is the Victory Condition for the World."""

    display_name = "Victory Condition"
    option_chapter_7_summit = 0
    option_chapter_8_core = 1
    option_chapter_9_farewell = 2
    default = 0


class StrawberryUnlockOldSiteCost(Range):
    """Strawberry Unlock Method: Number of Strawberries required to unlock Chapter 2: Old Site"""

    display_name = "Strawberry Unlock: Old Site Cost"
    range_start = 0
    range_end = 20
    default = 10


class StrawberryUnlockCelestialResortCost(Range):
    """Strawberry Unlock Method: Number of Strawberries required to unlock Chapter 3: Celestial Resort"""

    display_name = "Strawberry Unlock: Celestial Resort Cost"
    range_start = 0
    range_end = 38
    default = 19


class StrawberryUnlockGoldenRidgeCost(Range):
    """Strawberry Unlock Method: Number of Strawberries required to unlock Chapter 4: Golden Ridge"""

    display_name = "Strawberry Unlock: Golden Ridge Cost"
    range_start = 0
    range_end = 63
    default = 32


class StrawberryUnlockMirrorTempleCost(Range):
    """Strawberry Unlock Method: Number of Strawberries required to unlock Chapter 5: Mirror Temple"""

    display_name = "Strawberry Unlock: Mirror Temple Cost"
    range_start = 0
    range_end = 92
    default = 46


class StrawberryUnlockReflectionCost(Range):
    """Strawberry Unlock Method: Number of Strawberries required to unlock Chapter 6: Reflection"""

    display_name = "Strawberry Unlock: Reflection Cost"
    range_start = 0
    range_end = 123
    default = 62


class StrawberryUnlockSummitCost(Range):
    """Strawberry Unlock Method: Number of Strawberries required to unlock Chapter 7: The Summit"""

    display_name = "Strawberry Unlock: The Summit Cost"
    range_start = 0
    range_end = 123
    default = 63


class StrawberryUnlockCoreCost(Range):
    """Strawberry Unlock Method: Number of Strawberries required to unlock Chapter 9: Core"""

    display_name = "Strawberry Unlock: Core Cost"
    range_start = 0
    range_end = 170
    default = 85


class StrawberryUnlockFarewellCost(Range):
    """Strawberry Unlock Method: Number of Strawberries required to unlock Chapter 10: Farewell"""

    display_name = "Strawberry Unlock: Farewell Cost"
    range_start = 0
    range_end = 175
    default = 88


celeste_options: Dict[str, type] = {
    "berries_required": BerriesRequired,
    "cassettes_required": CassettesRequired,
    "hearts_required": HeartsRequired,
    "levels_required": LevelsRequired,
    "sbunlock_2A_cost": StrawberryUnlockOldSiteCost,
    "sbunlock_3A_cost": StrawberryUnlockCelestialResortCost,
    "sbunlock_4A_cost": StrawberryUnlockGoldenRidgeCost,
    "sbunlock_5A_cost": StrawberryUnlockMirrorTempleCost,
    "sbunlock_6A_cost": StrawberryUnlockReflectionCost,
    "sbunlock_7A_cost": StrawberryUnlockSummitCost,
    "sbunlock_9A_cost": StrawberryUnlockFarewellCost,
}


def is_option_enabled(world: MultiWorld, player: int, name: str) -> bool:
    return get_option_value(world, player, name) > 0


def get_option_value(world: MultiWorld, player: int, name: str) -> Union[bool, int]:
    option = getattr(world, name, None)

    if option is None:
        return 0

    if issubclass(celeste_options[name], Toggle) or issubclass(celeste_options[name], DefaultOnToggle):
        return bool(option[player].value)
    return option[player].value
