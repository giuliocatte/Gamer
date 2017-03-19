from random import choice


class Player:

    setup_lines = 1
    turn_lines = 1

    def __init__(self, **kw):
        self.listener = self.coroutine()
        for k, v in kw.items():
            setattr(self, k, v)

    def setup(self, player_id, inp):
        self.id = player_id
        self.listener.send(None)

    def compute_move(self):
        '''
            given the input for a turn as a list of turn_lines string, computes the move and return it as a string
        '''
        return NotImplemented

    def coroutine(self):
        outp = None
        while True:
            inp = []
            for i in range(self.turn_lines):
                v = yield outp
                inp.append(v)
            self.process_turn_input(inp)
            outp = self.compute_move()

    def process_turn_input(self, inp):
        '''
            updates internal state for a turn input
        '''
        pass


class IOPlayer(Player):

    loud = True

    def setup(self, player_id, inp):
        if self.loud:
            print('player', player_id, 'received starting configuration:')
            for i in range(self.setup_lines):
                print('{}. {}'.format(i + 1, inp[i]))
        return super().setup(player_id, inp)

    def process_turn_input(self, inp):
        if self.loud:
            print('received input:')
            for i in range(self.turn_lines):
                print('{}. {}'.format(i + 1, inp[i]))

    def compute_move(self):
        print('enter move: ', end='')
        return input()


class RandomPlayer(Player):

    def compute_available_moves(self):
        '''
            returns all available moves for next turn as a list
            using internal state
        '''
        return NotImplemented

    def compute_move(self):
        mv = self.compute_available_moves()
        return choice(mv)