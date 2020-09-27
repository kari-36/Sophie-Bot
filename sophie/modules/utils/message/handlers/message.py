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

from __future__ import annotations

import typing

from abc import ABC

from aiogram.dispatcher import handler

try:
    from sophie.components.localization.strings import Strings
except ImportError:
    Strings = None  # type: ignore


class MessageHandler(handler.MessageHandler, ABC):

    @property
    def args(self) -> typing.Any:
        """
        Returns Parsed arguments

        for type hints::

            from __future__ import annotations

            @parse_arguments(...)
            class SomeHandler(MessageHandler):
                args: Arguments

                class Arguments(ArgumentParser):
                    ...

        """
        return self.data.get("args")

    if Strings:
        @property
        def strings(self) -> Strings:
            """
            return localized strings of the module
            """
            return typing.cast(Strings, self.data.get("strings"))
