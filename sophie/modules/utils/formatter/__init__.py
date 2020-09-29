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

from typing import List, TYPE_CHECKING

from . import help
from .plugins.bases import BaseFormatPlugin
from .plugins.buttons import BaseNoteButton
from .format import Format

if TYPE_CHECKING:
    from aiogram.api.types import MessageEntity


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


__all__ = ["BaseFormatPlugin", "BaseNoteButton", "Format", "sort_entities"]
