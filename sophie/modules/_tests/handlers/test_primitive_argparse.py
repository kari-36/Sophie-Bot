# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo.
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

from aiogram.api.types import Message
from sophie.modules.utils.message import get_args, get_args_list

from .. import test_router


@test_router.message(commands=['test_get_args'])
async def test_get_args(message: Message):
    args = get_args(message)
    if not args:
        return await message.reply("None")
    return await message.reply(args)


@test_router.message(commands=['test_get_args_list'])
async def test_get_args_list(message: Message):
    args_list = get_args_list(message)
    return await message.reply(str(args_list))
