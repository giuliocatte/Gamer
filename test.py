
import logging

from tictactoe.play import test_game

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s %(message)s', level=logging.WARN)
from core.main import match_logger, player_logger, ref_logger

match_logger.setLevel(logging.WARN)
player_logger.setLevel(logging.DEBUG)
ref_logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    test_game()

