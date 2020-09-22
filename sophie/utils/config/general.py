# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is part of Sophie.
#
# Contains general/Core config model

from typing import List, TYPE_CHECKING
from pydantic import BaseModel, validator, Extra

from .field import Field


class GeneralConfig(BaseModel):
    token: str = Field(None, env="TOKEN")
    owner_id: int = Field(None, env="OWNER_ID")
    operators: List[int] = Field([], env="OPERATORS")

    @validator("operators")
    def populate_operators(cls, operators: List[int], values: dict) -> List[int]:
        operators.append(values["owner_id"])
        return operators


class AdvancedConfig(BaseModel):  # Advanced settings
    debug: bool = Field(False, env="DEBUG")
    uvloop: bool = Field(False, env="UVLOOP")
    migrator: bool = Field(True, env="MIGRATOR")
    log_file: bool = Field(True, env="LOG_FILE")


class ModuleConfig(BaseModel):
    load: List[str] = Field([], env="TO_LOAD")
    dont_load: List[str] = Field([], env="DONT_LOAD")

    class Config:
        extra = Extra.allow


class ComponentConfig(BaseModel):
    if TYPE_CHECKING:
        # Dynamically filled; defined here for type hints and calming mypy

        from sophie.components.pyrogram import __config__ as pyroConfig
        pyrogram: pyroConfig

        from sophie.components.localization import __config__ as localizationConfig
        localization: localizationConfig

        from sophie.components.caching import __config__ as cacheConfig
        caching: cacheConfig

        from sophie.components.help import __config__ as HelpConfig
        help: HelpConfig  # noqa

    class Config:
        extra = Extra.allow


class MongoConfig(BaseModel):  # settings for database
    url: str = Field('localhost', env="MONGO_URL")
    namespace: str = Field('sophie', env="MONGO_NAMESPACE")
