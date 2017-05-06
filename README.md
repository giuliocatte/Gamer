# Gamer (a better name still to be found)

Little proof of concept framework to playtest AIs at various games.<br>
Still very WIP.

There is a Match class, where the game and the players are plugged in.
So you can basically devise your own AI, and make it play against
another AI, or even yourself.

In full [codingame](https://www.codingame.com) fashion, I wanted
players and the "referee" of the game to communicate with sequences of
strings, so that easily players could be external programs.

I tried to write most of docstring and comments in english, but
probably something in italian survived so, if ever some english
speaking fellow reads this code: sorry pal.

## Requirements

This software has been developed with python 3.6; probably it'll work
also with previous versions, but sooner or later I'll throw in
asyncio, so 3.4+ will be required.

As non-standard dependencies, I use tensorflow (I used the dumbest
installation for macos without gpu), numpy (which is actually
required for tensorflow, so I'm not sure I should write it here),
colorama for interactive output, and Python Fire for
CLI.

Many thanks to Daniel Slater from whom
I copypasted some [pieces of code](https://github.com/DanielSlater/AlphaToe), and learned some techniques
(here's an excellent [youtube video](https://www.youtube.com/watch?v=Meb5hApAnj4)).

## Usage

For starters, you could run
```
python3 play.py {gamename}
```
from main directory.
Right now, the only implemented games are `ttt` for tic tac toe
 and `c4` for connect four.
It would ask some interactive input for the game configuration.
Neural networks won't work until trained, so you will be getting an
exception if you select them as an opponent.

Since CLI is run by Python Fire, the better way to understand the commands
is to have a look at the code. For instance
```
python3 play.py --p_log DEBUG --m_log DEBUG --r_log DEBUG - chess --clear_board False
```
will start a very verbose chess match, without the page clear after every
move so that the log would be readable.

Aside from neural network training, there are two main file you will
execute like this. The first is the aforementioned play.py, the second
one is arena.py, which is a script to pit an AI verus another, have them
to play a lot of matches, and get some stats. Running the "explain"
method, will instead run a single game, with verbose logging, so that the
 choices of the AIs could be debugged.

### Network Training

To train for instance your tictactoe network, you could run:
```
python3 tictactoe/nn.py --train-with-minimax
```
It will take a lot of hours, so maybe do it overnight (*and* the day after, probably).
If you're just interested in making it work quickly you could use:
```
python3 tictactoe/nn.py --train-with-random
```
but AI will suck.

I had some problems of overfitting in training the network versus the
minimax AI, because a specific game pattern wasn't learned. To
correct the behaviour I added a specific training course for that
pattern, if you have the same problem you can run:
```
python3 tictactoe/nn.py --corrective
```
Still, AI isn't perfect, sometimes it goes for a draw when it could win.
If you discover a way of training it that yields better results,
please let me know. I'm not done with it yet, probably i'll try mixing
the AIs for is opponents, to reduce overfitting.

Besides, if you are in the mood for doing a ton of games, you can
train the network against yourself, using:
```
python3 tictactoe/nn.py --manual-training
```
