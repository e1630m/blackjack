from random import shuffle, uniform
from os import system, name, get_terminal_size as tsize
from time import sleep


class Card(object):
    sdict = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
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

    def get_suit(self, colored=0) -> str:
        if colored and self.is_red:
            return Card.color['r'] + self.suit + Card.color['w']
        return self.suit

    def get_symbol(self, colored=0) -> str:
        if colored and self.is_red:
            return Card.color['r'] + self.symbol + Card.color['w']
        return self.symbol

    def get_rank(self, colored=0) -> str:
        r = self.rank[0] if self.rank != '10' else self.rank
        if colored and self.is_red:
            return Card.color['r'] + r + Card.color['w']
        return r

    def get_uid(self) -> int:
        return self.uid

    def get_value(self) -> int:
        return self.value

    def display(self, hide=0) -> list[str]:
        if hide:
            return ['┏━━━━━━━━━━━┓' if not i else
                    '┃███████████┃' if i != 10 else
                    '┗━━━━━━━━━━━┛' for i in range(11)]
        pad = ' ' * (self.get_rank() != '10')
        is_alpha = self.get_rank().isalpha()
        sym, val = self.get_symbol(1) + ' ', self.get_value()
        mid_cen = (sym * (val in (1, 3, 5, 9) or is_alpha)).ljust(2)
        midside = (sym * (5 < val < 9)).ljust(2)
        rdiff_1 = (sym * (val in (9, 10) and not is_alpha)).ljust(2)
        row_2up = (sym * (val in (7, 8, 10) and not is_alpha)).ljust(2)
        row_2dn = (sym * (val in (8, 10) and not is_alpha)).ljust(2)
        corners = (sym * (val > 3 and not is_alpha)).ljust(2)
        top_bot = (sym * (val in (2, 3))).ljust(2)
        return [
            '┏━━━━━━━━━━━┓',
            '┃{}         ┃'.format(self.get_rank(1) + pad),
            '┃  {} {} {} ┃'.format(corners, top_bot, corners),
            '┃     {}    ┃'.format(row_2up),
            '┃  {}    {} ┃'.format(rdiff_1, rdiff_1),
            '┃  {} {} {} ┃'.format(midside, mid_cen, midside),
            '┃  {}    {} ┃'.format(rdiff_1, rdiff_1),
            '┃     {}    ┃'.format(row_2dn),
            '┃  {} {} {} ┃'.format(corners, top_bot, corners),
            '┃         {}┃'.format(pad + self.get_rank(1)),
            '┗━━━━━━━━━━━┛']


class Shoe(object):
    def __init__(self, num_decks=6, vb=False):
        print(f'Generating a dealing shoe with {num_decks} decks', end='')
        self.last = 0
        self.shoe = self.build_shoe(num_decks)

        print('\nShuffling the cards...' if vb else '', end='')
        shuffle(self.shoe)

        print('\nGenerating a random cut' if vb else '', end='')
        self.cut_deck()
        print(f'\nRemoved {52 * num_decks - len(self.shoe)} cards '
              f'({len(self.shoe)} cards remaining)' if vb else '', end='')
        print()

    def build_shoe(self, num_decks: int) -> list[Card]:
        suits = 'Spade Heart Diamond Club'.split()
        ranks = 'Ace 2 3 4 5 6 7 8 9 10 Jack Queen King'.split()
        shoe = []
        for _ in range(num_decks):
            for suit in suits:
                for rank in ranks:
                    self.last += 1
                    shoe.append(Card(suit, rank, self.last))
        return shoe

    def cut_deck(self, minimum=0.30, maximum=0.50) -> None:
        cut = uniform(minimum, maximum)
        del self.shoe[:int(len(self.shoe) * cut)]

    def get_shoe(self) -> list[Card]:
        return self.shoe

    def get_length(self) -> int:
        return len(self.shoe)

    def deal(self, num_cards=1) -> list[Card]:
        cards = []
        for _ in range(num_cards):
            cards.append(self.shoe.pop(0))
        return cards


class Hand(object):
    def __init__(self, hand=None):
        self.hand = [] if hand is None else hand
        self.total_value = sum(c.get_value() for c in self.hand) if self.hand else 0
        self.num_aces = sum(c.get_value() == 11 for c in self.hand) if self.hand else 0
        self.hand_value = 0
        self.set_hand_value()
        self.decision = ''

    def add_cards(self, cards: list[Card]) -> None:
        for card in cards:
            self.hand.append(card)
            self.total_value += (v := card.get_value())
            self.num_aces += 1 if v == 11 else 0
            self.set_hand_value()

    def get_hand(self) -> list[Card]:
        return self.hand

    def get_printable(self, reveal=22) -> list[str]:
        cards = [c.display() if reveal > i else c.display(hide=True)
                 for i, c in enumerate(self.hand)]
        return ['   '.join(c[i] for c in cards) for i in range(len(cards[0]))]

    def get_hand_value(self) -> int:
        return self.hand_value

    def set_hand_value(self) -> None:
        if self.total_value <= 21:
            self.hand_value = self.total_value
        t, n = self.total_value, self.num_aces
        while n and t > 21:
            n -= 1
            t -= 10
        self.hand_value = t

    def get_decision(self) -> str:
        return self.decision

    def set_decision(self, decision: str) -> None:
        self.decision = decision

    def length(self) -> int:
        return len(self.hand)

    def is_busted(self) -> bool:
        return self.get_hand_value() > 21

    def is_blackjack(self) -> bool:
        return self.length() == 2 and self.hand_value == 21

    def is_playable(self) -> bool:
        return not (self.get_hand_value() >= 21 or self.decision in ('s', 'dd'))

    def is_splittable(self) -> bool:
        return self.length() == 2 and self.hand[0].get_value() == self.hand[1].get_value()


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

    def generate_shoe(self) -> Shoe:
        d = 6
        msg = f'\nEnter the number of decks [2-12] (Default: {d}): '
        return Shoe(self.get_int_input(msg, 12, 2, d), vb=True)

    @staticmethod
    def get_int_input(msg: str, hi=6, lo=2, default=6) -> int:
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
    def get_bool_input(msg: str, opt='YN') -> bool:
        user_input = '1'
        while user_input.upper()[0] not in opt:
            user_input = input(msg)
            if user_input == '':
                user_input = opt[0]
        return user_input.upper().startswith('Y')

    @staticmethod
    def take_decision(hand: Hand, msg: str, possibles: list[str]) -> None:
        decision = ''
        if hand.length() > 2:
            del possibles[2:]
        elif not hand.is_splittable():
            del possibles[3:]
        opt = '/'.join(c if i else c.upper() for i, c in enumerate(possibles))
        while decision[:2].lower() not in possibles:
            decision = input(msg + '[' + opt + ']: ')
            decision = possibles[0] if decision == '' else decision
        hand.set_decision(decision)

    def take_bet(self) -> None:
        d = max(self.min_bet, self.bankroll // 1000 // 1000 * 10)
        msg = f'Place your bet (Default: ${d}): '
        self.bet = self.get_int_input(msg, hi=self.bankroll, lo=self.min_bet, default=d)
        self.initial_bet = self.bet
        self.bankroll -= self.bet

    def get_insurance_premium(self) -> int:
        premium = 0
        if self.dealer.get_hand()[0].get_rank().startswith('A'):
            if self.get_bool_input('Do you want to take an insurance [y/N]? ', 'NY'):
                premium = self.initial_bet // 2
                self.bankroll -= premium
        return premium

    def print_board(self, rv=22) -> None:
        self.cls()
        width = tsize()[0]
        print(f'Bet: {self.bet:,}'.ljust((w := width // 3))
              + f'Round {self.num_round}'.center(w)
              + f'Bankroll: {self.bankroll:,}'.rjust(w))

        print(f'\n\nDealer'
              + (rv > 0) * f': {" ".join([str(c) for c in self.dealer.get_hand()][:rv])}'
              + (rv > 1) * f' ({self.dealer.get_hand_value()})')
        print('\n'.join([line for line in self.dealer.get_printable(rv)]))

        for i, h in enumerate(self.player):
            n = f'{(" (Hand " + str(i + 1) + ")") * (len(self.player) > 1)}'
            print(f'\nPlayer{n}: {" ".join([str(card) for card in h.get_hand()])}'
                  f' ({h.get_hand_value()})')
            print('\n'.join([line for line in h.get_printable()]))

    def get_payout(self) -> int:
        payout, dv, lp = 0, self.dealer.get_hand_value(), len(self.player)
        for i, h in enumerate(self.player):
            n = f'Hand {i + 1}' if lp > 1 else 'You'
            hv, dd = h.get_hand_value(), 1 + (1 * (h.get_decision() == 'dd'))
            if h.is_busted() or hv < dv <= 21:
                print(f'{n} lose')
                continue
            if dv > 21 or hv > dv:
                print('Dealer busted. ' * (dv > 21) + f'{n} win')
                payout += self.initial_bet * (2.5 if h.is_blackjack() else 2) * dd
            elif dv == hv:
                print('Tie')
                payout += self.initial_bet * dd
        return payout

    def cls(self) -> None:
        if self.nt:
            system('cls')
        else:
            system('clear')

    def round(self) -> None:
        self.cls()
        self.take_bet()
        self.dealer.__init__(self.shoe.deal(2))
        self.player = [Hand(self.shoe.deal(2))]
        
        if not self.player[0].is_blackjack():
            while any(h.is_playable() for h in self.player):
                for i, hand in enumerate(self.player):
                    if not hand.is_playable():
                        continue
                    self.print_board(rv=0)
                    s = f'(Hand {i + 1}) ' * (len(self.player) > 1)
                    self.take_decision(hand, f'Enter your decision {s}', 'h s dd sp'.split())
                    if (d := hand.get_decision()) != 's':
                        self.bankroll -= self.initial_bet if d in ('dd', 'sp') else 0
                        self.bet += self.initial_bet if d in ('dd', 'sp') else 0
                        if d == 'sp':
                            self.player += [Hand([hand.get_hand()[0]]), Hand([hand.get_hand()[1]])]
                            del self.player[i]
                            break
                        hand.add_cards(self.shoe.deal(1))

        in_play = not all(h.is_busted() for h in self.player)
        self.print_board(rv=1)
        sleep(0.5)
        premium = self.get_insurance_premium() if in_play else 0
        self.print_board()

        while self.dealer.get_hand_value() < 17 and in_play:
            self.dealer.add_cards(self.shoe.deal(1))
            sleep(0.5)
            self.print_board()

        payout = self.get_payout()
        self.bankroll += payout
        print(f'You received a payout of ${payout}')
        if premium and self.dealer.get_hand()[1].get_value() == 10:
            self.bankroll += premium * 2
            print(f'You received an insurance payout of ${premium * 2}')

    def play(self) -> None:
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
