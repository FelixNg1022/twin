from app.channels.base import Channel


class WebChannel(Channel):
    """Buffers outbound messages for the current HTTP request.

    One instance per request. The FastAPI route creates it, passes it to the
    graph runner, then reads `messages` after the graph run completes and
    returns them in the HTTP response.
    """

    def __init__(self) -> None:
        self.messages: list[str] = []

    async def deliver(self, session_id: str, text: str) -> None:
        self.messages.append(text)
