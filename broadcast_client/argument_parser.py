import argparse


def set_up_arguments():
    parser = argparse.ArgumentParser(description="Start a simple broadcast server.")

    parser.add_argument(
        "--host",
        help="Broadcast server host (default: '127.0.0.1').",
        default="127.0.0.1",
    )

    parser.add_argument(
        "--port",
        type=int,
        help="Broadcast server port (default: 8888).",
        default=8888,
    )

    parser.add_argument(
        "--user",
        help="Username (default: 'anonymous')",
        default="anonymous",
    )

    args = parser.parse_args()

    return args
