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

from __future__ import annotations
from typing import Any, TYPE_CHECKING

from sophie.utils.logging import log

if TYPE_CHECKING:
    from aiogram import Router
    from sophie.utils.loader.package import Package


async def __setup__(router: Router) -> Any:
    from sophie.utils.loader import LOADED_MODULES, LOADED_COMPONENTS

    log.debug('Loading owners functions...')

    for module in [*LOADED_MODULES.values(), *LOADED_COMPONENTS.values()]:  # type: Package
        if hasattr(module.p_object, 'OwnerFunctions'):
            log.debug(f"Found owners function for {module.name} module")
            class_object = module.p_object.OwnerFunctions

            # Check if function needs setup operation
            if hasattr(class_object, '__setup__'):
                await class_object.__setup__(class_object, router)

            functions = [f for f in dir(class_object) if not f.startswith('_')]
            for function in functions:
                # log.debug(f"Loading {function} under {module['name']} module...")
                func: Any = getattr(class_object, function)
                filters = {}

                # Check if function is owner-only
                if hasattr(func, 'only_owner') and func.only_owner is True:
                    filters['is_owner'] = True
                else:
                    filters['is_op'] = True

                filters['op_cmd'] = function  # type: ignore

                router.message.register(func, **filters)  # type: ignore
                log.debug('..Done')
        else:
            log.debug(f"Not found owners function for {module.name} module, skipping...")
            continue

    log.debug("...Done")
