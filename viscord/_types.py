from typing import List, TypedDict, TYPE_CHECKING

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
