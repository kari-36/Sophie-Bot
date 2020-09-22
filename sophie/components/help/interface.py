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

from typing import Optional

from aiogram.api.types import InlineKeyboardButton, InlineKeyboardMarkup
from pydantic import BaseModel

from sophie.components.caching.cached import cached
from sophie.utils.config import cfg

from .loader import DATA
from ..localization import GetString


class _ReplyModel(BaseModel):
    text: str
    reply_markup: InlineKeyboardMarkup


@cached()
async def get_helps(locale_code: str, module: Optional[str] = None) -> _ReplyModel:
    # TODO: Interfaces aint ready yet https://github.com/aiogram/aiogram/pull/342
    raise NotImplementedError

    buttons = InlineKeyboardMarkup()
    if module:
        buttons.add(InlineKeyboardButton(
            text="More info", url=cfg.component.help.base_url.format(module.lower())))
        fallback_locale = cfg.component.localization.default_language
        if module not in DATA:
            raise RuntimeError(f'`{module}` has no help registered!')
        elif locale_code not in DATA[module]:
            return _ReplyModel(
                text=DATA[module][fallback_locale], reply_markup=buttons)
        else:
            return _ReplyModel(
                text=DATA[module][locale_code], reply_markup=buttons
            )

    btns = [InlineKeyboardButton(text=module, callback_data='help_{0}'.format(module.lower())) for module in DATA]
    # sort buttons
    btns = sorted(btns, key=lambda item: item.text)
    return _ReplyModel(
        text=await GetString('help_menu_header', locale_code=locale_code), reply_markup=buttons.add(*btns)
    )
