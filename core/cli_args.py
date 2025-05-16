import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--fresh-start", 
        action="store_true", 
        help="Liquidate all positions before running"
    )

    parser.add_argument(
        "--strat-log", 
        action="store_true", 
        help="Enable strategy JSON logging"
    )

    parser.add_argument(
        "--log-level", 
        default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level for consol/file logs"
    )

    parser.add_argument(
        "--log-to-file",
        action="store_true",
        help="Write logs to file instead of just printing to stdout"
    )
    
    return parser.parse_args()
