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

from pathlib import Path
from typing import Any

from pydantic import BaseModel, validator


class __config__(BaseModel):
    default_language: str = 'en-US'
    languages_names_in_english: bool = False
    global_translation_path: Path = Path('sophie/modules/utils/translations')

    @validator('global_translation_path')
    def convert_path(cls, value: Any) -> Any:
        if isinstance(value, str):
            return Path(value)
        return value
