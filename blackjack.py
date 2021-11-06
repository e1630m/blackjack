from random import shuffle, uniform
from os import system, name, get_terminal_size as tsize
from time import sleep


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = self.c_rank = rank[0] if rank != '10' else rank
        self.sr = self.suit + self.rank
        if suit in '♥♦':
            self.sr = '\033[1;31;49m' + self.sr + '\033[1;37;49m'
            self.suit = '\033[1;31;49m' + self.suit + '\033[1;37;49m'
            self.c_rank = '\033[1;31;49m' + self.c_rank + '\033[1;37;49m'
        self.is_alpha = self.rank[0] in 'AJQK'
        self.value = rank

    def __str__(self):
        return self.sr

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, r: str) -> None:
        self.__value = 10 + int(r[0] == 'A') if r.isalpha() else int(r)

    def display(self, hide: bool = False) -> list[str]:
        if hide:
            return ['┏━━━━━━━━━━━┓' if not i else
                    '┃███████████┃' if i != 10 else
                    '┗━━━━━━━━━━━┛' for i in range(11)]
        pad = ' ' * (self.rank != '10')
        s, v = self.suit + ' ', self.value
        mid_cen = (s * (v in (1, 3, 5, 9) or self.is_alpha)).ljust(2)
        midside = (s * (5 < v < 9)).ljust(2)
        rdiff_1 = (s * (v in (9, 10) and not self.is_alpha)).ljust(2)
        row_2up = (s * (v in (7, 8, 10) and not self.is_alpha)).ljust(2)
        row_2dn = (s * (v in (8, 10) and not self.is_alpha)).ljust(2)
        corners = (s * (v > 3 and not self.is_alpha)).ljust(2)
        top_bot = (s * (v in (2, 3))).ljust(2)
        return [
            '┏━━━━━━━━━━━┓',
            '┃{}         ┃'.format(self.c_rank + pad),
            '┃  {} {} {} ┃'.format(corners, top_bot, corners),
            '┃     {}    ┃'.format(row_2up),
            '┃  {}    {} ┃'.format(rdiff_1, rdiff_1),
            '┃  {} {} {} ┃'.format(midside, mid_cen, midside),
            '┃  {}    {} ┃'.format(rdiff_1, rdiff_1),
            '┃     {}    ┃'.format(row_2dn),
            '┃  {} {} {} ┃'.format(corners, top_bot, corners),
            '┃         {}┃'.format(pad + self.c_rank),
            '┗━━━━━━━━━━━┛']


class Shoe:
    def __init__(self, num_decks: int = 6, vb: bool = False):
        print(f'Generating a dealing shoe with {num_decks} decks', end='')
        self.shoe = []
        self.build_shoe(num_decks)

        print('\nShuffling the cards...' if vb else '', end='')
        shuffle(self.shoe)

        print('\nGenerating a random cut' if vb else '', end='')
        self.cut_deck()
        print(f'\nRemoved {52 * num_decks - len(self.shoe)} cards '
              f'({len(self.shoe)} cards remaining)' if vb else '', end='')
        print()

    def build_shoe(self, num_decks: int) -> None:
        for _ in range(num_decks):
            for s in '♠ ♥ ♦ ♣'.split():
                for r in 'Ace 2 3 4 5 6 7 8 9 10 Jack Queen King'.split():
                    self.shoe.append(Card(s, r))

    def cut_deck(self, minimum: float = 0.30, maximum: float = 0.50) -> None:
        cut = uniform(minimum, maximum)
        del self.shoe[:int(len(self.shoe) * cut)]

    def get_shoe(self) -> list[Card]:
        return self.shoe

    def get_length(self) -> int:
        return len(self.shoe)

    def deal(self) -> Card:
        return self.shoe.pop(0)


class Hand:
    def __init__(self, card: Card = None):
        self.hand = []
        if card:
            self.add_card(card)
        self.decision = ''

    def add_card(self, card: Card) -> None:
        self.hand.append(card)
        self.value = (sum(c.value for c in self.hand), 
                      sum(c.value == 11 for c in self.hand))

    def get_hand(self) -> list[Card]:
        return self.hand
        
    def get_printable(self, reveal: int = 22) -> list[str]:
        cards = [c.display() if reveal > i else c.display(hide=True)
                 for i, c in enumerate(self.hand)]
        return ['   '.join(c[i] for c in cards) for i in range(len(cards[0]))]

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, tn) -> None:
        t, n = tn
        while t > 21 and n:
            t -= 10
            n -= 1
        self.__value = t

    @property
    def decision(self) -> str:
        return self.__decision

    @decision.setter
    def decision(self, decision: str) -> None:
        self.__decision = decision

    def len(self) -> int:
        return len(self.hand)

    def is_busted(self) -> bool:
        return self.value > 21

    def is_blackjack(self) -> bool:
        return self.len() == 2 and self.value == 21

    def is_playable(self) -> bool:
        return self.value < 21 and self.decision not in ('s', 'dd')

    def is_splittable(self) -> bool:
        return self.len() == 2 and (self.hand[0].value == self.hand[1].value)


class Blackjack:
    def __init__(self):
        self.nt = name == 'nt'
        self.cls()
        print('\033[1;37;49mWelcome to the game of Blackjack', end='')
        self.shoe = self.generate_shoe()
        self.bankroll = self.get_i(
            f'\nEnter your bankroll [$100-$100m] (Default: ${50_000:,}): ',
            int(1e8), 100, 50_000)
        self.min_bet = max(5, self.bankroll // 1000 // 1000 * 1000)
        self.bet = self.initial_bet = self.num_round = 0
        self.play()

    def generate_shoe(self) -> Shoe:
        d = 6
        msg = f'\nEnter the number of decks [2-12] (Default: {d}): '
        return Shoe(self.get_i(msg, 12, 2, d), vb=True)

    @staticmethod
    def get_i(msg: str, hi: int = 6, lo: int = 2, default: int = 6) -> int:
        user_input = lo - 1
        while not (lo <= user_input <= hi):
            try:
                tmp = input(msg)
                user_input = int(tmp) if tmp != '' else default
                if not (lo <= user_input <= hi):
                    print('Input out of range. Please try again.')
            except ValueError:
                print('Invalid input. Please try again.')
        return user_input

    @staticmethod
    def get_b(msg: str, opt: str = 'YN') -> bool:
        user_input = '1'
        while user_input.upper()[0] not in opt:
            user_input = input(msg)
            if user_input == '':
                user_input = opt[0]
        return user_input.upper().startswith('Y')

    @staticmethod
    def take_decision(hand: Hand, hnum: str, possibles: list[str]) -> None:
        decision = ''
        if hand.len() > 2:
            del possibles[2:]
        elif not hand.is_splittable():
            del possibles[3:]
        opt = '/'.join(c if i else c.upper() for i, c in enumerate(possibles))
        while decision[:2].lower() not in possibles:
            decision = input(f'Enter your decision {hnum}[{opt}]: ')
            decision = possibles[0] if decision == '' else decision
        hand.decision = decision

    def take_bet(self) -> None:
        d = max(self.min_bet, self.bankroll // 1000 // 1000 * 10)
        msg = f'Place your bet (Default: ${d}): '
        self.bet = self.get_i(msg, self.bankroll, self.min_bet, d)
        self.initial_bet = self.bet
        self.bankroll -= self.bet

    def get_insurance_premium(self) -> int:
        premium = 0
        if self.dealer.get_hand()[0].value == 11:
            if self.get_b('Do you want to take an insurance [y/N]? ', 'NY'):
                premium = self.initial_bet // 2
                self.bankroll -= premium
        return premium

    def print_board(self, rv: int = 22) -> None:
        self.cls()
        width = tsize()[0]
        print(f'Bet: {self.bet:,}'.ljust((w := width // 3))
              + f'Round {self.num_round}'.center(w)
              + f'Bankroll: {self.bankroll:,}'.rjust(w))

        dh = f': {" ".join([str(c) for c in self.dealer.get_hand()][:rv])}'
        dv = f' ({self.dealer.value})'
        print(f'\n\nDealer{(rv > 0) * dh}{(rv > 1) * dv}')
        print('\n'.join([line for line in self.dealer.get_printable(rv)]))

        for i, h in enumerate(self.player):
            num = f' (Hand {i + 1})' * (len(self.player) > 1)
            print(f'\nPlayer{num}: {" ".join([str(c) for c in h.get_hand()])}'
                  f' ({h.value})')
            print('\n'.join([line for line in h.get_printable()]))

    def get_payout(self) -> int:
        payout, dv, lp = 0, self.dealer.value, len(self.player)
        for i, hand in enumerate(self.player):
            n = f'Hand {i + 1}' if lp > 1 else 'You'
            hv = hand.value
            dd = self.initial_bet * (1 + (1 * (hand.decision == 'dd')))
            if hand.is_busted() or hv < dv <= 21:
                print(f'{n} lose')
                continue
            elif dv > 21 or hv > dv:
                print('Dealer busted. ' * (dv > 21) + f'{n} win')
                payout += dd * (2.5 if hand.is_blackjack() else 2)
            elif dv == hv:
                print('Tie')
                payout += dd
        return payout

    def cls(self) -> None:
        if self.nt:
            system('cls')
        else:
            system('clear')

    def round(self) -> None:
        self.cls()
        self.take_bet()
        self.dealer, self.player = Hand(), [Hand()]
        for _ in range(2):
            self.player[0].add_card(self.shoe.deal())
            self.dealer.add_card(self.shoe.deal())
            sleep(0.2)
            self.print_board(rv=1)

        while any(hand.is_playable() for hand in self.player):
            for i, h in enumerate(self.player):
                if not h.is_playable():
                    continue
                self.print_board(rv=1)
                h_num = f'(Hand {i + 1}) ' * (len(self.player) > 1)
                self.take_decision(h, h_num, 'h s dd sp'.split())
                if (d := h.decision) != 's':
                    if d in ('dd', 'sp'):
                        self.bankroll -= self.initial_bet
                        self.bet += self.initial_bet
                    if d == 'sp':
                        self.player += [Hand(c) for c in h.get_hand()]
                        del self.player[i]
                        break
                    h.add_card(self.shoe.deal())

        in_play = not all(hand.is_busted() for hand in self.player)
        self.print_board(rv=1)
        sleep(0.5)
        premium = self.get_insurance_premium() if in_play else 0
        self.print_board()

        while self.dealer.value < 17 and in_play:
            self.dealer.add_card(self.shoe.deal())
            sleep(0.5)
            self.print_board()

        payout = self.get_payout()
        self.bankroll += payout
        print(f'You received a payout of ${payout}')
        if premium and self.dealer.get_hand()[1].value == 10:
            self.bankroll += premium * 2
            print(f'You received an insurance payout of ${premium * 2}')

    def play(self) -> None:
        more = True
        while more and self.bankroll >= self.min_bet:
            self.num_round += 1
            self.round()
            more = self.get_b('Do you want to play more rounds [Y/n]? ', 'YN')
            if (ls := self.shoe.get_length()) < 15:
                msg = f"Only {ls} cards left in dealer's shoe. "
                msg += "Do you want to replenish the shoe [Y/n]? "
                if self.get_b(msg, 'YN'):
                    self.shoe = self.generate_shoe()
                else:
                    print("Game Over (too few cards remaining)")
                    break


if __name__ == '__main__':
    Blackjack()
