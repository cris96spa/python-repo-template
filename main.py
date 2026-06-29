import argparse
import logging

from python_repo_template.func import random_sum
from utils.logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    logger = logging.getLogger(__name__)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--number", type=int, help="Input number")
    args = arg_parser.parse_args()
    number = args.number

    logger.info("-" * 50)
    logger.info(f"Input number: {number}")
    logger.info(f"Output number: {random_sum(number)}")
    logger.info("-" * 50)
