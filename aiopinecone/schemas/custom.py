from typing import List
from typing import NotRequired
from typing import TypedDict


class FetchParams(TypedDict):
    ids: List[str]
    namespace: NotRequired[str]
