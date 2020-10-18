# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2020 Jeepeo
#
# This file is part of SophieBot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import Any

import motor_odm
import orjson


def _orjson_dumps(value: Any, *, default: Any) -> str:
    return orjson.dumps(value, default=default).decode()


class Document(motor_odm.Document, abstract=True):  # type: ignore

    class Config(motor_odm.Document.Config):
        # uses orjson as a replacement for `json`, can be used for importing/exporting
        json_loads = orjson.loads
        json_dumps = _orjson_dumps

        # use enum's value instead of ref
        use_enum_values = True


__all__ = ('Document',)
