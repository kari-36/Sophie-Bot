from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from sophie_bot.types.chat import ChatId


class ChatTypes(str, Enum):
    private = "private"
    """Represents private chats like chats with user"""
    public = "public"
    """Represents the groups, including private group"""
    unknown = "unknown"
    """Represents when connection cant determine the type of the group, in case of errors"""


class ConnectionStatus(str, Enum):
    success = "success"
    error = "error"


class Chat(BaseModel):
    id: ChatId
    """Unique identifier for the chat"""
    title: str = Field(default="Local Chat")
    """Title of chat, will be 'Local Chat' in private chats"""
    chat_type: ChatTypes = Field(default=ChatTypes.unknown)
    """Represents the chat type, private or public, unknown in case of failure"""


class ConnectedChat(BaseModel):
    status: ConnectionStatus
    """Status of connection, displays errors, like certain commands cant be used"""
    chat: Chat = Field(default=Chat(id=ChatId(0), title="", chat_type=ChatTypes.unknown))
    """Contains chat data, like Identifier, Title of chat"""
    error_msg: Optional[str]
    """Contains errors message in case of any failure"""

    def is_error(self) -> bool:
        """Function to check failure in connection"""
        if self.status == ConnectionStatus.error:
            return True
        return False
