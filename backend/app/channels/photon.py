from app.channels.base import Channel


class PhotonChannel(Channel):
    """Stub for Photon Spectrum SDK (Ditto's real iMessage delivery path).

    Not wired in this demo. The existence of this class alongside WebChannel
    is the architectural point: agent logic in app.agent.nodes doesn't care
    which one it's talking to.

    Real implementation would:
      1. Initialize the Photon Spectrum SDK client with Ditto's credentials
      2. Look up the user's phone number or iMessage handle by session_id
      3. Call photon_client.send_imessage(handle, text)

    See: https://photon-spectrum-sdk-docs.example/ (placeholder)
    """

    async def deliver(self, session_id: str, text: str) -> None:
        raise NotImplementedError(
            "PhotonChannel is a stub — wire the Photon Spectrum SDK to enable."
        )
