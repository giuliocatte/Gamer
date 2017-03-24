
from core.main import Match, SequentialGame
from .players import IOCFPlayer, RandomCFPlayer
from .referee import ConnectFour, DRAW


def test_game():
    players = [
            IOCFPlayer(),
            RandomCFPlayer()
    ]

    match = Match(SequentialGame(referee_class=ConnectFour), players=players)
    outcome = match.run()
    if outcome == DRAW:
        print('Draw!')
    else:
        print('player {} wins!'.format(outcome))
