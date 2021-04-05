# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2019 Aiogram
#
# This file is part of SophieBot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import Optional, Union, Any

from aiogram import types
from aiogram.utils.exceptions import Unauthorized

from sophie_bot.models.connections import ConnectedChat, ConnectionStatus, ChatTypes, Chat
from sophie_bot.modules.utils.user_details import is_user_admin
from sophie_bot.services.mongo import db
from sophie_bot.services.redis import redis
from sophie_bot.types.chat import ChatId
from sophie_bot.utils.cached import cached


@cached(ttl=900)
async def get_connected_chat(
        chat: types.Chat,
        user_id: int,
        admin: bool = False,
        only_groups: bool = False,
        command: Optional[str] = None
) -> ConnectedChat:
    # admin - Require admin rights in connected chat
    # only_in_groups - disable command when bot's pm not connected to any chat
    real_chat_id = chat.id
    key = 'connection_cache_' + str(user_id)

    if not chat.type == 'private':
        _chat = await db.chat_list.find_one({'chat_id': real_chat_id})
        chat_title = _chat['chat_title'] if _chat is not None else chat.title
        # On some strange cases such as Database is fresh or new ; it doesn't contain chat data
        # Only to "handle" the error, we do the above workaround - getting chat title from the update
        # return {'status': 'chat', 'chat_id': real_chat_id, 'chat_title': chat_title}
        return ConnectedChat(
            status=ConnectionStatus.success,
            chat=Chat(id=real_chat_id, title=chat_title, chat_type=ChatTypes.public)
        )

    # if pm and not connected
    if not (connected := await get_connection_data(user_id)) or 'chat_id' not in connected:
        if only_groups:
            # return {'status': None, 'err_msg': 'usage_only_in_groups'}
            return ConnectedChat(status=ConnectionStatus.error, error_msg="usage_only_in_groups")
        else:
            # return {'status': 'private', 'chat_id': user_id, 'chat_title': 'Local chat'}
            return ConnectedChat(
                status=ConnectionStatus.success,
                chat=Chat(id=ChatId(user_id), chat_type=ChatTypes.private)
            )

    chat_id = connected['chat_id']

    # Get chats where user was detected and check if user in connected chat
    # TODO: Really get the user and check on banned
    user_chats = (await db.user_list.find_one({'user_id': user_id}))['chats']
    if chat_id not in user_chats:
        # return {'status': None, 'err_msg': 'not_in_chat'}
        return ConnectedChat(status=ConnectionStatus.error, error_msg="not_in_chat")

    chat_title = (await db.chat_list.find_one({'chat_id': chat_id}))['chat_title']

    # Admin rights check if admin=True
    try:
        user_admin = await is_user_admin(chat_id, user_id)
    except Unauthorized:
        # return {'status': None, 'err_msg': 'bot_not_in_chat, please /disconnect'}
        return ConnectedChat(status=ConnectionStatus.error, error_msg="bot_not_in_chat, please /disconnect")

    if admin:
        if not user_admin:
            # return {'status': None, 'err_msg': 'u_should_be_admin'}
            return ConnectedChat(status=ConnectionStatus.error, error_msg="user_not_admin")

    if 'command' in connected:
        if command in connected['command']:
            # return {'status': True, 'chat_id': chat_id, 'chat_title': chat_title}
            return ConnectedChat(
                status=ConnectionStatus.success,
                chat=Chat(id=ChatId(chat_id), title=chat_title, chat_type=ChatTypes.public)
            )
        else:
            # Return local chat if user is accessing non connected command
            # return {'status': 'private', 'chat_id': user_id, 'chat_title': 'Local chat'}
            return ConnectedChat(
                status=ConnectionStatus.success,
                chat=Chat(id=ChatId(user_id), chat_type=ChatTypes.private)
            )

    # Check on /allowusersconnect enabled
    if settings := await db.chat_connection_settings.find_one({'chat_id': chat_id}):
        if 'allow_users_connect' in settings and settings['allow_users_connect'] is False and not user_admin:
            # return {'status': None, 'err_msg': 'conn_not_allowed'}
            return ConnectedChat(status=ConnectionStatus.error, error_msg="conn_not_allowed")

    return ConnectedChat(
        status=ConnectionStatus.success,
        chat=Chat(id=ChatId(chat_id), title=chat_title, chat_type=ChatTypes.public)
    )


def chat_connection(**dec_kwargs):
    def wrapped(func):
        async def wrapped_1(*args: Any, **kwargs: Any):

            raw_message: Union[types.Message, types.CallbackQuery] = args[0]
            if isinstance(raw_message, types.Message):
                chat = raw_message.chat
                user_id = raw_message.chat.id
            elif isinstance(raw_message, types.CallbackQuery):
                chat = raw_message.message.chat.id
                user_id = raw_message.from_user.id
            else:
                raise Exception("Connection got unexpected message type: failed to parse chat and user details")

            if (check := await get_connected_chat(chat=chat, user_id=user_id, **dec_kwargs)).is_error():
                if isinstance(raw_message, types.Message):
                    await raw_message.reply(check.error_msg, allow_sending_without_reply=True)
                elif isinstance(raw_message, types.CallbackQuery):
                    await raw_message.answer(check.error_msg, show_alert=True)
                else:
                    # totally unexpected
                    raise Exception("Unexpected condition at `chat_connection`")
                return
            else:
                return await func(*args, check.chat, **kwargs)

        return wrapped_1

    return wrapped


async def set_connected_chat(user_id: int, chat_id: Optional[int]):
    key = f'connection_cache_{user_id}'
    redis.delete(key)
    if not chat_id:
        await db.connections.update_one({'user_id': user_id}, {"$unset": {'chat_id': 1, 'command': 1}}, upsert=True)
        await get_connection_data.reset_cache(user_id)
        return

    await db.connections.update_one(
        {'user_id': user_id},
        {
            "$set": {'user_id': user_id, 'chat_id': chat_id},
            "$unset": {'command': 1},
            "$addToSet": {'history': {'$each': [chat_id]}}
        },
        upsert=True
    )
    return await get_connection_data.reset_cache(user_id)


async def set_connected_command(user_id, chat_id, command):
    command.append('disconnect')
    await db.connections.update_one(
        {'user_id': user_id},
        {
            '$set': {'user_id': user_id, 'chat_id': chat_id, 'command': list(command)}
        },
        upsert=True
    )
    return await get_connection_data.reset_cache(user_id)


@cached()
async def get_connection_data(user_id: int) -> dict:
    return await db.connections.find_one({'user_id': user_id})
