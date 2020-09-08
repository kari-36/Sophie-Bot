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

import re
from typing import Any, Callable, Generator, Literal, TYPE_CHECKING, Union

from .plugins.bases import get_all_plugins

if TYPE_CHECKING:
    from aiogram.api.types import Message
    from .compiler import RawNoteModel


class _Validate:

    async def __call__(
            self, message: Message, data: RawNoteModel
    ) -> bool:

        self.message = message
        self.data = data

        return await self.validate()

    @classmethod
    def __get_validator(cls, validator: Callable[..., Any]) -> Union[Literal[False], Callable[..., Any]]:
        from inspect import signature
        args = set(list(signature(validator).parameters.keys())[1:])

        if args == {}:
            return lambda message, match, data: validator(message)
        elif args == {'match'}:
            return lambda message, match, data: validator(message, match=match)
        elif args == {'data'}:
            return lambda message, match, data: validator(message, data=data)
        elif args == {'match', 'data'}:
            return lambda message, match, data: validator(message, match=match, data=data)
        else:
            return False

    async def validate(self) -> bool:
        for plugin in get_all_plugins():
            if validator := self.__get_validator(plugin.validate):
                if plugin.__syntax__:
                    if self.data.text is not None:
                        for match in re.finditer(plugin.__syntax__, self.data.text):
                            try:
                                await validator(self.message, match, self.data)
                            except (TypeError, ValueError, AssertionError):
                                return False
                else:
                    try:
                        await validator(self.message, None, self.data)
                    except (TypeError, ValueError, AssertionError):
                        return False
        return True

    def __await__(self, message: Message, data: RawNoteModel) -> Generator[Any, None, bool]:
        return self.__call__(message, data).__await__()


validate = _Validate()

__all__ = ["validate"]
