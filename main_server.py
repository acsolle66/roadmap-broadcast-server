import asyncio

from broadcast_server.argument_parser import set_up_arguments
from broadcast_server.server import BroadcastServer
from utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    args = set_up_arguments()
    logger.debug("Logging level: DEBUG")

    logger.debug("Initializing broadcast server")
    server = BroadcastServer(args.host, args.port)
    logger.debug(f"Broadcast server initialized")

    logger.info(f"Broadcast server running on: {args.host}:{args.port}")
    await server.run()


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Thanks for using me. Bye")
            break
        except Exception as e:
            logger.warning(f"Something bad happened: {e}. Restarting...")
