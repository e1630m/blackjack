from random import shuffle, uniform
from os import system, name, get_terminal_size as tsize
from time import sleep


class Card(object):
    sdict = {'S': '♤', 'H': '♡', 'D': '♢', 'C': '♧'}
    color = {'r': '\033[1;31;49m', 'w': '\033[1;37;49m'}

    def __init__(self, suit, rank, uid):
        self.suit = suit
        self.symbol = Card.sdict[suit[0]]
        self.rank = rank
        self.uid = uid
        self.is_red = self.suit[0] in 'HD'
        self.value = 10 + (rank[0] == 'A') if rank.isalpha() else int(rank)

    def __str__(self):
        r = self.get_rank()
        if self.is_red:
            return Card.color['r'] + self.symbol + r + Card.color['w']
        return self.symbol + r

    def get_suit(self, color=0):
        if color and self.is_red:
            return Card.color['r'] + self.suit + Card.color['w']
        return self.suit

    def get_symbol(self, color=0):
        if color and self.is_red:
            return Card.color['r'] + self.symbol + Card.color['w']
        return self.symbol

    def get_rank(self, color=0):
        r = self.rank[0] if self.rank != '10' else self.rank
        if color and self.is_red:
            return Card.color['r'] + r + Card.color['w']
        return r

    def get_uid(self):
        return self.uid

    def get_value(self):
        return self.value

    def display(self, hide=0):
        pad = ' ' * (self.get_rank() != '10')
        is_alpha = self.get_rank().isalpha()
        sym, val = self.get_symbol(1) + ' ', self.get_value()
        mid_c = (sym * (val in (1, 3, 5, 9) or is_alpha)).ljust(2)
        mid_s = (sym * (5 < val < 9)).ljust(2)
        rdiff_1 = (sym * (val in (9, 10) and not is_alpha)).ljust(2)
        row_2up = (sym * (val in (7, 8, 10) and not is_alpha)).ljust(2)
        row_2dn = (sym * (val in (8, 10) and not is_alpha)).ljust(2)
        corners = (sym * (val > 3 and not is_alpha)).ljust(2)
        rdiff_3 = (sym * (val in (2, 3))).ljust(2)
        lines = [
            '┏━━━━━━━━━━━┓',
            '┃{}         ┃'.format(self.get_rank(1) + pad),
            '┃  {} {} {} ┃'.format(corners, rdiff_3, corners),
            '┃     {}    ┃'.format(row_2up),
            '┃  {}    {} ┃'.format(rdiff_1, rdiff_1),
            '┃  {} {} {} ┃'.format(mid_s, mid_c, mid_s),
            '┃  {}    {} ┃'.format(rdiff_1, rdiff_1),
            '┃     {}    ┃'.format(row_2dn),
            '┃  {} {} {} ┃'.format(corners, rdiff_3, corners),
            '┃         {}┃'.format(pad + self.get_rank(1)),
            '┗━━━━━━━━━━━┛'
        ]
        if hide:
            for r in range(1, 10):
                lines[r] = '┃███████████┃'
        return lines


class Shoe(object):
    def __init__(self, num_decks=6, vb=False):
        print(f'Generating a dealing shoe with {num_decks} decks', end='')
        self.shoe = self.build_shoe(num_decks)

        print('\nShuffling the cards...' if vb else '', end='')
        shuffle(self.shoe)

        print('\nGenerating a random cut' if vb else '', end='')
        self.shoe = self.cut_deck(self.shoe)
        print(f'\nRemoved {52 * num_decks - len(self.shoe)} cards '
              f'({len(self.shoe)} cards remaining)' if vb else '', end='')
        print()

    def build_shoe(self, num_decks):
        suits = 'Spade Heart Diamond Club'.split()
        ranks = 'Ace 2 3 4 5 6 7 8 9 10 Jack Queen King'.split()
        shoe = []
        for _ in range(num_decks):
            for suit in suits:
                for rank in ranks:
                    shoe.append(Card(suit, rank, len(shoe)))
        return shoe

    def cut_deck(self, shoe, minimum=0.30, maximum=0.50):
        cut = uniform(minimum, maximum)
        del shoe[:int(len(shoe) * cut)]
        return shoe

    def get_shoe(self):
        return self.shoe

    def get_length(self):
        return len(self.shoe)

    def deal(self, num_cards=1):
        cards = []
        for _ in range(num_cards):
            cards.append(self.shoe.pop(0))
        return cards


class Hand(object):
    def __init__(self):
        self.total_value = 0
        self.num_aces = 0
        self.hand = []

    def add_cards(self, cards):
        for card in cards:
            self.hand.append(card)
            self.total_value += (v := card.get_value())
            self.num_aces += 1 if v == 11 else 0

    def get_hand(self):
        return self.hand

    def get_printable(self, reveal=22):
        cards = [c.display() if reveal > i else c.display(hide=True)
                 for i, c in enumerate(self.hand)]
        lines = []
        for i in range(len(cards[0])):
            line = ''
            for card in cards:
                line += card[i] + '   '
            lines.append(line)
        return lines

    def get_total_value(self):
        if self.total_value <= 21:
            return self.total_value
        if self.num_aces:
            t, n = self.total_value, self.num_aces
            while n:
                n -= 1
                t -= 10
                if t <= 21:
                    return t
        return self.total_value

    def is_busted(self):
        return self.get_total_value() > 21

    def length(self):
        return len(self.hand)


class Blackjack(object):
    def __init__(self):
        self.nt = name == 'nt'
        self.cls()
        print('\033[1;37;49mWelcome to the game of Blackjack', end='')
        self.shoe = self.generate_shoe()
        self.bankroll = self.get_int_input(
            f'\nEnter your bankroll [$100-$100m] (Default: ${50_000:,}): ',
            int(1e8), 100, 50_000)
        self.min_bet = max(5, self.bankroll // 1000 // 1000 * 1000)
        self.dealer = Hand()
        self.player = [Hand()]
        self.bet = 0
        self.initial_bet = 0
        self.num_round = 0
        self.play()

    def generate_shoe(self):
        d = 6
        msg = f'\nEnter the number of decks [2-12] (Default: {d}): '
        return Shoe(self.get_int_input(msg, 12, 2, d), vb=True)

    @staticmethod
    def get_int_input(msg, hi=6, lo=2, default=6):
        user_input = lo - 1
        while user_input < lo or user_input > hi:
            try:
                tmp = input(msg)
                user_input = int(tmp) if tmp != '' else default
                if not (lo <= user_input <= hi):
                    print('Input out of range. Please try again.')
            except ValueError:
                print('Invalid input. Please try again.')
        return user_input

    @staticmethod
    def get_bool_input(msg, opt='YN'):
        user_input = '1'
        while user_input.upper()[0] not in opt:
            user_input = input(msg)
            if user_input == '':
                user_input = opt[0]
        return user_input.upper().startswith('Y')

    def take_bet(self):
        d = max(self.min_bet, self.bankroll // 1000 // 1000 * 10)
        msg = f'Place your bet (Default: ${d}): '
        self.bet = self.get_int_input(msg, hi=self.bankroll, lo=self.min_bet, default=d)

    def take_choice(self, player, msg, choices):
        choice = ''
        h = player.get_hand()
        if (p := len(h)) > 2:
            del choices[2:]
        elif p == 2 and h[0].get_value() != h[1].get_value():
            del choices[3:]
        opt = '/'.join(c if i else c.upper() for i, c in enumerate(choices))
        while choice[:2].lower() not in choices:
            choice = input(msg + '[' + opt + ']: ')
            choice = choices[0] if choice == '' else choice
        return choice.lower()

    def take_insurance_premium(self):
        premium = 0
        if self.dealer.get_hand()[0].get_rank().startswith('A'):
            if self.get_bool_input('Do you want to take an insurance [y/N]? ', 'NY'):
                premium = self.bet // 2
                self.bankroll -= premium
        return premium

    def print_board(self, rv=22):
        self.cls()
        width = tsize()[0]
        print(f'Bet: {self.bet:,}'.ljust((w := width // 3))
              + f'Round {self.num_round}'.center(w)
              + f'Bankroll: {self.bankroll:,}'.rjust(w))

        print(f'\n\nDealer'
              + (rv > 0) * f': {" ".join([str(c) for c in self.dealer.get_hand()][:rv])}'
              + (rv > 1) * f' ({self.dealer.get_total_value()})')
        print('\n'.join([line for line in self.dealer.get_printable(rv)]))

        for i, p in enumerate(self.player):
            n = f'{(" (Hand " + str(i + 1) + ")") * (len(self.player) > 1)}'
            print(f'\n\nPlayer{n}: {" ".join([str(c) for c in p.get_hand()])}'
                  f' ({p.get_total_value()})')
            print('\n'.join([line for line in p.get_printable()]))

    def get_payout(self, choices):
        dv = self.dealer.get_total_value()
        lp = len(self.player)
        payout = 0
        for i, p in enumerate(self.player):
            dd = 2 if choices[i] == 'dd' else 1
            pv = p.get_total_value()
            h = f'Hand {i + 1}' if lp > 1 else 'You'
            if pv > 21:
                print(f'{h} lose')
            elif dv > 21 or pv > dv:
                print('Dealer busted. ' * (dv > 21) + f'{h} win')
                payout += self.initial_bet * (2 if pv != 21 or p.length() > 2 else 2.5) * dd
            elif dv == pv:
                print('Tie')
                payout += self.initial_bet * dd
            else:
                print(f'{h} lose')
        return payout

    def cls(self):
        if self.nt:
            system('cls')
        else:
            system('clear')

    def round(self):
        self.cls()
        self.take_bet()
        self.initial_bet = self.bet
        self.bankroll -= self.bet
        self.dealer.__init__()
        self.dealer.add_cards(self.shoe.deal(2))
        self.player = [Hand()]
        self.player[0].add_cards(self.shoe.deal(2))

        self.print_board(rv=0)
        
        choices = ['']
        if not self.player[0].get_total_value() == 21:
            while any(choices[i] not in ('s', 'dd') for i, p in enumerate(self.player) if not p.is_busted()):
                for i, p in enumerate(self.player):
                    if p.is_busted() or choices[i] in ('s', 'dd'):
                        continue
                    s = f'(Hand {i + 1}) ' * (len(self.player) > 1)
                    choices[i] = self.take_choice(p, f'Enter your decision {s}', 'h s dd sp'.split())
                    if choices[i] in ('h', 'dd'):
                        if choices[i] == 'dd':
                            self.bankroll -= self.bet
                            self.bet *= 2
                        p.add_cards(self.shoe.deal(1))
                        self.print_board(rv=0)
                        if p.is_busted():
                            print("You're busted")
                            break
                    if p.length() == 2 and choices[i] == 'sp':
                        self.player += [Hand(), Hand()]
                        for j in range(-1, -3, -1):
                            self.player[j].add_cards([p.get_hand()[j]])
                            choices.append('')
                        del self.player[i]
                        del choices[i]
                        self.bet += self.initial_bet
                        self.bankroll -= self.initial_bet
                        self.print_board(rv=0)
                        break

        self.print_board(rv=1)
        sleep(0.5)
        premium = self.take_insurance_premium()
        self.print_board()

        while self.dealer.get_total_value() < 17 and not all(p.is_busted() for p in self.player):
            self.dealer.add_cards(self.shoe.deal(1))
            sleep(0.5)
            self.print_board()

        payout = self.get_payout(choices)
        self.bankroll += payout
        self.print_board()
        print(f'You received a payout of ${payout}')
        if premium and self.dealer.get_hand()[1].get_value() == 10:
            self.bankroll += 10000
            self.bankroll += premium * 3
            print(f'You received an insurance payout of ${premium * 2}')

    def play(self):
        more = True
        while more and self.bankroll >= self.min_bet:
            self.num_round += 1
            self.round()
            more = self.get_bool_input('Do you want to play more rounds [Y/n]? ', 'YN')
            if (ls := self.shoe.get_length()) < 15:
                msg = f"Only {ls} cards left in dealer's shoe. "
                msg += "Do you want to replenish the shoe [Y/n]? "
                if self.get_bool_input(msg, 'YN'):
                    self.shoe = self.generate_shoe()
                else:
                    print("Game Over (too few cards remaining)")
                    break


if __name__ == '__main__':
    Blackjack()
