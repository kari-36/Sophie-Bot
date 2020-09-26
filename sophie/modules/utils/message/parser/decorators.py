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


def parse_method(*fields: str) -> typing.Callable[[typing.Callable[..., typing.Any]], classmethod]:

    """
    Decorator for assigning methods to field parsers

    >>> @parse_method('SomeFieldNames')
    >>> def something(cls, value):
    >>>     pass

    You can access multiple other properties by using args as shown below
    >>> def something (cls, text, values: dict, field: '_ArgField', match: typing.Optional[typing.Match]): ...
    >>> # contains values of field before---^,   ^--- Field data      ^--- Optional match object
    :param fields:  fields which parser made for
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
