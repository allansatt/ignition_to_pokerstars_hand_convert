from datetime  import datetime
from typing import List, Optional
from decimal import Decimal
from typing_extensions import Literal
from pydantic import BaseModel

ACTIONS = Literal[
    "Dealt Cards",
    "Mucks Cards",
    "Shows Cards",
    "Post Ante",
    "Post SB",
    "Post BB",
    "Straddle",
    "Post Dead",
    "Post Extra Blind",
    "Fold",
    "Check",
    "Bet",
    "Raise",
    "Call",
    "Added Chips",
    "Sits Down",
    "Stands Up",
    "Add to Pot"
]
CARDS = Literal[
    '2s', '2h', '2d', '2c',
    '3s', '3h', '3d', '3c',
    '4s', '4h', '4d', '4c',
    '5s', '5h', '5d', '5c',
    '6s', '6h', '6d', '6c',
    '7s', '7h', '7d', '7c',
    '8s', '8h', '8d', '8c',
    '9s', '9h', '9d', '9c',
    'Ts', 'Th', 'Td', 'Tc',
    'Js', 'Jh', 'Jd', 'Jc',
    'Qs', 'Qh', 'Qd', 'Qc',
    'Ks', 'Kh', 'Kd', 'Kc',
    'As', 'Ah', 'Ad', 'Ac'
]

class Speed(BaseModel):
    type: Literal['Normal', 'Semi-Turbo', 'Turbo', 'Super-Turbo', 'Hyper-Turbo', 'Ultra-Turbo']
    round_time: int

class Action(BaseModel):
    action_number : int
    player_id : Optional[int] = None
    action: ACTIONS
    amount: Optional[Decimal] = None
    is_allin: Optional[bool] = None
    cards: Optional[List[CARDS]] = None

class TournamentInfo(BaseModel):
    tournament_number: str
    name: str
    start_date_utc: datetime
    currency: Literal['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'PPC', 'XSC']
    buyin_amount: Optional[Decimal] = None
    fee_amount: Optional[Decimal] = None
    bounty_fee_amount: Optional[Decimal] = None
    initial_stack: int
    type: Literal['STT', 'MTT']
    flags: Optional[List[Literal[
        "SNG",
        "DON",
        "Bounty",
        "Shootout",
        "Rebuy",
        "Matrix",
        "Push_Or_Fold",
        "Satellite",
        "Steps",
        "Deep",
        "Multi-Entry",
        "Fifty50",
        "Flipout",
        "TripleUp",
        "Lottery",
        "Re-Entry",
        "Power_Up",
        "Progressive-Bounty"
    ]]] = None
    speed: Speed

class BetLimit(BaseModel):
    bet_type: Literal['NL', 'PL', 'FL']
    bet_cap: Optional[Decimal] = None
    action: Literal['Dealt Cards', 'PotLimit', 'FixedLimit']

class Player(BaseModel):
    id: int 
    seat: int
    name: str
    display: Optional[str] = None
    starting_stack: Decimal
    player_bounty: Optional[Decimal] = None
    is_sitting_out: Optional[bool] = None

class Round(BaseModel):
    id: int
    street: Literal['Preflop', 'Flop', 'Turn', 'River', 'Showdown']
    cards: Optional[List[CARDS]] = None
    actions: List[Action]

class PlayerWin(BaseModel):
    player_id: int
    win_amount: Decimal
    cashout_amount: Optional[Decimal] = None
    cashout_fee: Optional[Decimal] = None
    bonus_amount: Optional[Decimal] = None
    contributed_rake: Optional[Decimal] = None

class Pot(BaseModel):
    number: int
    amount: Decimal
    rake: Optional[Decimal] = None
    jackpot: Optional[Decimal] = None
    player_wins: Optional[List[PlayerWin]] = None

class TournamentBounty(BaseModel):
    # Define fields as per your tournament_bounty_obj spec
    pass

class OpenHandHistory(BaseModel):
    spec_version: str = "1.4.6"
    site_name: str
    network_name: str
    internal_version: str
    tournament: Optional[bool] = None
    tournament_info: Optional[TournamentInfo] = None
    game_number: str
    start_date_utc: datetime
    table_name: str
    table_handle: Optional[str] = None
    table_skin: Optional[str] = None
    game_type: Literal['Holdem', 'Omaha', 'OmahaHiLo', 'Stud', 'StudHiLo', 'Draw']
    bet_limit: BetLimit
    table_size: int
    currency: str
    dealer_seat: int
    small_blind_amount: Decimal
    big_blind_amount: Decimal
    ante_amount: Optional[Decimal] = None
    hero_player_id: Optional[int] = None
    flags: Optional[List[Literal['Run_It_Twice', 'Anonymous', 'Observed', 'Fast', 'Cap']]] = None
    players: List[Player]
    rounds: List[Round]
    pots: List[Pot]
    tournament_bounties: Optional[List[TournamentBounty]] = None


class IgnitionHandHistory(OpenHandHistory):
    version: str = "1.4.7"
    site_name: str = "ignition"
    network_name: str = "bovada"
    internal_version: str = "0.1.0"
    currency: str = "USD"
    tournament: bool = False
    game_type: str = "holdem"
    bet_limit: str = "NL"
