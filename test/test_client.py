from typing import Optional, Type
from aiohttp import ClientError, ClientSession
from pydantic import BaseModel, BaseSettings
import pytest

from aiopinecone.client import PineconeVectorClient, PydanticModelT
from aiopinecone.schemas.generated import IndexMeta


class Config(BaseSettings):
    api_key: str
    region: str
    project_id: str
    index: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@pytest.mark.asyncio
async def test_describe_index():
    cfg = Config()
    async with ClientSession() as sess:
        client = PineconeVectorClient(
            api_key=cfg.api_key,
            project_id=cfg.project_id,
            index=cfg.index,
            region=cfg.region,
            session=sess,
        )
        resp = await client.describe_index()
        assert resp is not None
        assert resp.database.name == cfg.index


@pytest.mark.asyncio
async def test_retryable():
    class PineconeVectorClientExtended(PineconeVectorClient):
        called: bool = False

        async def _json_request_inner(
            self,
            method,
            url,
            request_model_instance: Optional[BaseModel] = None,
            response_model: Optional[Type[PydanticModelT]] = None,
        ) -> Optional[PydanticModelT]:
            if not self.called:
                self.called = True
                raise ClientError("test error")
            return await super()._json_request_inner(
                method, url, request_model_instance, response_model
            )

    cfg = Config()
    async with PineconeVectorClientExtended(
        api_key=cfg.api_key,
        project_id=cfg.project_id,
        index=cfg.index,
        region=cfg.region,
        retry=True,
    ) as client:
        resp = await client.describe_index()
        assert resp is not None
        assert resp.database.name == cfg.index
