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
from typing import Any, Match, Optional, TYPE_CHECKING

from .bases import BaseFormatPlugin

if TYPE_CHECKING:
    from ..compiler import ParsedNoteModel, RawNoteModel


class WebPreview(BaseFormatPlugin):
    __syntax__: re.Pattern = re.compile("[%|$]PREVIEW")

    @classmethod
    async def validate(cls, match: Optional[Match], data: RawNoteModel) -> Any:
        if match:
            data.__setattr__('web_preview', True)
            if data.text:
                data.text = re.sub('%PREVIEW', '', data.text)

    @classmethod
    async def compile_(cls, data: RawNoteModel, payload: ParsedNoteModel) -> Any:
        if preview := getattr(data, 'web_preview', None) and not data.document:
            payload.__setattr__('disable_web_page_preview', preview)

    @classmethod
    async def decompile(cls, data: RawNoteModel, payload: ParsedNoteModel) -> Any:
        if preview := getattr(data, 'web_preview', None):
            if preview is True and payload.text is not None:
                payload.text += "\n%PREVIEW"
