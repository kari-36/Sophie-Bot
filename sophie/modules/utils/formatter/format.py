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
from typing import List, Literal, Optional, TYPE_CHECKING, Union

from .compiler import RawNoteModel
from .parser import parse_html, parse_markdown
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
        self.message = message
        self.text = text  # should pass text if. and enitities must unparsed in HTML
        self.entities = entities

        if excluded_plugins and included_plugins:
            raise ValueError(
                "Expected either `excluded_plugins` or `included_plugins`, not both!"
            )
        self.excluded_plugins = excluded_plugins
        self.included_plugins = included_plugins

        return await self.parse()

    async def parse(self) -> Union[RawNoteModel, Literal[False]]:
        parser = self.get_parse_mode()  # noqa
        data = RawNoteModel(text=self.text)

        if not await validate(self.message, data, self.excluded_plugins, self.included_plugins):
            return False

        if self.text and data.text:
            if parser in ('md', 'markdown'):
                data.text, data.entities = parse_markdown(data.text)
            elif parser in ('html',):
                data.text, data.entities = parse_html(data.text)
            # merge entities
            if self.entities and data.entities is not None:
                data.entities.extend(self.entities)
        return data

    def get_parse_mode(self) -> str:
        if not self.text:
            return self._default_parser

        match = re.search(r'%PARSEMODE_(?P<parse_mode>\w+)', self.text)
        if match is not None:
            if (mode := match.group('parse_mode')) is not None:
                if mode.lower() in {'md', 'html', 'none', 'markdown'}:
                    self.text = re.sub(r'%PARSEMODE_(?P<parse_mode>\w+)\s?', '', self.text, 1)  # noqa
                    return mode.lower()
        return self._default_parser


Format = _Format(default_parser='html')
