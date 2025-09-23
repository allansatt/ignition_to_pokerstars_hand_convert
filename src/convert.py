from decimal import Decimal
from random import randint
import re
import io

from src.models import IgnitionHandHistory, Player

def convert_ignition_to_open_hh(infile: io.TextIOWrapper) -> dict:
    hands = []
    open_hh_hand = None
    seat_map = {}
    while infile.buffer:
        if open_hh_hand:
            hands.append(open_hh_hand)
        open_hh_hand = _setup_hand(seat_map, infile)
        break
                

    if not open_hh_hand:
        print("No hands found in the input file.")
    else:
        hands.append(open_hh_hand)
    return hands

def _setup_hand(seat_map, infile):
    IGNITION_SEAT_REGEX = r'Seat ([\d]): (\w*\s?\w+\+?\d?)\s(\[ME\])?\s?\(\$(\d+\.?\d{0,2})'
    line = infile.readline().strip()
    while line != "*** HOLE CARDS ***":
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
            seat_info = re.search(IGNITION_SEAT_REGEX, line).groups(0)
            player_seat = seat_info[0]
            if player_seat not in seat_map:
                seat_map[player_seat] = randint(1,99999999)
            open_hh_hand.players.append(Player(
                name=str(seat_map[player_seat]),
                seat=int(player_seat),
                starting_stack=Decimal(seat_info[3]),
                is_sitting_out=False,
                id= seat_map[player_seat],
            )),
            if seat_info[1].lower() == 'dealer':
                open_hh_hand.dealer_seat = seat_info[0]
            if seat_info[2]:
                open_hh_hand.hero_player_id = seat_map[player_seat]
            if line.startswith("Dealer"):
                continue
        if line.startswith("Small Blind"):
            open_hh_hand.small_blind_amount = Decimal(re.search(r'\$(\d+\.?\d{0,2})', line).group(1))
        if line.startswith("Big Blind"):
            open_hh_hand.big_blind_amount = Decimal(re.search(r'\$(\d+\.?\d{0,2})', line).group(1))
        line = infile.readline().strip()
        
    return open_hh_hand