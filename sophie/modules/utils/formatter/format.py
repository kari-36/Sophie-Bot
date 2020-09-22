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

from typing import List, Literal, Optional, TYPE_CHECKING, Union

from .parser import HTML, Markdown, ParseError
from .validator import validate
from .compiler import RawNoteModel

if TYPE_CHECKING:
    from aiogram.api.types import Message


class _Format:

    def __init__(self, default_parser: Literal['md', 'html', 'none']):
        self._default_parser = default_parser

    async def __call__(
            self,
            message: Message,
            text: Optional[str] = None,
            parse_mode: Optional[str] = None,
            excluded_plugins: Optional[List[str]] = None,
            included_plugins: Optional[List[str]] = None
    ) -> Union[RawNoteModel, Literal[False]]:
        self._message = message
        self._text = text  # should pass text if. and enitities must unparsed in HTML
        self.parse_mode = parse_mode

        if excluded_plugins and included_plugins:
            raise ValueError(
                "Expected either `excluded_plugins` or `included_plugins`, not both!"
            )
        self.excluded_plugins = excluded_plugins
        self.included_plugins = included_plugins

        return await self.parse()

    async def parse(self) -> Union[RawNoteModel, Literal[False]]:
        parser = self.parse_mode or self._default_parser
        data = RawNoteModel(text=self._text)

        if not await validate(self._message, data, self.excluded_plugins, self.included_plugins):
            return False

        if self._text and data.text:
            if parser in ('html', 'md', 'markdown'):
                callback = HTML.parse if parser == 'html' else Markdown.parse
                try:
                    data.text = callback(data.text)
                except ParseError as error:
                    await self._message.answer(f"Unable to compile: {html.escape(error.text, False)}")
                    return False
            else:
                data.text = html.escape(data.text, quote=False)
        return data


Format = _Format(default_parser='html')
