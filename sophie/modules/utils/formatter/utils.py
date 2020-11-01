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

from typing import List, Optional, TYPE_CHECKING, TypeVar

from pydantic import Extra, validator

from .compiler import RawNoteModel
from .plugins.buttons import ButtonDataModel

if TYPE_CHECKING:
    from aiogram.api.types import MessageEntity

T = TypeVar('T')


def sort_entities(
        new_length: int, old_length: int, entities: List[MessageEntity]
) -> List[MessageEntity]:
    """
    Utility function to modify entities when you actually want to unpack entities of a modified text
    :param new_length: length of new string
    :param old_length:  length of old string
    :param entities:  .copy() of entities
    :return:
    """
    new_offset = old_length - new_length
    new = list(filter(lambda entity: entity.offset - new_offset > 0, entities))
    for ent in new:  # type: MessageEntity
        ent.__config__.allow_mutation = True
        # We have no *performant* options other than allowing mutation
        # Could do this by creating new entity objects, it would be relatively slow
        # Although, callers are free to pass a copy
        ent.offset -= new_offset  # type: ignore
    return new


class StrictRawNoteModel(RawNoteModel):
    """
    RawNoteModel is exposed to public via Import/Export or similiar
    To have maximum performance, some fields are left unchecked (not validated) by NoteCompiler

    This Model performs strong type check for possible fields that may present in RawNoteModel to avoid unhandled
    errors, and ignores extra fields getting inserted (More secure?!)
    """

    buttons: Optional[List[ButtonDataModel]]
    disable_web_page_preview: bool = False

    @validator('buttons')
    def validate_buttons(cls, value: T, values: dict) -> T:
        if not value:  # can be NoneType or empty
            plugins: list = values['plugins']
            try:
                # remove plugin
                plugins.remove('NoteButtons')
            except ValueError:
                pass
        return value

    class Config:
        extra = Extra.ignore
