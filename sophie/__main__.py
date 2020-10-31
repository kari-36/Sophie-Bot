# Copyright (C) 2018 - 2020 MrYacha.
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

import sys
import asyncio
from logging import DEBUG

from sophie import constants
from sophie.services.aiogram import dp, bot
from sophie.services.mongo import __setup__ as init_mongo
from sophie.utils.logging import log
from sophie.utils.config import cfg

from sophie.utils.loader import load_all

loop = asyncio.get_event_loop()


def initialise(loop_: asyncio.AbstractEventLoop) -> None:

    if len(sys.argv) > 1:
        if sys.argv[1] in {'testmode'}:
            log.warning("! RUNNING ON TEST MODE")
            constants.TEST_MODE = True

    # test mode != debugging
    if cfg.advanced.debug and not constants.TEST_MODE:
        log.setLevel(DEBUG)
        log.warning("! Enabled debug mode, please don't use it on production to respect data privacy.")

    log.debug("Initalising database...")
    init_mongo(loop_)
    log.debug("...Done")

    # load modules, components
    load_all(loop_)

    if cfg.advanced.migrator:
        from sophie.utils.migrator import migrator

        log.debug("Checking database migration status...")
        loop_.run_until_complete(migrator())
        log.debug("...Done")

    log.info("Running the bot...")
    loop_.run_until_complete(dp.start_polling(bot))


if __name__ == "__main__":
    initialise(loop)
