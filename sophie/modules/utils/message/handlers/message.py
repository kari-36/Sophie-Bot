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


_T = typing.TypeVar('_T')


class MessageHandler(handler.MessageHandler, typing.Generic[_T], ABC):

    @property
    def args(self) -> _T:
        value = self.data.get("args", None)
        if value is None:
            raise ValueError(
                f"Unable to fetch arg data in {self.__class__.__name__}"
                "Makes sure you have passed Argument model to filter."
            )
        return typing.cast(_T, value)

    if Strings:
        @property
        def strings(self) -> Strings:
            """
            return localized strings of the module
            """
            return typing.cast(Strings, self.data.get("strings"))
