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
from ._internal import _ArgField


class Undefined:
    def __repr__(self) -> str:
        return 'Undefined'


def ArgField(
        default: typing.Any = Undefined, *,
        index: int = 0,
        regex: str = r'[^\s]+',
        optional: bool = False,
        description: str = None
) -> typing.Any:
    """
    :param default: fallback value
    :param regex: Regex for field
    :param index: index of where argument lies, defaults to 0
    :param optional: True if ``None`` value is allowed
    :param description: Small description of field, used to hint user if field isn't given
    """

    return _ArgField(
        default, index, regex, optional
    )
