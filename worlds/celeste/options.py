# pylint: disable=missing-class-docstring, missing-module-docstring, fixme, unused-import

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Union

from BaseClasses import MultiWorld
from Options import Choice, DefaultOnToggle, PerGameCommonOptions, Range, Toggle
from worlds.celeste.data import CelesteChapter, CelesteLevel, CelesteSide


class BerriesRequired(Range):
    """Number of Strawberries required to access the goal level."""

    display_name = "Strawberry Requirement"
    range_start = 0
    range_end = 175
    default = 0


class CassettesRequired(Range):
    """Number of Cassettes required to access the goal level."""

    display_name = "Cassette Requirement"
    range_start = 0
    range_end = 8
    default = 0


class HeartsRequired(Range):
    """Number of Crystal Hearts required to access the goal level."""

    display_name = "Crystal Heart Requirement"
    range_start = 0
    range_end = 24
    default = 0


class LevelsRequired(Range):
    """Number of Level Completions required to access the goal level."""

    display_name = "Level Completion Requirement"
    range_start = 0
    range_end = 25
    default = 0


class GoalLevel(Choice):
    """Selects the Level whose Completion is the Victory Condition for the World."""

    display_name = "Victory Condition"
    option_chapter_7_summit_a = 0
    option_chapter_8_core_a = 1
    option_chapter_9_farewell_a = 2
    option_chapter_7_summit_b = 3
    option_chapter_8_core_b = 4
    option_chapter_7_summit_c = 5
    option_chapter_8_core_c = 6
    default = 0


class ProgressionSystem(Choice):
    """Selects the Progression System for the World."""

    display_name = "Progression System"
    option_default_progression = 0
    default = 0


class DisableHeartGates(Toggle):
    """Disables heart gates in Core and Farewell."""

    display_name = "Disable Heart Gates"


@dataclass
class CelesteGameOptions(PerGameCommonOptions):
    berries_required: BerriesRequired
    cassettes_required: CassettesRequired
    hearts_required: HeartsRequired
    levels_required: LevelsRequired
    goal_level: GoalLevel
    progression_system: ProgressionSystem
    disable_heart_gates: DisableHeartGates

    @staticmethod
    def upgrade(options: PerGameCommonOptions) -> "CelesteGameOptions":
        return CelesteGameOptions(
            options.progression_balancing,
            options.accessibility,
            options.local_items,
            options.non_local_items,
            options.start_inventory,
            options.start_hints,
            options.start_location_hints,
            options.exclude_locations,
            options.priority_locations,
            options.item_links,
            berries_required=BerriesRequired(BerriesRequired.default),
            cassettes_required=CassettesRequired(CassettesRequired.default),
            hearts_required=HeartsRequired(HeartsRequired.default),
            levels_required=LevelsRequired(LevelsRequired.default),
            goal_level=GoalLevel(GoalLevel.default),
            progression_system=ProgressionSystem(ProgressionSystem.default),
            disable_heart_gates=DisableHeartGates(DisableHeartGates.default),
        )

    _goal_level_map = {
        GoalLevel.option_chapter_7_summit_a: CelesteLevel(CelesteChapter.THE_SUMMIT, CelesteSide.A_SIDE),
        GoalLevel.option_chapter_7_summit_b: CelesteLevel(CelesteChapter.THE_SUMMIT, CelesteSide.B_SIDE),
        GoalLevel.option_chapter_7_summit_c: CelesteLevel(CelesteChapter.THE_SUMMIT, CelesteSide.C_SIDE),
        GoalLevel.option_chapter_8_core_a: CelesteLevel(CelesteChapter.CORE, CelesteSide.A_SIDE),
        GoalLevel.option_chapter_8_core_b: CelesteLevel(CelesteChapter.CORE, CelesteSide.B_SIDE),
        GoalLevel.option_chapter_8_core_c: CelesteLevel(CelesteChapter.CORE, CelesteSide.C_SIDE),
        GoalLevel.option_chapter_9_farewell_a: CelesteLevel(CelesteChapter.FAREWELL, CelesteSide.A_SIDE),
    }

    def get_goal_level(self) -> CelesteLevel:
        return CelesteGameOptions._goal_level_map[self.goal_level.value]
