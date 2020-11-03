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
import html
from typing import List
import struct

from aiogram.api.types.message_entity import MessageEntity
from aiogram.utils.helper import Helper, HelperMode, Item


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


def _co_entities(entities: List[_MutableMessageEntity]) -> List[MessageEntity]:
    """
    Convert internal-use "_MutableMessageEntity" into MessageEntity
    """
    result = []
    for ent in entities:
        result.append(MessageEntity(**ent.dict()))
    return result


def _escape_html(text: str) -> str:
    return html.escape(text, quote=False)
