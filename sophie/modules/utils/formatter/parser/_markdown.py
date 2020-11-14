# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo
# Copyright (C) 2020 Telethon (LonamiWebs)
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

import re
from typing import Any, List, Optional, Tuple

from aiogram.api.types import MessageEntity

from .utils import (
    _MutableMessageEntity, MessageEntityType, _co_entities, _gen_writeable_ents,
    _escape_html, add_surrogate, del_surrogate, strip_text, update_ents
)

DELIMITERS = {
    '**': MessageEntityType.BOLD,
    '__': MessageEntityType.ITALIC,
    '~~': MessageEntityType.STRIKETHROUGH,
    '++': MessageEntityType.UNDERLINE,
    '`': MessageEntityType.CODE,
    '```': MessageEntityType.PRE
}

URL_RE = re.compile(r'\[([\S\s]+?)]\((.+?)\)')

# Build a regex to efficiently test all delimiters at once.
# Note that the largest delimiter should go first, we don't
# want ``` to be interpreted as a single back-tick in a code block.
DELIM_RE = re.compile('|'.join('({})'.format(re.escape(k)) for k in sorted(DELIMITERS, key=len, reverse=True)))


def parse_markdown(text: str, entities: Optional[List[MessageEntity]]) -> Tuple[str, List[MessageEntity]]:
    """
    Parses the given markdown message and returns its stripped representation
    plus a list of the MessageEntity's that were found.
    """

    # Cannot use a for loop because we need to skip some indices
    i = 0
    result: List[_MutableMessageEntity] = [] if entities is None else _gen_writeable_ents(entities)

    # Work on byte level with the utf-16le encoding to get the offsets right.
    # The offset will just be half the index we're at.
    text = add_surrogate(text)
    while i < len(text):
        m = DELIM_RE.match(text, pos=i)

        # Did we find some delimiter here at `i`?
        if m:
            delim = next(filter(None, m.groups()))

            # +1 to avoid matching right after (e.g. "****")
            end = text.find(delim, i + len(delim) + 1)

            # Did we find the earliest closing tag?
            if end != -1:

                # Remove the delimiter from the string
                text = ''.join((
                    text[:i],
                    text[i + len(delim):end],
                    text[end + len(delim):]
                ))

                # Check other affected entities
                result = update_ents(result, i, len(delim) * 2)

                # Append the found entity
                ent_type = DELIMITERS[delim]
                if ent_type == MessageEntityType.PRE:
                    result.append(_generate_ent(ent_type, offset=i, length=end - i - len(delim), language=''))  # has
                    # 'lang'
                else:
                    result.append(_generate_ent(ent_type, offset=i, length=end - i - len(delim)))

                # No nested entities inside code blocks
                if ent_type in (MessageEntityType.CODE, MessageEntityType.PRE):
                    i = end - len(delim)

                continue

        else:
            m = URL_RE.match(text, pos=i)
            if m:
                # Replace the whole match with only the inline URL text.
                text = ''.join((
                    text[:m.start()],
                    m.group(1),
                    text[m.end():]
                ))

                delim_size = m.end() - m.start() - len(m.group())
                result = update_ents(result, i, delim_size, split_length=False)

                result.append(_generate_ent(
                    MessageEntityType.URL,
                    offset=m.start(), length=len(m.group(1)),
                    url=del_surrogate(m.group(2))
                ))
                i += len(m.group(1))
                continue

        i += 1

    text = strip_text(text, result)
    return _escape_html(del_surrogate(text)), _co_entities(result)


def _generate_ent(type_: str, **args: Any) -> _MutableMessageEntity:
    return _MutableMessageEntity(type=type_, **args)
