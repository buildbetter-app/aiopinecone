from aiohttp import ClientSession
from pydantic import BaseSettings
import pytest

from aiopinecone.client import PineconeVectorClient
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
