
from typing import List, TypedDict, TYPE_CHECKING

class ChatPerms(TypedDict):

    """
    `dict` representing a user's permission to read and write to a specific channel/chat.
    Contains the following keys:

    ```python
    readable: bool
    writeable: bool
    ```
    """

    readable: bool
    writeable: bool

class ServerPerms(TypedDict):

    """
    `dict` representing a user's permissions to manage server, channel, vc settings, etc.
    Contains the following keys:

    ```python
    manage_server: bool
    manage_chats: bool
    manage_members: bool
    manage_roles: bool
    manage_voice: bool
    manage_messages: bool
    ```
    """

    manage_server: bool
    manage_chats: bool
    manage_members: bool
    manage_roles: bool
    manage_voice: bool
    manage_messages: bool


if TYPE_CHECKING:
    from datetime import datetime

class MessageInfo(TypedDict):
    """ Interface specifying fields for a Message Object
    schema:
    ```python
    {
        message_id: str
        user_id: str
        message_content: str
        server_id: str
        chat_id: str
        replied_to_id: str
        message_content: str
        message_timestamp: datetime
        pinged_user_ids: List[str]
    }
    ```
    """
    message_id: str
    user_id: str
    message_content: str
    server_id: str
    chat_id: str
    replied_to_id: str
    message_content: str
    message_timestamp: datetime
    pinged_user_ids: List[str]