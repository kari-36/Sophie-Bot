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

from __future__ import annotations

import typing

from sophie.modules.utils.term import term
from sophie.modules.utils.text import FormatListText

if typing.TYPE_CHECKING:
    from aiogram import Router
    from aiogram.api.types import Message


class OwnerFunctions:
    async def __setup__(self, _: Router) -> None:
        self.term.only_owner = True  # type: ignore  # https://github.com/python/mypy/issues/2087

    @staticmethod
    async def stats(message: Message) -> typing.Any:
        from sophie.version import version
        from sophie.utils.loader import LOADED_MODULES

        text_list = FormatListText({
            'General': {
                'Version': version
            }
        }, title='Stats')

        for module in LOADED_MODULES.values():
            if 'stats' in module.data:
                text_list = module.data['stats'](text_list)

        await message.reply(text_list.text)

    @staticmethod
    async def modules(message: Message) -> typing.Any:
        from sophie.utils.loader import LOADED_MODULES

        data = []
        for module in LOADED_MODULES.values():
            args = {'ver': module.version}

            # Show database version. Reference to /sophie/utils/migrator.py
            if 'current_db_version' in module.data:
                args['db'] = module.p_object.current_db_version

            data.append((module.name, args))

        # Convert list to tuple, to make FormatListText understand this as typed list
        await message.reply(FormatListText(tuple(data), title='Loaded modules').text)

    @staticmethod
    async def term(message: Message, arg_raw: typing.Optional[str] = None) -> typing.Any:
        cmd = arg_raw
        if cmd is not None:
            text_list = FormatListText({'$': '\n' + cmd}, title='Shell')
            stdout, stderr = await term(cmd)
            text_list['stdout'] = '\n' + stdout
            text_list['stderr'] = '\n' + stderr
            await message.reply(text_list.text)
