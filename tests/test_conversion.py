from decimal import Decimal
from src.convert import convert_ignition_to_open_hh
import random
import deepdiff


from src.models import Action, IgnitionHandHistory, PlayerWin, Pot, Round
from src.models import Player

TEST_INPUT_PATH = "tests/HH20250716-232414 - 21171592 - RING - $0.02-$0.05 - HOLDEM - NL - TBL No.35104085.txt"

def test_convert_ignition_cash_to_open_hh():
    random.seed(42)
    expected_hand_1 = IgnitionHandHistory.model_construct(
        spec_version="1.4.6",
        site_name="ignition",
        network_name="bovada",
        bet_limit="NL",
        big_blind_amount=Decimal('0.05'),
        small_blind_amount=Decimal('0.02'),
        dealer_seat=5,
        players=[
            Player.model_construct(
                id=85822413,
                is_sitting_out=False,
                name="85822413",
                seat=1,
                starting_stack=Decimal('5'),
            ),
            Player.model_construct(
                id=14942604,
                is_sitting_out=False,
                name="14942604",
                seat=2,
                starting_stack=Decimal('2.34'),
            ),
            Player.model_construct(
                id=3356887,
                is_sitting_out=False,
                name="3356887",
                seat=3,
                starting_stack=Decimal('5.40'),
            ),
            Player.model_construct(
                id=99529224,
                is_sitting_out=False,
                name="99529224",
                seat=4,
                starting_stack=Decimal('0.95'),
            ),
            Player.model_construct(
                id=36913811,
                is_sitting_out=False,
                name="36913811",
                seat=5,
                starting_stack=Decimal('4.45'),
            ),
            Player.model_construct(
                id=32868829,
                is_sitting_out=False,
                name="32868829",
                seat=6,
                starting_stack=Decimal('4.87'),
            ),
        ],
        internal_version="0.1.0",
        tournament=False,
        game_number="4805145714",
        game_action="holdem",
        hero_player_id=32868829,
        start_date_utc="2025-07-16 23:26:00",
        table_name="35104085",
        table_size=6,
        version="1.4.7",
        rounds=[
            Round.model_construct(
                id=0,
                street="Preflop",
                actions=[
                    Action.model_construct(
                        action_number=0,
                        player_id=32868829,
                        action="Post SB",
                        amount=Decimal('0.02'),
                    ),
                    Action.model_construct(
                        action_number=1,
                        player_id=85822413,
                        action="Post BB",
                        amount=Decimal('0.05'),
                    ),
                    Action.model_construct(
                        action_number=2,
                        player_id=85822413,
                        action="Dealt Cards",
                        cards=['7c', 'Qc']
                    ),
                    Action.model_construct(
                        action_number=3,
                        player_id=14942604,
                        action="Dealt Cards",
                        cards=['Qd', 'Td']
                    ),
                    Action.model_construct(
                        action_number=4,
                        player_id=3356887,
                        action="Dealt Cards",
                        cards=['5c', 'Kh'] 
                    ),
                    Action.model_construct(
                        action_number=5,
                        player_id=99529224,
                        action="Dealt Cards",
                        cards=['Js', '3c'] 
                    ),
                    Action.model_construct(
                        action_number=6,
                        player_id=36913811,
                        action="Dealt Cards",
                        cards=['5d', '9s']
                    ),
                    Action.model_construct(
                        action_number=7,
                        player_id=32868829,
                        action="Dealt Cards",
                        cards=['8c', '6h']
                    ),
                    Action.model_construct(
                        action_number=8,
                        player_id=14942604,
                        action="Call",
                        amount=Decimal('0.05'),
                        cards=['Qd', 'Td']
                    ),
                    Action.model_construct(
                        action_number=9,
                        player_id=3356887,
                        action="Fold",
                        cards=['5c', 'Kh'] 
                    ),
                    Action.model_construct(
                        action_number=10,
                        player_id=99529224,
                        action="Fold",
                        cards=['Js', '3c'] 
                    ),
                    Action.model_construct(
                        action_number=11,
                        player_id=36913811,
                        action="Fold",
                        cards=['5d', '9s']
                    ),
                    Action.model_construct(
                        action_number=12,
                        player_id=32868829,
                        action="Call",
                        amount=Decimal('0.03'),
                        cards=['8c', '6h']
                    ),
                    Action.model_construct(
                        action_number=13,
                        player_id=85822413,
                        action="Raise",
                        amount=Decimal('0.10'),
                        cards=['7c', 'Qc']
                    ),
                    Action.model_construct(
                        action_number=14,
                        player_id=14942604,
                        action="Call",
                        amount=Decimal('0.10'),
                        cards=['Qd', 'Td']
                    ),
                    Action.model_construct(
                        action_number=15,
                        player_id=32868829,
                        action="Fold",
                        cards=['8c', '6h']
                    ),

                ],
            ),
            Round.model_construct(
                id=1,
                street="Flop",
                cards=['4h', 'Jh', '8h'],
                actions=[
                    Action.model_construct(
                        action_number=0,
                        player_id=85822413,
                        action="Check",
                        cards=['7c', 'Qc']
                    ),
                    Action.model_construct(
                        action_number=1,
                        player_id=14942604,
                        action="Check",
                        cards=['Qd', 'Td']
                    )
                ],
            ),
            Round.model_construct(
                id=2,
                street="Turn",
                cards=['Tc'],
                actions=[
                    Action.model_construct(
                        action_number=0,
                        player_id=85822413,
                        action="Check",
                        cards=['7c', 'Qc']
                    ),
                    Action.model_construct(
                        action_number=1,
                        player_id=14942604,
                        action="Bet",
                        amount=Decimal('0.28'),
                        cards=['Qd', 'Td']
                    ),
                    Action.model_construct(
                        action_number=2,
                        player_id=85822413,
                        action="Fold",
                        cards=['7c', 'Qc']
                    ),
                ],
            )
        ],
        pots=[
            Pot(
                number=0,
                amount=Decimal("0.35"),
                rake=Decimal("0.01"),
                jackpot=None,
                player_wins=[
                    PlayerWin(
                        player_id=14942604,
                        win_amount=Decimal("0.35"),
                        cashout_amount=None,
                        cashout_fee=None,
                        bonus_amount=None,
                        contributed_rake=Decimal("0.01"),
                    )
                ],
            )
        ],
    )
    expected_hand_2 = IgnitionHandHistory.model_construct(
        spec_version="1.4.6",
        site_name="ignition",
        network_name="bovada",
        bet_limit="NL",
        big_blind_amount=Decimal('0.05'),
        small_blind_amount=Decimal('0.02'),
        dealer_seat=5,
        players=[
            Player.model_construct(
                id=85822413,
                is_sitting_out=False,
                name="85822413",
                seat=1,
                starting_stack=Decimal('4.85'),
            ),
            Player.model_construct(
                id=14942604,
                is_sitting_out=False,
                name="14942604",
                seat=2,
                starting_stack=Decimal('2.53'),
            ),
            Player.model_construct(
                id=3356887,
                is_sitting_out=False,
                name="3356887",
                seat=3,
                starting_stack=Decimal('5.40'),
            ),
            Player.model_construct(
                id=99529224,
                is_sitting_out=False,
                name="99529224",
                seat=4,
                starting_stack=Decimal('0.95'),
            ),
            Player.model_construct(
                id=36913811,
                is_sitting_out=False,
                name="36913811",
                seat=5,
                starting_stack=Decimal('4.45'),
            ),
            Player.model_construct(
                id=32868829,
                is_sitting_out=False,
                name="32868829",
                seat=6,
                starting_stack=Decimal('4.82'),
            ),
        ],
        internal_version="0.1.0",
        tournament=False,
        game_number="4805146115",
        game_action="holdem",
        hero_player_id=32868829,
        start_date_utc="2025-07-16 23:27:00",
        table_name="35104085",
        table_size=6,
        version="1.4.7",
        rounds=[
            Round.model_construct(
                id=0,
                street="Preflop",
                actions=[
                    Action.model_construct(
                        action_number=0,
                        player_id=32868829,
                        action="Post SB",
                        amount=Decimal('0.02'),
                    ),
                    Action.model_construct(
                        action_number=1,
                        player_id=85822413,
                        action="Post BB",
                        amount=Decimal('0.05'),
                    ),
                    Action.model_construct(
                        action_number=2,
                        player_id=85822413,
                        action="Dealt Cards",
                        cards=['6d', '8h']
                    ),
                    Action.model_construct(
                        action_number=3,
                        player_id=14942604,
                        action="Dealt Cards",
                        cards=['3s', 'Kh']
                    ),
                    Action.model_construct(
                        action_number=4,
                        player_id=3356887,
                        action="Dealt Cards",
                        cards=['2h', '7s'] 
                    ),
                    Action.model_construct(
                        action_number=5,
                        player_id=99529224,
                        action="Dealt Cards",
                        cards=['Ah', '4c'] 
                    ),
                    Action.model_construct(
                        action_number=6,
                        player_id=36913811,
                        action="Dealt Cards",
                        cards=['8d', 'Qc']
                    ),
                    Action.model_construct(
                        action_number=7,
                        player_id=32868829,
                        action="Dealt Cards",
                        cards=['4s', '6s']
                    ),
                    Action.model_construct(
                        action_number=8,
                        player_id=14942604,
                        action="Fold",
                        amount=Decimal('0.05'),
                        cards=['2h', '7s']
                    ),
                    Action.model_construct(
                        action_number=9,
                        player_id=3356887,
                        action="Call",
                        cards=['Ah', '4c'] 
                    ),
                    Action.model_construct(
                        action_number=10,
                        player_id=99529224,
                        action="Fold",
                        cards=['8d', 'Qc']
                    ),
                    Action.model_construct(
                        action_number=11,
                        player_id=36913811,
                        action="Call",
                        cards=['4s', '6s']
                    ),
                    Action.model_construct(
                        action_number=12,
                        player_id=32868829,
                        action="Fold",
                        amount=Decimal('0.03'),
                        cards=['6d', '8h']
                    ),
                    Action.model_construct(
                        action_number=13,
                        player_id=32868829,
                        action="Check",
                        amount=Decimal('0.03'),
                        cards=['3s', 'Kh']
                    ),
                ],
            ),
            Round.model_construct(
                id=1,
                street="Flop",
                cards=['6c', '4h', '3c'],
                actions=[
                    Action.model_construct(
                        action_number=0,
                        player_id=85822413,
                        action="Check",
                        cards=['7c', 'Qc']
                    ),
                    Action.model_construct(
                        action_number=1,
                        player_id=14942604,
                        action="Check",
                        cards=['Qd', 'Td']
                    )
                ],
            ),
            Round.model_construct(
                id=2,
                street="Turn",
                cards=['Tc'],
                actions=[
                    Action.model_construct(
                        action_number=0,
                        player_id=85822413,
                        action="Check",
                        cards=['7c', 'Qc']
                    ),
                    Action.model_construct(
                        action_number=1,
                        player_id=14942604,
                        action="Bet",
                        amount=Decimal('0.28'),
                        cards=['Qd', 'Td']
                    ),
                    Action.model_construct(
                        action_number=2,
                        player_id=85822413,
                        action="Fold",
                        cards=['7c', 'Qc']
                    ),
                ],
            )
        ],
        pots=[
            Pot(
                number=0,
                amount=Decimal("0.35"),
                rake=Decimal("0.01"),
                jackpot=None,
                player_wins=[
                    PlayerWin(
                        player_id=14942604,
                        win_amount=Decimal("0.35"),
                        cashout_amount=None,
                        cashout_fee=None,
                        bonus_amount=None,
                        contributed_rake=Decimal("0.01"),
                    )
                ],
            )
        ],
    )
    with open(TEST_INPUT_PATH, 'r') as infile:
        result = convert_ignition_to_open_hh(infile)
    diff = deepdiff.DeepDiff(result, [expected_hand_1, expected_hand_2], significant_digits=6)
    assert not diff