# Copyright (C) 2018 - 2020 MrYacha.
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

from typing import Any, TYPE_CHECKING, Type

from sophie.utils.logging import log
from sophie.utils.bases import BaseComponent

from .config import __config__

if TYPE_CHECKING:
    from . import strings

    get_string_dec: strings.get_strings_dec  # type: ignore
    Strings: Type[strings.Strings]
    GetStrings: Type[strings.GetStrings]
    GetString: Type[strings.GetString]


class Component(BaseComponent):
    configurations = __config__

    async def __setup__(*args: Any, **kwargs: Any) -> Any:
        from .loader import __setup__ as load_all_languages
        from .db import __setup__ as database

        log.debug('Loading localizations...')
        load_all_languages()
        log.debug('...Done!')

        log.debug('Loading database...')
        await database()
        log.debug('...Done!')

        return True

    @classmethod
    def __pre_init__(cls, module: Any) -> Any:
        from . import strings

        module.get_string_dec = strings.get_strings_dec
        module.Strings = strings.Strings
        module.GetStrings = strings.GetStrings
        module.GetString = strings.GetString
