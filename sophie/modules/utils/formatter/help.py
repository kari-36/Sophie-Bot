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

from contextlib import suppress
from typing import Dict

try:
    from sophie.components.help.decorators import include_help
    from sophie.components.localization import GetString
    from sophie.components.localization.loader import LANGUAGES

except ImportError:
    pass

else:
    @include_help('formatting')
    async def formatting_help() -> Dict[str, str]:
        payload = {}
        for locale in LANGUAGES:
            with suppress(KeyError):
                _help = await GetString('formatting_help', locale_code=locale)
                payload[locale] = _help
        return payload
