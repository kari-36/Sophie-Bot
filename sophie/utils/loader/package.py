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

import inspect

from importlib import import_module
from pathlib import Path
from typing import Any, Optional, Type, cast, Dict

from sophie.utils.bases import Base, BaseModule
from sophie.utils.config import cfg, real_config
from sophie.utils.logging import log
from .requirements import check_requirements


class Package:

    def __init__(self, type: str, name: str, path: Path):  # noqa: A002
        self.type = type
        self.name = name
        self.path = path
        self.python_path = str(self.path).replace('/', '.')

        # vars
        self.data: Dict[Any, Any] = {}
        self.version: Optional[str] = None

        if not path.exists():
            raise FileNotFoundError

        log.debug(f"Loading {self.name} package, {self.type=}...")

        if (requirements_file_path := self.path / 'requirements.txt').exists():
            log.debug(f"Checking requirements for {self.name} {self.type}...")
            with open(requirements_file_path) as f:
                check_requirements(f)
                log.debug("...Done!")

        log.debug(f"Importing {self.name} package...")
        self.p_object: Any = import_module(self.python_path)  # contains the module
        self.base = self.__get_member()  # contains base class

        version_file = self.path / 'version.txt'
        if version_file.exists():
            with open(version_file) as f:
                self.version = f.read()

        if hasattr(self.base, 'configurations'):
            self.__load_config()

        if hasattr(self.base, '__pre_init__'):
            log.debug(f"Running __pre_init__ of {self.name} package...")
            self.__trigger_pre_init()
            log.debug("...Done")

        log.debug("...Done!")

    def __load_config(self) -> bool:
        log.debug(f"Loading configurations for {self.name} package")
        setattr(
            getattr(
                cfg,
                self.type
            ),
            self.name,
            self.base.configurations.parse_obj(
                real_config.get(self.type, {}).get(self.name, {})
            )
        )
        return True

    def __trigger_pre_init(self) -> Any:
        log.debug(f"Running __pre_init__ of {self.name} package...")
        self.base.__pre_init__(self.p_object)
        log.debug("...Done")

    def __get_member(self) -> Type[Base]:
        for cls in inspect.getmembers(self.p_object, self.__istarget):
            return cls[1]
        else:
            raise RuntimeError(f"{self.type} {self.name} should implement base!")

    @staticmethod
    def __istarget(member: Any) -> bool:
        if inspect.isclass(member) and issubclass(member, Base):
            if member.__name__ not in {'BaseModule', 'BaseComponent'}:
                return True
        return False

    def __repr__(self) -> str:
        # debugging
        attrs = ", ".join(repr(v) if k is None else f'{k}={v!r}' for k, v in self.__dict__.items())
        cls = self.__class__.__name__
        return f"{cls}({attrs})"


class Module(Package):

    def __init__(self, type: str, name: str, path: Path):  # noqa: A002
        super().__init__(type, name, path)
        if type == 'module':
            self._load_module(cast(BaseModule, self.base))

    def _load_module(self, module: BaseModule) -> None:
        from sophie.services.aiogram import modules_router
        # Load routers
        if module.router:

            log.debug(f"Loading router(s) for {self.name} {self.type}...")
            if not isinstance(module.router, list):
                self.routers = [module.router]
            self.routers = self.routers

            # Include routers
            for router in self.routers:
                modules_router.include_router(router)
            log.debug("...Done")
