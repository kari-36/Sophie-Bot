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

import typing


def parse_method(
        *fields: str, last_fields: bool = False, pass_whole_text: bool = False, communicate: bool = False
) -> typing.Callable[[typing.Callable[..., typing.Any]], classmethod]:

    """
    Decorator for assigning methods to field parsers

    You can use the decorator as follows::

        @parse_method("field1", "field2")
        async def field_one_method(cls, message, text):
            # yes! parse methods can be async
            # text param returns the IndexField matched text
            return text, {"I got field1", 1}

    You could also communicate between fields, to receieve comm data, you should use ``communication=True`` param::

        @parse_method("field3", communicate=True)
        def field3_parse_method(cls, message, text, communication):
            # communication param contains "{"I got field1": 1}
            return text

    You can also view the value of last fields::

        @parse_method("field4", last_fields=True, communication=True)
        def field4_parse_method(cls, message, text, last_fields, comm):
            # last_fields :> {"field1": ..., "field2": ...}
            return text


    :param fields:  fields which parser made for
    :param last_fields: If True, parser will get all parsed fields (yet)
    :param pass_whole_text: whole text instead of Index matched field
    :param communicate:  if parser need to recieve additional data from last field
    """

    def decorator(func: typing.Callable[..., typing.Any]) -> classmethod:
        f_cls = func if isinstance(func, classmethod) else classmethod(func)
        setattr(  # noqa
            f_cls,
            "__parser_method__",
            (
                fields,
                f_cls.__func__
            )
        )
        return f_cls
    return decorator
