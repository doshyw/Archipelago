import json
import pkgutil
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from BaseClasses import Item, ItemClassification, Location, Region

_PATH_ITEM_DATA = str(Path("data", "items.json"))
_PATH_REGION_DATA = str(Path("data", "regions.json"))

_OFFSET_BASE = 8000000
_OFFSET_TYPE = 20000
_OFFSET_LEVEL = 1000
_OFFSET_SIDE = 100

_COLUMN_ITEM_TYPE = "type"
_COLUMN_LEVEL = "level"
_COLUMN_SIDE = "side"
_COLUMN_OFFSET = "offset"
_COLUMN_ITEM_NAME = "item_name"
_COLUMN_LOCATION_NAME = "location_name"
_COLUMN_REGION_NAME = "region_name"


def _get_json_data(location: str) -> List[Dict[str, Any]]:
    byte_data = pkgutil.get_data(__name__, location)
    return json.loads(byte_data)


@total_ordering
class CelesteChapter(Enum):
    def __eq__(self, other) -> bool:
        if not isinstance(other, CelesteChapter):
            return False
        return self.value == other.value

    def __lt__(self, other) -> bool:
        if not isinstance(other, CelesteChapter):
            return False
        return self.value < other.value

    def previous(self) -> "CelesteChapter":
        if self.value <= 10 and self.value > 0:
            return CelesteChapter(self.value - 1)
        else:
            return self

    PROLOGUE = 0
    FORSAKEN_CITY = 1
    OLD_SITE = 2
    CELESTIAL_RESORT = 3
    GOLDEN_RIDGE = 4
    MIRROR_TEMPLE = 5
    REFLECTION = 6
    THE_SUMMIT = 7
    EPILOGUE = 8
    CORE = 9
    FAREWELL = 10
    NOT_APPLICABLE = 19


class CelesteSide(Enum):
    def __eq__(self, other) -> bool:
        if not isinstance(other, CelesteSide):
            return False
        return self.value == other.value

    def __lt__(self, other) -> bool:
        if not isinstance(other, CelesteSide):
            return False
        return self.value < other.value

    A_SIDE = 0
    B_SIDE = 1
    C_SIDE = 2


@dataclass
@total_ordering
class CelesteLevel:
    """Class representing a playable level in Celeste.

    Properties:
        chapter (`CelesteChapter`): The chapter that the level is in.
        side (`CelesteSide`): The side that the level is on.
    """

    chapter: CelesteChapter
    side: CelesteSide

    def __eq__(self, other) -> bool:
        if not isinstance(other, CelesteLevel):
            return False
        return self.chapter == other.chapter and self.side == other.side

    def __lt__(self, other) -> bool:
        if not isinstance(other, CelesteLevel):
            return False
        return self.chapter < other.chapter or (self.chapter == other.chapter and self.side < other.side)


class CelesteItemType(Enum):
    VICTORY = 0
    CASSETTE = 1
    COMPLETION = 2
    GEMHEART = 3
    STRAWBERRY = 4


STRAWBERRY_UUID = (
    _OFFSET_BASE + _OFFSET_TYPE * CelesteItemType.STRAWBERRY.value + _OFFSET_LEVEL * CelesteChapter.NOT_APPLICABLE.value
)

VICTORY_UUID = (
    _OFFSET_BASE
    + _OFFSET_TYPE * CelesteItemType.VICTORY.value
    + _OFFSET_LEVEL * CelesteChapter.FAREWELL.value
    + _OFFSET_SIDE * CelesteSide.B_SIDE.value
)


class CelesteItem(Item):
    game: str = "Celeste"
    item_type: CelesteItemType
    level: CelesteLevel

    def __init__(
        self,
        name: str,
        classification: ItemClassification,
        code: Optional[int],
        player: int,
        item_type: CelesteItemType,
        level: CelesteLevel,
    ):
        super().__init__(name, classification, code, player)
        self.item_type = item_type
        self.level = level

    def copy(self) -> "CelesteItem":
        return CelesteItem(self.name, self.classification, self.code, self.player, self.item_type, self.level)


class CelesteLocation(Location):
    game: str = "Celeste"
    level: CelesteLevel

    # override constructor to automatically mark event locations as such
    def __init__(
        self,
        player: int,
        level: CelesteLevel,
        name: str = "",
        code: Optional[int] = None,
        parent: Optional[Region] = None,
    ):
        super().__init__(player, name, code, parent)
        self.level = level
        self.event = code is None


class BaseData:
    _generated = False

    _item_data = _get_json_data(_PATH_ITEM_DATA)
    _region_data = _get_json_data(_PATH_REGION_DATA)
    _item_lookup: Dict[int, Dict[str, Any]] = {}
    _region_lookup: Dict[int, Dict[str, Any]] = {}

    _item_name_to_id: Dict[str, int] = {}
    _location_name_to_id: Dict[str, int] = {}

    @classmethod
    def _generate_lookups(cls):
        for row in cls._item_data:
            uuid = cls.item_hash(
                item_type=CelesteItemType[row[_COLUMN_ITEM_TYPE].upper()],
                level=CelesteChapter(row[_COLUMN_LEVEL]),
                side=CelesteSide(row[_COLUMN_SIDE]),
                offset=row[_COLUMN_OFFSET],
            )
            cls._location_name_to_id[row[_COLUMN_LOCATION_NAME]] = uuid
            cls._item_lookup[uuid] = row
            if row[_COLUMN_ITEM_TYPE] != "strawberry":
                cls._item_name_to_id[row[_COLUMN_ITEM_NAME]] = uuid

        cls._item_name_to_id["Strawberry"] = STRAWBERRY_UUID

        for row in cls._region_data:
            uuid = cls._region_hash(CelesteChapter(row[_COLUMN_LEVEL]), CelesteSide(row[_COLUMN_SIDE]))
            cls._region_lookup[uuid] = row

        cls._generated = True

    @classmethod
    def item_hash(cls, item_type: CelesteItemType, level: CelesteChapter, side: CelesteSide, offset: int) -> int:
        return (
            _OFFSET_BASE
            + _OFFSET_TYPE * item_type.value
            + _OFFSET_LEVEL * level.value
            + _OFFSET_SIDE * side.value
            + offset
        )

    @classmethod
    def _region_hash(cls, level: CelesteChapter, side: CelesteSide) -> int:
        return _OFFSET_LEVEL * level.value + _OFFSET_SIDE * side.value

    @classmethod
    def _lookup_value(cls, uuid: int, column: str) -> Any:
        if not cls._generated:
            cls._generate_lookups()
        return cls._item_lookup[uuid][column]

    @classmethod
    def item_name(cls, item_type: CelesteItemType, level: CelesteChapter, side: CelesteSide, offset: int = 0) -> str:
        if not cls._generated:
            cls._generate_lookups()
        if item_type == CelesteItemType.STRAWBERRY:
            return "Strawberry"
        return cls._lookup_value(cls.item_hash(item_type, level, side, offset), _COLUMN_ITEM_NAME)

    @classmethod
    def location_name(
        cls, item_type: CelesteItemType, level: CelesteChapter, side: CelesteSide, offset: int = 0
    ) -> str:
        if not cls._generated:
            cls._generate_lookups()
        return cls._lookup_value(cls.item_hash(item_type, level, side, offset), _COLUMN_LOCATION_NAME)

    @classmethod
    def region_name(cls, level: CelesteChapter, side: CelesteSide) -> str:
        if not cls._generated:
            cls._generate_lookups()
        return cls._region_lookup[cls._region_hash(level, side)][_COLUMN_REGION_NAME]

    @classmethod
    def item_name_to_id(cls) -> Dict[str, int]:
        if not cls._generated:
            cls._generate_lookups()
        return cls._item_name_to_id

    @classmethod
    def location_name_to_id(cls) -> Dict[str, int]:
        if not cls._generated:
            cls._generate_lookups()
        return cls._location_name_to_id

    @classmethod
    def get_item(cls, uuid: int) -> Tuple[CelesteItemType, CelesteLevel, str, int]:
        if not cls._generated:
            cls._generate_lookups()

        if uuid == STRAWBERRY_UUID:
            return (
                CelesteItemType.STRAWBERRY,
                CelesteLevel(CelesteChapter.NOT_APPLICABLE, CelesteSide.A_SIDE),
                "Strawberry",
                STRAWBERRY_UUID,
            )

        item_dict = cls._item_lookup[uuid]

        return (
            CelesteItemType[item_dict[_COLUMN_ITEM_TYPE].upper()],
            CelesteLevel(CelesteChapter(item_dict[_COLUMN_LEVEL]), CelesteSide(item_dict[_COLUMN_SIDE])),
            item_dict[_COLUMN_ITEM_NAME],
            uuid,
        )

    @classmethod
    def items(
        cls,
    ) -> List[Tuple[CelesteItemType, CelesteLevel, str, int]]:
        if not cls._generated:
            cls._generate_lookups()

        item_list = []
        for uuid, row in sorted(cls._item_lookup.items()):
            if row[_COLUMN_ITEM_TYPE] == "strawberry":
                continue
            item_list.append(cls.get_item(uuid))

        for row in cls._item_data:
            if row[_COLUMN_ITEM_TYPE] != "strawberry":
                continue
            item_list.append(
                (
                    CelesteItemType.STRAWBERRY,
                    CelesteLevel(CelesteChapter(row[_COLUMN_LEVEL]), CelesteSide(row[_COLUMN_SIDE])),
                    "Strawberry",
                    STRAWBERRY_UUID,
                )
            )

        return item_list

    @classmethod
    def locations(
        cls,
    ) -> List[Tuple[CelesteLevel, str, int]]:
        if not cls._generated:
            cls._generate_lookups()

        return [
            (
                CelesteLevel(CelesteChapter(row[_COLUMN_LEVEL]), CelesteSide(row[_COLUMN_SIDE])),
                row[_COLUMN_LOCATION_NAME],
                uuid,
            )
            for uuid, row in sorted(cls._item_lookup.items())
        ]

    @classmethod
    def regions(
        cls,
    ) -> List[Tuple[CelesteLevel, str]]:
        if not cls._generated:
            cls._generate_lookups()

        return [
            (CelesteLevel(CelesteChapter(row[_COLUMN_LEVEL]), CelesteSide(row[_COLUMN_SIDE])), row[_COLUMN_REGION_NAME])
            for uuid, row in sorted(cls._region_lookup.items())
        ]
