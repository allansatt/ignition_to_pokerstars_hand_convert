from decimal import Decimal
from random import randint
import re
import io

from src.models import IgnitionHandHistory, Player, Round, Action

def convert_ignition_to_open_hh(infile: io.TextIOWrapper) -> dict:
    hands = []
    open_hh_hand = None
    #TODO: don't abuse mutability to initialize this
    seat_map = {}
    while infile.buffer:
        if open_hh_hand:
            hands.append(open_hh_hand)
        open_hh_hand = _setup_hand(seat_map, infile)
        open_hh_hand.rounds = _read_rounds(open_hh_hand, seat_map, infile)
        return [open_hh_hand]

    if not open_hh_hand:
        print("No hands found in the input file.")
    else:
        hands.append(open_hh_hand)
    return hands

def _setup_hand(seat_map, infile):
    IGNITION_SEAT_REGEX = r'Seat ([\d]): (\w*\s?\w+\+?\d?)\s(?:\[ME\])?\s?\(\$(\d+\.?\d{0,2})'
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
            player_seat = int(seat_info.group(1))
            if player_seat not in seat_map:
                seat_map[player_seat] = randint(1,99999999)
            open_hh_hand.players.append(Player(
                name=str(seat_map[player_seat]),
                seat=int(player_seat),
                starting_stack=Decimal(seat_info.group(3)),
                is_sitting_out=False,
                id= seat_map[player_seat],
            )),
            if seat_info.group(2).lower() == 'dealer':
                open_hh_hand.dealer_seat = int(seat_info.group(1))
            if seat_info.group(3):
                open_hh_hand.hero_player_id = seat_map[player_seat]
            if line.startswith("Dealer"):
                continue
        line = infile.readline().strip()
    return open_hh_hand
def _read_rounds(open_hh_hand, seat_map, infile):
    line = infile.readline().strip()
    actions = []
    round = Round.model_construct(
        id=0,
        street="Preflop",
        actions=actions
    )
    rounds = []
    seat_to_cards = {}
    def _get_seat_from_position(pos):
        if pos == "Small Blind":
            return ((open_hh_hand.dealer_seat) % open_hh_hand.table_size) + 1
        if pos == "Big Blind":
            return ((open_hh_hand.dealer_seat + 1) % open_hh_hand.table_size) + 1
        if pos == "UTG":
            return ((open_hh_hand.dealer_seat + 2) % open_hh_hand.table_size) + 1
        if pos == "UTG+1":
            return ((open_hh_hand.dealer_seat + 3) % open_hh_hand.table_size) + 1
        if pos == "UTG+2":
            return ((open_hh_hand.dealer_seat + 4) % open_hh_hand.table_size) + 1
        if pos == "Dealer":
            return open_hh_hand.dealer_seat
        
        return None
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
            seat_number = _get_seat_from_position("Small Blind")
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat_number],
                    action="Post SB",
                    amount=open_hh_hand.small_blind_amount
                )
            )
        #Note: capitalization difference vs Small Blind
        if ": Big blind" in line:
            open_hh_hand.big_blind_amount = Decimal(re.search(r'\$(\d+\.?\d{0,2})', line).group(1))
            seat_number = _get_seat_from_position("Big Blind")
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
            seat = _get_seat_from_position(position)
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
            seat = _get_seat_from_position(position)
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
            seat = _get_seat_from_position(position)
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
            seat = _get_seat_from_position(position)
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
            seat = _get_seat_from_position(position)
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
            seat = _get_seat_from_position(position)
            actions.append(
                Action.model_construct(
                    action_number=len(actions),
                    player_id=seat_map[seat],
                    action="Fold",
                    cards=seat_to_cards[seat]
                )
            )
        line = infile.readline().strip()
    rounds.append(round)
    return rounds