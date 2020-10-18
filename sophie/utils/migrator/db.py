# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
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

import enum

from typing import Any, Optional
from pymongo import ASCENDING, IndexModel

from sophie.services.mongo import mongo, Document
from sophie.utils.logging import log

col_name = 'migrator'


class Types(str, enum.Enum):

    # noinspection PyMethodParameters
    def _generate_next_value_(name: Any, start: int, count: int, last_values: list) -> str:  # type: ignore
        return str(name)

    base = enum.auto()
    module = enum.auto()
    component = enum.auto()


class MigrationDB(Document):
    name: str
    type: Types  # noqa: A003
    version: int

    class Mongo:
        collection = col_name
        indexes = [
            IndexModel([("chat_id", ASCENDING)], name="chat_id", unique=True)
        ]


async def get_current_version(package_name: str, package_type: str) -> Optional[int]:
    data = await MigrationDB.find_one({"name": package_name, "type": package_type})

    if not data:
        return None

    return data.version


async def set_version(package_name: str, package_type: str, version: int) -> int:
    await MigrationDB.collection().update_one(
        {'name': package_name, 'type': package_type},
        {'$set': {'version': version}},
        upsert=True
    )
    return version


async def __setup__() -> Any:
    if col_name not in await mongo.list_collection_names():
        log.info(f'Created not exited column "{col_name}"')
        await mongo.create_collection(col_name)

    log.debug(f'Creating indexes for "{col_name}" column')
    # await MigrationDB.init_indexes()
