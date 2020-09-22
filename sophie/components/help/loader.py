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

from typing import Dict
from .decorators import EXTERNAL_HELPFUNCS

DATA: Dict[str, Dict[str, str]] = {}


async def load() -> None:
    from sophie.utils.loader import LOADED_MODULES

    # load help from translations
    for module, module_data in LOADED_MODULES.items():
        if 'translations' not in module_data.data:
            continue

        for locale, trans in module_data.data['translations'].items():  # type: str, Dict[str, str]
            if 'HELP' in trans:
                data = {locale: trans['HELP']}

                if module in DATA:
                    DATA[module.capitalize()].update(data)
                else:
                    DATA[module.capitalize()] = data

    # load help from external help funcs
    for module, func in EXTERNAL_HELPFUNCS.items():
        DATA[module.capitalize()] = await func()
