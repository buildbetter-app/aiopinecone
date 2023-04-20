import logging

from aiohttp import ClientConnectionError, ClientPayloadError, ClientResponseError, ServerDisconnectedError, ServerTimeoutError
from aiohttp import ClientConnectorError
from aiohttp import ClientError
from aiohttp import ClientOSError
from aiohttp import ServerConnectionError
from tenacity import retry
from tenacity import RetryCallState
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random_exponential


logger: logging.Logger = logging.getLogger(__name__)


def log_it(retry_state: RetryCallState) -> None:
    if retry_state.outcome is not None and retry_state.outcome.failed:
        ex = retry_state.outcome.exception()
        verb, value = "raised", f"{ex.__class__.__name__}: {ex}"
        exc_info = retry_state.outcome.exception()
    else:
        if retry_state.outcome is None:
            verb, value = "called", "None"
        else:
            verb, value = "returned", retry_state.outcome.result()
        exc_info = None# exc_info does not apply when no exception

    retry_seconds = retry_state.next_action and retry_state.next_action.sleep
    logger.info(
        f"Retrying {retry_state.fn} "
        f"in {retry_seconds} seconds as it {verb} {value}.",
        exc_info=exc_info,
    )


def get_retryer(max_retries: int = 5, min_seconds: int = 3, max_seconds: int = 30):
    return retry(
        reraise=True,
        stop=stop_after_attempt(max_retries),
        wait=wait_random_exponential(min=min_seconds, max=max_seconds),
        retry=(
            retry_if_exception_type(ClientError)
            | retry_if_exception_type(ClientOSError)
            | retry_if_exception_type(ClientConnectionError)
            | retry_if_exception_type(ClientConnectorError)
            | retry_if_exception_type(ServerConnectionError)
            | retry_if_exception_type(ServerTimeoutError)
            | retry_if_exception_type(ServerDisconnectedError)
        ),
        before_sleep=log_it,
    )
