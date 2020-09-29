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
from typing import Callable, List, Literal, Optional, TYPE_CHECKING, Tuple, Union

from sophie.components.localization import GetString

from .compiler import RawNoteModel
from .parser import HTML, Markdown, ParseError, UnpackEntitiesHTML, UnpackEntitiesMD
from .validator import validate

if TYPE_CHECKING:
    from aiogram.api.types import Message, MessageEntity


class _Format:

    def __init__(self, default_parser: Literal['md', 'html', 'none']):
        self._default_parser = default_parser

    async def __call__(
            self,
            message: Message,
            text: Optional[str] = None,
            entities: Optional[List[MessageEntity]] = None,
            excluded_plugins: Optional[List[str]] = None,
            included_plugins: Optional[List[str]] = None
    ) -> Union[RawNoteModel, Literal[False]]:
        self._message = message
        self._text = text  # should pass text if. and enitities must unparsed in HTML
        self.entities = entities

        if excluded_plugins and included_plugins:
            raise ValueError(
                "Expected either `excluded_plugins` or `included_plugins`, not both!"
            )
        self.excluded_plugins = excluded_plugins
        self.included_plugins = included_plugins

        return await self.parse()

    async def parse(self) -> Union[RawNoteModel, Literal[False]]:
        parser = self.get_parse_mode
        data = RawNoteModel(text=self._text)

        if not await validate(self._message, data, self.excluded_plugins, self.included_plugins):
            return False

        if self._text and data.text:
            if parser in ('html', 'md', 'markdown'):
                callback, entities = self.get_parser
                try:
                    data.text = callback(entities.unparse(data.text, self.entities))
                except ParseError as error:
                    await self._message.answer(
                        (
                            await GetString("compilation_error", chat_id=self._message.chat.id)
                        ).format(error=html.escape(error.text, quote=False))
                    )
                    return False
            else:
                data.text = html.escape(data.text, quote=False)
        return data

    @property
    def get_parse_mode(self) -> str:
        if not self._text:
            return self._default_parser

        match = re.search(r'%PARSEMODE_(?P<parse_mode>\w+)', self._text)
        if match is not None:
            if (mode := match.group('parse_mode')) is not None:
                if mode.lower() in {'md', 'html', 'none', 'markdown'}:
                    self._text = re.sub(r'%PARSEMODE_(?P<parse_mode>\w+)\s?', '', self._text, 1)  # noqa
                    return mode.lower()
        return self._default_parser

    @property
    def get_parser(self) -> Tuple[Callable[[str], str], Union[UnpackEntitiesMD, UnpackEntitiesHTML]]:
        parser = self.get_parse_mode
        if parser == 'html':
            return HTML.parse, UnpackEntitiesHTML()
        return Markdown.parse, UnpackEntitiesMD()


Format = _Format(default_parser='html')
