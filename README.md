# Simple Blackjack Game
This is a simple blackjack game I made. At this moment, I've only written it in Python, but I probably gonna write some more in other languages, when I'm bored. 

## Gameplay example
```shell:
Bet: 10                                        Round 4                               Bankroll: 49,980


Dealer: ♦2 ♥Q ♠10 (22)
┏━━━━━━━━━━━┓   ┏━━━━━━━━━━━┓   ┏━━━━━━━━━━━┓
┃2          ┃   ┃Q          ┃   ┃10         ┃
┃     ♦     ┃   ┃           ┃   ┃  ♠     ♠  ┃
┃           ┃   ┃           ┃   ┃     ♠     ┃
┃           ┃   ┃           ┃   ┃  ♠     ♠  ┃
┃           ┃   ┃     ♥     ┃   ┃           ┃
┃           ┃   ┃           ┃   ┃  ♠     ♠  ┃
┃           ┃   ┃           ┃   ┃     ♠     ┃
┃     ♦     ┃   ┃           ┃   ┃  ♠     ♠  ┃
┃          2┃   ┃          Q┃   ┃         10┃
┗━━━━━━━━━━━┛   ┗━━━━━━━━━━━┛   ┗━━━━━━━━━━━┛

Player (Hand 1): ♦Q ♣7 (17)
┏━━━━━━━━━━━┓   ┏━━━━━━━━━━━┓
┃Q          ┃   ┃7          ┃
┃           ┃   ┃  ♣     ♣  ┃
┃           ┃   ┃     ♣     ┃
┃           ┃   ┃           ┃
┃     ♦     ┃   ┃  ♣     ♣  ┃
┃           ┃   ┃           ┃
┃           ┃   ┃           ┃
┃           ┃   ┃  ♣     ♣  ┃
┃          Q┃   ┃          7┃
┗━━━━━━━━━━━┛   ┗━━━━━━━━━━━┛

Player (Hand 2): ♠J ♦4 ♣J (24)
┏━━━━━━━━━━━┓   ┏━━━━━━━━━━━┓   ┏━━━━━━━━━━━┓
┃J          ┃   ┃4          ┃   ┃J          ┃
┃           ┃   ┃  ♦     ♦  ┃   ┃           ┃
┃           ┃   ┃           ┃   ┃           ┃
┃           ┃   ┃           ┃   ┃           ┃
┃     ♠     ┃   ┃           ┃   ┃     ♣     ┃
┃           ┃   ┃           ┃   ┃           ┃
┃           ┃   ┃           ┃   ┃           ┃
┃           ┃   ┃  ♦     ♦  ┃   ┃           ┃
┃          J┃   ┃          4┃   ┃          J┃
┗━━━━━━━━━━━┛   ┗━━━━━━━━━━━┛   ┗━━━━━━━━━━━┛
Dealer busted. Hand 1 win
Hand 2 lose
You received a payout of $10
Do you want to play more rounds [Y/n]?
```
