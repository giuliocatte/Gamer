# Gamer (a better name still to be found)

Quando trovo la voglia scrivo anche questo file in inglese.
Già buona parte delle docstring e dei commenti lo sono,
ma ho finito le energie al riguardo.

I tried to write most of docstring and comments in english, but
probably something in italian survived, so, if ever some english
speaking fellow reads this code: sorry pal.

## Requirements

This software has been developed with python 3.6; probably it'll work
also with previous versions, but sooner or later I'll throw in
asyncio, so 3.4+ will be required.

As non-standard dependencies, I use tensorflow (I used the dumbest
installation for macos without gpu), numpy (which is actually
required for tensorflow, so I'm not sure I should write it here),
colorama (right now just for Connect4), and python fire for
firing the neural network trainers.

Many thanks to Daniel Slater from whom
I copypasted some [slices of code](https://github.com/DanielSlater/AlphaToe), and learned some techniques
(here's an excellent [youtube video](https://www.youtube.com/watch?v=Meb5hApAnj4)).

## Usage

For starters, you could run play.py from main directory.
It would ask some interactive input for the game configuration.
Neural networks won't work until trained, so you will be getting an
exception if you select them as an opponent.

### Network Training

To train your tictactoe network, you could run:
```
python3 tictactoe/nn.py --train-with-minimax
```
It will take a lot of hours, so maybe do it overnight (*and* the day after, probably).
If you're just interested in making it work quick you could use:
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
please let me know. I'm not done with it yet. Probably i'll try mixing
the AIs for is opponents, to reduce overfitting.

Besides, if you are in the mood for doing a ton of games, you can
train the network against yourself, using:
```
python3 tictactoe/nn.py --manual-training
```
