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

from typing import TYPE_CHECKING, Any, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.api.types import Update
from sentry_sdk import capture_exception
from sentry_sdk.api import push_scope

from sophie.utils.config import cfg

if TYPE_CHECKING:
    from aiogram import Dispatcher


class SentryLogger(BaseMiddleware[Update]):

    async def __call__(
        self,
        handler: Callable[..., Any],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        self.event = event.copy()

        try:
            return await handler(event, data)
        # TODO: Ignore certain errors
        except Exception as err:
            with push_scope() as scope:
                scope.set_extra("update", self.event.dict())
                capture_exception(err)
            raise  # re raise the error and pass it to aiogram error handler


def __setup__(dp: Dispatcher) -> None:
    if cfg.advanced.sentry_dsn:
        dp.update.outer_middleware(SentryLogger())
