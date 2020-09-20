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

import html
import re
from html.parser import HTMLParser
from typing import Any, List, Tuple, Optional

from aiogram.utils.text_decorations import HtmlDecoration, MarkdownDecoration

TG_TAGS = {
    "s", "b", "strong",  # bold
    "i", "em",  # italics
    "u",  # underline
    "s", "del", "strike",  # strikethrough
    "code",  # code
    "pre",  # code block
    "a"  # link
}

BOLD_DELIM = "**"
ITALIC_DELIM = "__"
UNDERLINE_DELIM = "++"
STRIKE_DELIM = "~~"
CODE_DELIM = "`"
PRE_DELIM = "```"

MARKDOWN_RE = re.compile(r"({d})|\[(.+?)]\((.+?)\)".format(
    d="|".join(
        ["".join(i) for i in [
            [rf"\{j}" for j in i]
            for i in [
                PRE_DELIM,
                CODE_DELIM,
                STRIKE_DELIM,
                UNDERLINE_DELIM,
                ITALIC_DELIM,
                BOLD_DELIM
            ]
        ]]
    )))

OPENING_TAG = "<{}>"
CLOSING_TAG = "</{}>"
URL_MARKUP = '<a href="{}">{}</a>'
FIXED_WIDTH_DELIMS = [CODE_DELIM, PRE_DELIM]


class HTML(HTMLParser):

    def __init__(self) -> None:
        super().__init__()

        self.tags: List[Tuple[str, int]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:

        if tag not in TG_TAGS:
            return

        _, offset = self.getpos()
        self.tags.append((tag, offset - 1))

    def handle_endtag(self, tag: str) -> None:
        # for nested entities; last tag need to be closed first
        last_tag = self.tags[-1]
        _, offset = self.getpos()

        if tag not in dict(self.tags):
            raise ParseError(f"Unmatched end tag'{CLOSING_TAG.format(tag)}' at offset {offset}.")
        if last_tag[0] != tag:
            raise ParseError(
                f"Unmatched end tag '{CLOSING_TAG.format(tag)}', "
                f"expected '{CLOSING_TAG.format(last_tag[0])}' at offset {offset}."
            )

        try:
            self.tags.pop()
        except IndexError:
            pass

    @staticmethod
    def _fix_unmatched_tag(text: str, offset: int, tag: str) -> str:
        return text[:offset] + text[offset:].replace(tag, '', 1)

    def error(self, message: Any) -> None:
        pass

    @classmethod
    def parse(cls, text: str) -> str:
        parser = cls()
        parser.feed(text)
        parser.close()

        if len(parser.tags) > 0:
            raise ParseError(
                f"Unclosed start tags '{', '.join([OPENING_TAG.format(i) for i, _ in parser.tags])}'"
            )

        return text


class Markdown:

    @classmethod
    def parse(cls, text: str) -> str:
        text = html.escape(text, quote=False)

        delims: List[Tuple[str, int]] = []
        is_fixed_width = False
        _addition_offset = 0

        for match in re.finditer(MARKDOWN_RE, text):
            start, _ = match.span()
            offset = start + _addition_offset
            delim, text_url, url = match.groups()  # type: str, str, str
            full = match.group(0)

            if delim in FIXED_WIDTH_DELIMS:
                is_fixed_width = not is_fixed_width

            if is_fixed_width and delim not in FIXED_WIDTH_DELIMS:
                continue

            if text_url:
                html_url = URL_MARKUP.format(url, text_url)
                text = cls.replace_once(text, full, html_url, offset)
                _addition_offset += cls._get_offset(html_url, f"[{text_url}]({url})")
                continue

            if delim == BOLD_DELIM:
                tag = "b"
            elif delim == ITALIC_DELIM:
                tag = "i"
            elif delim == UNDERLINE_DELIM:
                tag = "u"
            elif delim == STRIKE_DELIM:
                tag = "s"
            elif delim == CODE_DELIM:
                tag = "code"
            elif delim == PRE_DELIM:
                tag = "pre"
            else:
                continue

            if delim not in dict(delims):
                delims.append((delim, offset))
            else:
                open_tag = OPENING_TAG.format(tag)
                open_offset = dict(delims).get(delim)
                if open_offset is not None:
                    text = cls.replace_once(text, delim, open_tag, open_offset)
                    _addition_offset += cls._get_offset(open_tag, delim)

                tag = CLOSING_TAG.format(tag)
                text = cls.replace_once(text, delim, tag, offset)
                _addition_offset += cls._get_offset(tag, delim)

        return HTML.parse(text)

    @classmethod
    def _get_offset(cls, new: str, old: str) -> int:
        return len(new) - len(old)

    @staticmethod
    def replace_once(source: str, old: str, new: str, start: int) -> str:
        return source[:start] + source[start:].replace(old, new, 1)


def get_parse_mode(text: str, default_parser: str = 'md') -> Tuple[str, str]:
    if not text:
        return text, default_parser

    match = re.search(r'%PARSEMODE_(?P<parse_mode>\w+)', text)
    if match is not None:
        if (mode := match.group('parse_mode')) is not None:
            if mode.lower() in {'md', 'html', 'none'}:
                text = re.sub(r'%PARSEMODE_(?P<parse_mode>\w+)\s?', '', text, 1)
                return text, mode.lower()
    return text, default_parser


class UnpackEntitiesHTML(HtmlDecoration):

    def quote(self, value: str) -> str:
        return value


class UnpackEntitiesMD(MarkdownDecoration):

    def quote(self, value: str) -> str:
        return value

    def bold(self, value: str) -> str:
        return f"**{value}**"

    def italic(self, value: str) -> str:
        return f"__{value}__"

    def underline(self, value: str) -> str:
        return f"++{value}++"

    def strikethrough(self, value: str) -> str:
        return f"~~{value}~~"


class ParseError(Exception):

    def __init__(self, text: str):
        self.text = text
