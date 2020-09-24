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

from typing import Any, Callable, Optional, Protocol, TYPE_CHECKING

from sophie.utils.bases import BaseComponent
from .config import __config__

if TYPE_CHECKING:
    from .interface import _ReplyModel

    class GetHelpsType(Protocol):
        async def __call__(self, locale_code: str, module: Optional[str] = None) -> _ReplyModel:
            ...

    include_help: Callable[[str], Callable[..., Any]]
    get_helps: GetHelpsType


class Help(BaseComponent):
    configurations = __config__

    @classmethod
    async def __before_serving__(cls) -> None:
        from .loader import load
        await load()

    @classmethod
    def __pre_init__(cls, module: Any) -> None:
        from .decorators import include_help
        from .interface import get_helps

        module.include_help = include_help
        module.get_helps = get_helps
