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

import asyncio
import os
import subprocess
import sys
import time
from typing import Union

import pytest
from pyrogram import Client
from tgintegration import BotController

_BOT_PROC: Union[subprocess.Popen[bytes], subprocess.Popen]


def pytest_configure():
    global _BOT_PROC

    env = os.environ.copy()
    # we dont want to run sophie in debug mode :shrug:
    env.update(COVERAGE_FILE='.coverage')

    # run sophie
    cmd = ["coverage", "run", "-m", "sophie", "testmode"]

    if sys.platform != "win32":
        _BOT_PROC = subprocess.Popen(
            cmd,
            env=env,
            cwd='../',
        )  # set cwd to root dir of project
    else:
        # On Windows, attach proc to another console to make sure CTRL-C event doesnt leak
        _BOT_PROC = subprocess.Popen(
            cmd,
            env=env,
            cwd='../',
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

    # wait some time to start sophie
    time.sleep(10)


def pytest_unconfigure():
    # kill the sophie (process)
    if sys.platform != "win32":
        _BOT_PROC.kill()
    else:
        # using _BOT_PROC.kill() on windows exits with code 1, hacky fix to it
        import ctypes
        kernel = ctypes.windll.kernel32
        kernel.FreeConsole()
        kernel.AttachConsole(_BOT_PROC.pid)
        kernel.SetConsoleCtrlHandler(None, 1)
        kernel.GenerateConsoleCtrlEvent(0, 0)
    # wait some time ...
    time.sleep(2)
    # Generate xml coverage report
    subprocess.Popen(["coverage", "xml"], cwd="../").wait()
    # Show coverage report to tests' stdout
    subprocess.Popen(["coverage", "report"], cwd='../').wait()


@pytest.yield_fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> Client:
    client = Client(
        os.environ.get("SESSION"),
        api_hash=os.environ.get("API_HASH"),
        api_id=os.environ.get("API_ID")
    )
    await client.start()
    yield client
    await client.stop()


@pytest.fixture(scope="module")
async def controller(client: Client) -> BotController:
    ctrl = BotController(
        client=client,
        peer=os.environ.get("PEER"),
        max_wait=20
    )
    await ctrl.initialize(start_client=False)
    yield ctrl

