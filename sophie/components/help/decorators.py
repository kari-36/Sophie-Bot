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
from typing import Any, Awaitable, Callable, Dict, TypeVar

EXTERNAL_HELPFUNCS: Dict[str, Callable[..., Awaitable[Dict[str, str]]]] = {}

F = TypeVar("F", bound=Callable[..., Any])


def include_help(module: str) -> Callable[[F], None]:
    def wrapped(func: F) -> None:
        EXTERNAL_HELPFUNCS[module.capitalize()] = func
    return wrapped
