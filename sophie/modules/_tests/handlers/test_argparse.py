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

from __future__ import annotations

from typing import TYPE_CHECKING

from sophie.modules.utils.message import ArgField, ArgumentParser, parse_method
from .. import test_router

if TYPE_CHECKING:
    from aiogram.dispatcher.filters import CommandObject
    from aiogram.api.types import Message


class TestArgs(ArgumentParser):
    arg_one: str = ArgField(regex=r"\w+")
    arg_two: str = ArgField(index=1, regex=r"\d+")


@test_router.message(TestArgs.filter(), commands=['testargs'])
async def test_args(message: Message, args: TestArgs, command: CommandObject) -> Message:
    cmd = command.prefix + command.command
    if command.mention:
        cmd += "@"
        cmd += command.mention
    return await message.reply(f"{cmd} {args.arg_one} {args.arg_two}")


class InheritedTestArgs(TestArgs):
    arg_three: str = ArgField(index=2)


@test_router.message(InheritedTestArgs.filter(), commands=['testinheritedargs'])
async def test_inherited_args(message: Message, args: InheritedTestArgs) -> Message:
    return await message.reply(f"{args.arg_one} {args.arg_two} {args.arg_three}")


class TestDefaultArg(ArgumentParser):
    arg_one: str = ArgField(default="default")


@test_router.message(TestDefaultArg.filter(optional=True), commands=['testdefaultarg'])
async def test_default_arg(message: Message, args: TestDefaultArg) -> Message:
    return await message.reply(args.arg_one)


class TestArgParseMethod(ArgumentParser):
    arg_one: str = ArgField()
    arg_two: str = ArgField(index=1)

    @parse_method("arg_one")
    def parse_arg_one(cls, value: str) -> str:
        return value.lower()

    @parse_method("arg_two")
    async def parse_arg_two(cls, _: str) -> str:
        return "PASSED"


@test_router.message(TestArgParseMethod.filter(), commands=['testargparsemethod'])
async def test_arg_parse_method(message: Message, args: TestArgParseMethod) -> Message:
    return await message.reply(f"{args.arg_one} {args.arg_two}")


class TestArgParseMethodBlock(ArgumentParser):
    arg_one: str = ArgField()

    @parse_method('arg_one')
    def parse_arg_one(cls, value: str) -> None:
        raise ValueError("TEST")


@test_router.message(TestArgParseMethodBlock.filter(), commands=['testargparsemethodblock'])
async def test_arg_parse_method_blocking() -> None:
    raise RuntimeError("WHAT!??! This can't be called")


class TestOptionalArgs(ArgumentParser):
    arg_one = ArgField()
    arg_two = ArgField(optional=True)


@test_router.message(TestOptionalArgs.filter(), commands=['testoptionalargs'])
async def test_optional_args(message: Message, args: TestOptionalArgs):
    return await message.reply(f"{args.arg_one} {args.arg_two}")
