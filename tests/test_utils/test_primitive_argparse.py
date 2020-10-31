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

import pytest
from tgintegration import BotController, Response


class TestPrimitiveArgParse:

    @pytest.mark.asyncio
    async def test_get_args(self, controller: BotController):

        args = ['test', 'test']
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command('test_get_args', args=args)

        assert res.full_text == "test test"

        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command('test_get_args')

        assert res.full_text == "None"

    @pytest.mark.asyncio
    async def test_get_args_list(self, controller: BotController):
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command('test_get_args_list')

        assert eval(res.full_text) == ['']

        async with controller.collect(count=1) as res:  # type: Response
            args = ['test', 'test']
            await controller.send_command('test_get_args_list', args=args)

        assert eval(res.full_text) == args
