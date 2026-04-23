from abc import ABC, abstractmethod


class Channel(ABC):
    """Outbound delivery abstraction.

    Nodes call channel.deliver(...) without knowing whether they're talking
    to a web client, Photon Spectrum, or anything else. Inbound messages are
    handled by the delivery system's own route handler (FastAPI route for
    web, webhook for Photon), not by this ABC.
    """

    @abstractmethod
    async def deliver(self, session_id: str, text: str) -> None:
        """Send a message to the user. Implementations decide how."""
