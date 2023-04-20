from pydantic import BaseModel

import aiopinecone.schemas.custom as custom
import aiopinecone.schemas.generated as generated

for module in [custom, generated]:
    for obj in module.__dict__.values():
        if isinstance(obj, type) and issubclass(obj, BaseModel):
            obj.update_forward_refs()


from aiopinecone.schemas.custom import *
from aiopinecone.schemas.generated import *