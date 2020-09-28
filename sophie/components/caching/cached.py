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
import functools
from typing import Any, Callable, Optional, Union, cast

from sophie.utils.logging import log
from . import cache


class cached:

    def __init__(self, ttl: Optional[Union[int, float]] = None, key: Optional[str] = None, no_self: bool = False):
        self.ttl = ttl
        self.key = key
        self.no_self = no_self

    def __call__(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        if not hasattr(self, 'func'):
            self.func: Callable[..., Any] = args[0]
            # wrap
            functools.update_wrapper(self, self.func)
            # return ``cached`` object when function is not being called
            return self
        return cast(Callable[..., Any], self._set(*args, **kwargs))

    async def _set(self, *args: dict, **kwargs: dict) -> Any:
        key = self.__build_key(*args, **kwargs)

        value = await cache.get(key)
        if value is not None:
            return value if value is not _NotSet else value.real_value

        result = await self.func(*args, **kwargs)
        asyncio.ensure_future(cache.set(key, result if result is not None else _NotSet, ttl=self.ttl))
        log.debug(f'Cached: writing new data for key - {key}')
        return result

    def __build_key(self, *args: dict, **kwargs: dict) -> str:
        ordered_kwargs = sorted(kwargs.items())

        new_key = self.key if self.key else (self.func.__module__ or "") + self.func.__name__
        new_key += str(args[1:] if self.no_self else args)

        if ordered_kwargs:
            new_key += str(ordered_kwargs)

        return new_key

    async def reset_cache(self, *args: Any, new_value: Any = None, **kwargs: Any) -> Any:
        """
        >>> @cached()
        >>> def somefunction(arg):
        >>>     pass
        >>>
        >>> [...]
        >>> arg = ... # same thing ^^
        >>> await somefunction.reset_cache(arg, new_value='Something')

        :param new_value: new/ updated value to be set [optional]
        """

        key = self.__build_key(*args, **kwargs)
        if new_value:
            return await cache.set(key, new_value, ttl=self.ttl)
        return await cache.delete(key)


class _NotSet:
    real_value = None

    def __repr__(self) -> str:
        return 'NotSet'
