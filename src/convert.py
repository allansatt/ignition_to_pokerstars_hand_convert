from decimal import Decimal
from random import randint
import re
import io
from src.models import IgnitionHandHistory, Player, PlayerWin, Pot, Round, Action

def convert_ignition_to_open_hh(infile: io.TextIOWrapper) -> dict:
    hands = []
    open_hh_hand = None
    pos = infile.tell()
    raw_line = infile.readline()
    infile.seek(pos)
    while raw_line != '':
        seat_map, position_map, open_hh_hand = _setup_hand_and_get_seat_map_and_position_map(infile)
        open_hh_hand.rounds, pots_minus_rakes = _read_rounds_and_pots(open_hh_hand, seat_map, position_map, infile)
        open_hh_hand.pots = _calculate_total_pots_from_summary_and_net_pots(pots_minus_rakes, infile)
        try:
            open_hh_hand.__class__.model_validate(open_hh_hand.model_dump())
        except Exception as e:
            raise e
        hands.append(open_hh_hand)
        pos = infile.tell()
        raw_line = infile.readline()
        while not raw_line.startswith("Ignition Hand #") and raw_line != '':
            raw_line = infile.readline()
        if raw_line.startswith("Ignition Hand #"):
            infile.seek(pos)
    if not open_hh_hand:
        print("No hands found in the input file.")
    return hands

def _setup_hand_and_get_seat_map_and_position_map(infile):
    IGNITION_SEAT_REGEX = r'Seat ([\d]): (\w*\s?\w+\+?\d?)\s(?:\[ME\])?\s?\(\$(\d+\.?\d{0,2})'
    #TODO: track user behavior across a single table (e.g. make seat_map consistent across hands)
    seat_map = {}
    position_map = {}
    line = infile.readline().strip()
    while 'Set dealer' not in line:
        if line.startswith("Ignition Hand #"):
            open_hh_hand = IgnitionHandHistory.model_construct()
            hand_id = re.search(r'Hand #(\d+)', line).group(1)
            table_id = re.search(r'TBL#(\d+)', line).group(1)
            hand_start_time = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line).group(1)
            game_type = re.search(r'TBL#\d+\s+(\w+)', line).group(1)
            open_hh_hand.game_number = hand_id
            open_hh_hand.game_type = game_type.lower()
            open_hh_hand.table_name = table_id
            open_hh_hand.start_date_utc = hand_start_time
            open_hh_hand.players = []
        if line.startswith("Seat "):
            seat_info = re.search(IGNITION_SEAT_REGEX, line)
            position_info = seat_info.group(2)
            player_seat = int(seat_info.group(1))
            seat_map[player_seat] = randint(1,99999999)
            position_map[position_info] = player_seat
            open_hh_hand.players.append(Player(
                name=str(seat_map[player_seat]),
                seat=int(player_seat),
                starting_stack=Decimal(seat_info.group(3)),
                is_sitting_out=False,
                id=seat_map[player_seat],
            )),
            if seat_info.group(2).lower() == 'dealer':
                open_hh_hand.dealer_seat = int(seat_info.group(1))
            if seat_info.group(3):
                open_hh_hand.hero_player_id = seat_map[player_seat]
            if line.startswith("Dealer"):
                continue
        line = infile.readline().strip()
    if 'dealer_seat' not in open_hh_hand.__dict__:
        dealer = position_map['Small Blind'] -1
        if dealer == 0:
            dealer = open_hh_hand.table_size
        if dealer in seat_map:
            raise ValueError("Non player dealer calculation.")
        open_hh_hand.dealer_seat = dealer
            
    return seat_map, position_map,open_hh_hand

def _read_rounds_and_pots(open_hh_hand, seat_map, position_map, infile):
    line = infile.readline().strip()
    actions = []
    round = Round.model_construct(
        id=0,
        street="Preflop",
        actions=actions
    )
    rounds = []
    pots = []
    seat_to_cards = {}
    while line != '*** SUMMARY ***':
        if line.startswith("*** FLOP ***"):
            rounds.append(round)
            cards_search = re.search(r'\[(\w\w) (\w\w) (\w\w)\]', line)
            actions = []
            round = Round.model_construct(
                id=1,
                street="Flop",
                cards=[cards_search.group(1), cards_search.group(2), cards_search.group(3)],
                actions=actions
            )
        if line.startswith("*** TURN ***"):
            rounds.append(round)
            cards_search = re.search(r'\w\w \w\w \w\w\] \[(\w\w)\]', line)
            actions = []
            round = Round.model_construct(
                id=2,
                street="Turn",
                cards=[cards_search.group(1)],
                actions=actions
            )
        if line.startswith("*** RIVER ***"):
            rounds.append(round)
            cards_search = re.search(r'\w\w \w\w \w\w \w\w\] \[(\w\w)\]', line)
            actions = []
            round = Round.model_construct(
                id=2,
                street="Turn",
                cards=[cards_search.group(1)],
                actions=actions
            )
        if ": Small Blind" in line:
            open_hh_hand.small_blind_amount = Decimal(re.search(r'\$(\d+\.?\d{0,2})', line).group(1))
            seat_number = position_map["Small Blind"]
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat_number],
                    action="Post SB",
                    amount=open_hh_hand.small_blind_amount
                )
            )
        #NOTE: capitalization difference vs Small Blind
        if ": Big blind" in line:
            open_hh_hand.big_blind_amount = Decimal(re.search(r'\$(\d+\.?\d{0,2})', line).group(1))
            seat_number = position_map["Big Blind"]
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat_number],
                    action="Post BB",
                    amount=open_hh_hand.big_blind_amount
                )
            )
        if "Card dealt to a spot" in line:
            regex_match = re.search(r'(\w+\s?\w*\+?\d?)\s(?:\s\[ME\]\s)?: Card dealt to a spot \[(\w\w) (\w\w)\]', line)
            position = regex_match.group(1)
            cards = [regex_match.group(2), regex_match.group(3)]
            seat = position_map[position]
            seat_to_cards[seat] = cards
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat],
                    action="Dealt Cards",
                    cards=cards
                )
            )
        if "Checks" in line:
            regex_match = re.search(r'(\w+\s?\w*\+?\d?)\s(?:\s\[ME\]\s)?: Checks', line)
            position = regex_match.group(1)
            seat = position_map[position]
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat],
                    action="Check",
                    cards=seat_to_cards[seat]
                )
            )
        if "Bets" in line:
            regex_match = re.search(r'(\w+\s?\w*\+?\d?)\s(?:\s\[ME\]\s)?: Bets \$(\d+\.?\d{0,2})', line)
            position = regex_match.group(1)
            amount = Decimal(regex_match.group(2))
            seat = position_map[position]
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat],
                    action="Bet",
                    amount=amount,
                    cards=seat_to_cards[seat]
                )
            )
        if "Calls" in line:
            regex_match = re.search(r'(\w+\s?\w*\+?\d?)\s(?:\s\[ME\]\s)?: Calls \$(\d+\.?\d{0,2})', line)
            position = regex_match.group(1)
            amount = Decimal(regex_match.group(2))
            seat = position_map[position]
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat],
                    action="Call",
                    amount=amount,
                    cards=seat_to_cards[seat]
                )
            )
        if "Raises" in line:
            regex_match = re.search(r'(\w+\s?\w*\+?\d?)\s(?:\s\[ME\]\s)?: Raises \$(\d+\.?\d{0,2}) to \$\d+\.?\d{0,2}', line)
            position = regex_match.group(1)
            amount = Decimal(regex_match.group(2))
            seat = position_map[position]
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat],
                    action="Raise",
                    amount=amount,
                    cards=seat_to_cards[seat]
                )
            )
        if "Folds" in line:
            regex_match = re.search(r'(\w+\s?\w*\+?\d?)\s(?:\s\[ME\]\s)?: Folds', line)
            position = regex_match.group(1)
            seat = position_map[position]
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat],
                    action="Fold",
                    cards=seat_to_cards[seat]
                )
            )
        #NOTE: Even though Open HH Doesn't put this in the rounds, Ignition puts it in the River.
        if "Hand result" in line:
            groups = re.search(r'(\w+ ?\w*\+?\d?) : Hand result(?:-Side pot)? \$(\d+\.\d\d)', line).groups()
            is_side = "-Side pot" in line
            if not pots:
                pots.append(Pot.model_construct(
                    number=0,
                    amount=Decimal('0.00'),
                    player_wins=[]
                ))
            if is_side and len(pots) == 1:
                pots.append(Pot.model_construct(
                    number=1,
                    amount=Decimal('0.00'),
                    player_wins=[]
                ))
            pot = pots[1] if is_side else pots[0]
            pot.amount += Decimal(groups[1])
            pot.player_wins.append(
                PlayerWin.model_construct(
                    player_id=seat_map[position_map[groups[0]]],
                    win_amount=Decimal(groups[1])
                )
            )
        line = infile.readline().strip()
    rounds.append(round)
    return rounds, pots

"""Ignition only gives individual payouts after rake, and a single total pot including all side pots and rake."""
def _calculate_total_pots_from_summary_and_net_pots(pots_minus_rakes, infile):
    line = infile.readline().strip()
    pots = []
    post_rake_total = sum([pot.amount for pot in pots_minus_rakes])
    while 'Total Pot' not in line:
        line = infile.readline().strip()
    total_pot = Decimal(re.search(r'Total Pot\(\$(\d+\.?\d{0,2})\)', line).group(1))
    for pot in pots_minus_rakes:
        pot_amt = pot.amount / post_rake_total * total_pot
        pot_rake = pot_amt - pot.amount
        new_player_wins = []
        for player_win in pot.player_wins:
            new_win_amount = player_win.win_amount / pot.amount * pot_amt
            new_player_win = PlayerWin.model_construct(
                player_id=player_win.player_id,
                win_amount=new_win_amount,
                contributed_rake=new_win_amount - player_win.win_amount
            )
            new_player_wins.append(new_player_win)
        pots.append(Pot.model_construct(
            number=pot.number,
            amount=pot_amt,
            rake=pot_rake,
            player_wins=new_player_wins
        ))
    return pots