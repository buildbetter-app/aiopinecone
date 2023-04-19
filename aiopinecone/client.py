from typing import Optional
from typing import overload
from typing import Type
from typing import TypeVar
from urllib.parse import quote
from urllib.parse import urlencode

from aiohttp import ClientSession
from pydantic import BaseModel
from pydantic import root_validator

from aiopinecone.schemas import DeleteRequest
from aiopinecone.schemas import FetchResponse
from aiopinecone.schemas import IndexMeta
from aiopinecone.schemas import QueryRequest
from aiopinecone.schemas import QueryResponse
from aiopinecone.schemas.custom import FetchParams
from aiopinecone.schemas.generated import UpdateRequest
from aiopinecone.schemas.generated import UpsertRequest

PydanticModelT = TypeVar("PydanticModelT", bound=BaseModel)


class PineconeVectorClient(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    api_key: str
    region: str
    index: str
    project_id: str
    session: ClientSession

    @root_validator(pre=True)
    def session_validation(cls, v):
        session = v.get(
            "session",
            ClientSession(
                raise_for_status=True, headers={"Api-Key": v["api_key"]}
            ),
        )
        v["session"] = session

    @property
    def base_url(self) -> str:
        return f"https://controller.{self.region}.pinecone.io"

    @property
    def index_url(self) -> str:
        return f"https://{self.index}-{self.project_id}.svc.{self.region}.pinecone.io"

    def base_path(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    def path(self, path: str) -> str:
        return f"{self.index_url}/{path}"

    @overload
    async def _json_request(
        self,
        method,
        path,
        request_model_instance: None = None,
        response_model: None = None,
    ) -> None:
        ...

    @overload
    async def _json_request(
        self,
        method,
        path,
        request_model_instance: Optional[BaseModel] = None,
        response_model: Type[PydanticModelT] = None,
    ) -> PydanticModelT:
        ...

    async def _json_request(
        self,
        method,
        path,
        request_model_instance: Optional[BaseModel] = None,
        response_model: Optional[Type[PydanticModelT]] = None,
    ) -> Optional[PydanticModelT]:
        async with self.session.request(
            method,
            self.path(path),
            json=None
            if request_model_instance is None
            else request_model_instance.dict(),
        ) as resp:
            if response_model:
                return response_model(**await resp.json())

    async def describe_index(self) -> IndexMeta:
        return await self._json_request(
            "GET", self.base_path(f"databases/{self.index}"), None, IndexMeta
        )

    async def query(self, request: QueryRequest) -> QueryResponse:
        return await self._json_request(
            "POST", self.path("query"), request, QueryResponse
        )

    async def delete(self, request: DeleteRequest) -> None:
        return await self._json_request(
            "DELETE", self.path("vectors/delete"), request
        )

    async def fetch(self, params: FetchParams) -> FetchResponse:
        url = self.path(
            f"vectors/fetch?{urlencode(params, doseq=True, quote_via=quote)}"
        )
        return await self._json_request("GET", url, None, FetchResponse)

    async def update(self, request: UpdateRequest) -> None:
        return await self._json_request(
            "POST", self.path("vectors/update"), request
        )

    async def upsert(self, request: UpsertRequest) -> None:
        return await self._json_request(
            "POST", self.path("vectors/upsert"), request
        )
