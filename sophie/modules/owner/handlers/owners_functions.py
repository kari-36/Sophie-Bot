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

import html
import typing

from kantex.html import Bold, Code, Item, KeyValueItem, Section, SubSection
from sophie.modules.utils.term import term

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

        text_list = Section(
            "Stats", SubSection(
                "General", KeyValueItem(
                    Bold("version"), version
                )
            )
        )

        for module in LOADED_MODULES.values():
            if 'stats' in module.data:
                text_list.append(module.data['stats']())
        await message.reply(str(text_list))

    @staticmethod
    async def modules(message: Message) -> typing.Any:
        from sophie.utils.loader import LOADED_MODULES

        document = Section("Loader Modules")
        for module in LOADED_MODULES.values():
            mod_doc = SubSection(
                module.name, KeyValueItem(
                    "version", module.version
                )
            )

            # Show database version. Reference to /sophie/utils/migrator.py
            if 'current_db_version' in module.data:
                mod_doc.append(KeyValueItem(
                    "database", module.data['current_db_version']
                ))

            document.append(mod_doc)

        # Convert list to tuple, to make FormatListText understand this as typed list
        await message.reply(str(document))

    @staticmethod
    async def term(message: Message, arg_raw: typing.Optional[str] = None) -> typing.Any:
        cmd = arg_raw
        if cmd is not None:
            stdout, stderr = await term(cmd)
            doc = Section(
                "Shell", SubSection(
                    "$", Code(
                        html.escape(cmd, quote=False)
                    )
                ),
                SubSection(
                    "stdout", Item(
                        stdout
                    )
                ),
                SubSection(
                    "stderr", Item(
                        stderr
                    )
                )
            )
            await message.reply(str(doc))
