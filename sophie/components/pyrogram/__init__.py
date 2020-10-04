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

import typing

from sophie.utils.bases import BaseComponent
from sophie.utils.logging import log

from .config import __config__
from .owner_functions import OwnerFunctions

if typing.TYPE_CHECKING:
    from pyrogram import Client
    pbot: Client


class Component(BaseComponent):
    configurations = __config__

    @classmethod
    def __pre_init__(cls, module: typing.Any) -> typing.Any:
        from .pyrogram import pbot

        module.pbot = pbot

    async def __setup__(*args: typing.Any, **kwargs: typing.Any) -> None:
        from .pyrogram import pbot

        log.debug('Starting 🔥Pyrogram...')
        await pbot.start()
