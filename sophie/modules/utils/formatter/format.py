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

import html
import re

from typing import Any, Generator, Literal, Optional, TYPE_CHECKING, Union

from .parser import ParseError
from .validator import validate
from .compiler import RawNoteModel

if TYPE_CHECKING:
    from aiogram.api.types import Message


class _Format:

    def __init__(self, default_parser: Literal['md', 'html', 'none']):
        self._default_parser = default_parser

    async def __call__(
            self, message: Message, text: Optional[str] = None
    ) -> Union[RawNoteModel, Literal[False]]:
        self._message = message
        self._text = text or message.text or message.caption
        return await self.parse()

    def __get_parse_mode(self) -> str:
        if not self._text:
            return self._default_parser

        match = re.search(r'%PARSEMODE_(?P<parse_mode>\w+)', self._text)
        if match is not None:
            if (mode := match.group('parse_mode')) is not None:
                if mode.lower() in {'md', 'html', 'none'}:
                    self._text = re.sub(r'%PARSEMODE_(?P<parse_mode>\w+)\s?', '', self._text, 1)
                    return mode.lower()
        return self._default_parser

    async def parse(self) -> Union[RawNoteModel, Literal[False]]:
        parser = self.__get_parse_mode()
        data = RawNoteModel(text=self._text)

        if await validate(self._message, data):
            if self._text and data.text:

                if parser == 'html':
                    from .parser import HTML, UnpackEntitiesHTML
                    try:
                        data.text = HTML.parse(
                            UnpackEntitiesHTML().unparse(
                                data.text,
                                self._message.entities or self._message.caption_entities
                            )
                        )
                    except ParseError as error:
                        await self._message.answer(f"Unable to compile: {html.escape(error.text, False)}")
                        return False

                elif parser == 'md':
                    from .parser import Markdown, UnpackEntitiesMD

                    data.text = Markdown.parse(
                        UnpackEntitiesMD().unparse(
                            data.text,
                            self._message.entities or self._message.caption_entities
                        )
                    )

                else:
                    data.text = html.escape(data.text, quote=False)

        return data

    def __await__(
            self, message: Message, text: Optional[str] = None
    ) -> Generator[Any, None, Union[RawNoteModel, Literal[False]]]:

        return self.__call__(message, text).__await__()


Format = _Format(default_parser='md')
