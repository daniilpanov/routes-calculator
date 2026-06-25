from dataclasses import dataclass

from module_shared.schemas.setting import SettingType


@dataclass(frozen=True)
class SettingDefinition:
    group: str
    name: str
    value_type: SettingType
    default: str
    description: str


SETTING_DEFINITIONS: list[SettingDefinition] = [
    SettingDefinition(
        group="feature-flag",
        name="hide-sea-soc",
        value_type=SettingType.BOOL,
        default="false",
        description="Hide sea SOC segments from combined sea+rail route calculation",
    ),
]


def get_setting_definitions() -> list[SettingDefinition]:
    return SETTING_DEFINITIONS


def get_setting_definition(group: str, name: str) -> SettingDefinition | None:
    for defn in SETTING_DEFINITIONS:
        if defn.group == group and defn.name == name:
            return defn
    return None
