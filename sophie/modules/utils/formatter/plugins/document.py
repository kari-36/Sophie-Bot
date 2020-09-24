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

from typing import Any, TYPE_CHECKING, Tuple

from aiogram.api.types import ContentType
from pydantic import BaseModel

from .bases import BaseFormatPlugin

if TYPE_CHECKING:
    from ..compiler import RawNoteModel, ParsedNoteModel
    from aiogram.api.types import Message

FILE_TYPES = [
    ContentType.ANIMATION, ContentType.AUDIO, ContentType.DOCUMENT, ContentType.PHOTO,
    ContentType.STICKER, ContentType.VIDEO, ContentType.VIDEO_NOTE, ContentType.VOICE
]


class DocumentModel(BaseModel):
    file_id: str
    file_type: str


class Document(BaseFormatPlugin):

    @classmethod
    async def validate(cls, message: Message, data: RawNoteModel) -> bool:
        file_id, file_type = cls.__get_fileinfo(message)
        if not (file_id and file_type):
            assert data.text is not None, 'invalid_document'
            return False

        if data.text:
            assert len(data.text) <= 1024, 'media_caption_too_long'
        data.__setattr__(
            'document', DocumentModel(file_id=file_id, file_type=file_type)
        )
        return True

    @staticmethod
    def __get_fileinfo(message: Message) -> Tuple[Any, Any]:
        for file_type in FILE_TYPES:
            if message.content_type == file_type:
                file = getattr(message, file_type)
                if isinstance(file, list):
                    file_id = file[-1].file_id
                else:
                    file_id = file.file_id
                return file_id, file_type
        else:
            return None, None

    @classmethod
    async def compile_(cls, data: RawNoteModel, payload: ParsedNoteModel) -> Any:
        if data.document is not None:
            payload.__setattr__(
                data.document.file_type,
                data.document.file_id
            )

    @classmethod
    async def decompile(cls, data: RawNoteModel, payload: ParsedNoteModel) -> Any:
        await cls.compile_(data, payload)
