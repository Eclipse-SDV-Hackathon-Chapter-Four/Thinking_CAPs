from aiohttp import web
from livekit.api import AccessToken, VideoGrants
import os

# LiveKit credentials (must be provided via environment variables)
API_KEY = os.environ.get("LIVEKIT_API_KEY")
API_SECRET = os.environ.get("LIVEKIT_API_SECRET")

# Default room name used for viewer connections
ROOM_NAME = os.environ.get("LIVEKIT_ROOM", "carla-room")


def require_env(var_name: str, value: str):
    if not value:
        raise RuntimeError(f"Missing required environment variable: {var_name}")


# Validate required configuration
require_env("LIVEKIT_API_KEY", API_KEY)
require_env("LIVEKIT_API_SECRET", API_SECRET)


async def token(request):
    """
    Generate a view-only LiveKit access token.

    Query parameters:
      - id: unique viewer identity
    """
    identity = request.query.get("id", "viewer")

    grants = VideoGrants(
        room_join=True,
        room=ROOM_NAME,
        can_publish=False,   # View-only access
        can_subscribe=True,
    )

    jwt = (
        AccessToken(API_KEY, API_SECRET)
        .with_identity(identity)
        .with_grants(grants)
        .to_jwt()
    )

    return web.json_response(
        {"token": jwt},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


async def options_handler(request):
    """
    CORS preflight handler.
    """
    return web.Response(
        status=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


async def health(request):
    """
    Health check endpoint.
    """
    return web.json_response({"status": "ok"})


app = web.Application()

# Token endpoint
app.router.add_route("GET", "/token", token)
app.router.add_route("OPTIONS", "/token", options_handler)

# Health endpoint
app.router.add_route("GET", "/health", health)

web.run_app(app, port=8080)
