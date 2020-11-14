# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo
# Copyright (C) 2020 Aiogram  [ actual implementation ]
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
import struct
from typing import Any, List, Optional, TypeVar, cast, overload

from aiogram.api.types.message_entity import MessageEntity
from aiogram.utils.helper import Helper, HelperMode, Item
from aiogram.utils.text_decorations import HtmlDecoration


def add_surrogate(text: str) -> str:
    return ''.join(
        ''.join(chr(y) for y in struct.unpack('<HH', x.encode('utf-16le')))
        if (0x10000 <= ord(x) <= 0x10FFFF) else x for x in text
    )


def del_surrogate(text: str) -> str:
    return text.encode('utf-16', 'surrogatepass').decode('utf-16')


class _MutableMessageEntity(MessageEntity):
    """
    Internal usage only!
    """
    class Config(MessageEntity.Config):
        allow_mutation = True


def strip_text(text: str, entities: List[_MutableMessageEntity]) -> str:
    if not entities:
        return text.strip()

    while text and text[-1].isspace():
        e = entities[-1]
        if e.offset + e.length == len(text):
            if e.length == 1:
                del entities[-1]
                if not entities:
                    return text.strip()
            else:
                e.length -= 1
        text = text[:-1]

    while text and text[0].isspace():
        for i in reversed(range(len(entities))):
            e = entities[i]
            if e.offset != 0:
                e.offset -= 1
                continue

            if e.length == 1:
                del entities[0]
                if not entities:
                    return text.lstrip()
            else:
                e.length -= 1

        text = text[1:]

    return text


class MessageEntityType(Helper):
    mode = HelperMode.snake_case

    MENTION = Item()  # mention - @username
    HASHTAG = Item()  # hashtag
    CASHTAG = Item()  # cashtag
    BOT_COMMAND = Item()  # bot_command
    URL = Item()  # url
    EMAIL = Item()  # email
    PHONE_NUMBER = Item()  # phone_number
    BOLD = Item()  # bold -  bold text
    ITALIC = Item()  # italic -  italic text
    CODE = Item()  # code - monowidth string
    PRE = Item()  # pre - monowidth block
    UNDERLINE = Item()  # underline
    STRIKETHROUGH = Item()  # strikethrough
    TEXT_LINK = Item()  # text_link -  for clickable text URLs
    TEXT_MENTION = Item()  # text_mention -  for users without usernames


@overload
def _co_entities(entities: _MutableMessageEntity) -> MessageEntity:
    ...


@overload
def _co_entities(entities: List[_MutableMessageEntity]) -> List[MessageEntity]:
    ...


def _co_entities(entities: Any) -> Any:
    """
    Convert internal-use "_MutableMessageEntity" into MessageEntity
    """
    if type(entities) is not list:
        return MessageEntity(**entities.dict())
    result = []
    for ent in entities.copy():
        result.append(MessageEntity(**ent.dict()))
    return result


def _escape_html(text: str) -> str:
    return html.escape(text, quote=False)


@overload
def _gen_writeable_ents(ents: MessageEntity) -> _MutableMessageEntity:
    ...


@overload
def _gen_writeable_ents(ents: List[MessageEntity]) -> List[_MutableMessageEntity]:
    ...


def _gen_writeable_ents(ents: Any) -> Any:
    if type(ents) is not list:
        return _MutableMessageEntity(**ents.dict())

    result = []
    for ent in ents:
        result.append(_MutableMessageEntity(**ent.dict()))
    return result


class __NoEscapeUnparse(HtmlDecoration):
    def quote(self, value: str) -> str:
        return value


_no_escape_unparse = __NoEscapeUnparse().unparse


def rm_obsolete_ents(ents: Optional[List[MessageEntity]]) -> Optional[List[MessageEntity]]:
    if not ents:
        return ents

    _acc_ents = [
        MessageEntityType.BOLD, MessageEntityType.ITALIC,
        MessageEntityType.CODE, MessageEntityType.PRE,
        MessageEntityType.UNDERLINE, MessageEntityType.STRIKETHROUGH,
        MessageEntityType.TEXT_LINK, MessageEntityType.TEXT_MENTION
    ]
    return list(filter(lambda x: x.type in _acc_ents, ents))


_L = TypeVar('_L', MessageEntity, _MutableMessageEntity)


def update_ents(entities: List[_L], offset: int, length: int, split_length: bool = True) -> List[_L]:
    result = []
    for ent in entities.copy():
        if _filter_ent(ent, offset):
            mut_ent = cast(
                _MutableMessageEntity, _gen_writeable_ents(ent) if type(ent) is not _MutableMessageEntity else ent
            )
            if mut_ent.offset + mut_ent.length >= offset:
                mut_ent.length -= length
                mut_ent.offset -= length
            elif mut_ent.offset >= offset <= mut_ent.length + mut_ent.offset:
                # look like thing is between first and end
                mut_ent.length -= round(length / 2) if split_length else length
            ent = cast(_L, _co_entities(mut_ent) if type(ent) is not _MutableMessageEntity else ent)
        result.append(ent)
    return result


def _filter_ent(_ent: MessageEntity, limit: int) -> bool:
    if _ent.offset <= limit:
        return True
    elif _ent.offset >= limit <= _ent.offset + _ent.length:
        return True
    else:
        return False
