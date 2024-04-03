from typing import TypedDict

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