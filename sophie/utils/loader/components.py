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

from typing import Union

from pathlib import Path

from sophie.utils.logging import log
from .package import Package


def load_component(component_name: str) -> Union[Package, bool]:
    from . import LOADED_COMPONENTS

    path = Path(f"sophie/components/{component_name}")
    # check if component exists
    if not path.exists():
        return False

    log.debug(f"Loading component: {component_name}")
    component = Package(
        type='component',
        name=component_name,
        path=path
    )

    LOADED_COMPONENTS[component_name] = component
    return component
