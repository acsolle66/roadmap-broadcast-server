import asyncio

from broadcast_client.argument_parser import set_up_arguments
from broadcast_client.client import BroadcastClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    args = set_up_arguments()
    logger.debug("Logging level: DEBUG")

    logger.debug("Initializing broadcast client")
    client = BroadcastClient(args.host, args.port, args.user)
    logger.debug(f"Broadcast client initialized")

    logger.info(f"Client connected to broadcast server.")
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
        logger.debug("Tasks completed")
    except KeyboardInterrupt:
        logger.info("Thanks for using me. Bye")
    except Exception as e:
        logger.warning(f"Something bad happened: {e}.")
