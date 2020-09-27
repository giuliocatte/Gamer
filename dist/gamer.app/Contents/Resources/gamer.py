
def main():
    from play import Play
    p = Play()
    print('choose game:')
    print('1. tic tac toe')
    print('2. connectfour')
    print('3. chess')
    print('4. brasserie (default)')
    game = int(input() or 4) - 1
    getattr(p, ['ttt', 'c4', 'chess', 'brasserie'][game])()
    print('any key to close')
    input()


if __name__ == '__main__':
    main()
