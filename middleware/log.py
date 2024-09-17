import logging
from fastapi import Request
# Configure the logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        logging.info('\n')
        async def wrapped_send(message):
            # Log the response status code
            if 'status' in message:
                logging.info(f"Response status code: {message['status']}")
            if 'body' in message:
                logging.info(f"Response body: {message['body']}")

            await send(message)
        # Log the request
        logging.info(f"Incoming request: {scope['method']} {scope['path']}")

        # Call the next middleware or endpoint
        await self.app(scope, receive, wrapped_send)