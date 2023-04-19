from typing import List
from typing import TypedDict
from typing_extensions import NotRequired

class FetchParams(TypedDict):
    ids: List[str]
    namespace: NotRequired[str]
