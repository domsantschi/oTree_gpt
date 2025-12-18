from otree.api import *
import random

doc = """
Infinitely Repeated Prisoner's Dilemma with random termination.
Pairs stay matched throughout all rounds. Each round has a 90% chance of continuing.
"""


class C(BaseConstants):
    NAME_IN_URL = 'prisoner'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 100  # Maximum possible rounds

    # Payoff if 1 player defects and the other cooperates
    BETRAY_PAYOFF = 50
    BETRAYED_PAYOFF = 12

    # Payoff if both players cooperate or both defect
    BOTH_COOPERATE_PAYOFF = 32
    BOTH_DEFECT_PAYOFF = 25

    # Probability of continuing to next round (90%)
    CONTINUATION_PROBABILITY = 0.9


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    game_continues = models.BooleanField(initial=True)


class Player(BasePlayer):
    decision = models.StringField(
        choices=['Action 1', 'Action 2'],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    round_payoff = models.IntegerField(initial=0)
    total_payoff = models.IntegerField(initial=0)

    # Comprehension checks
    comp_check_payoff = models.BooleanField(
        label="True or False: If I choose Action 1 and the other participant chooses Action 2, I will receive 50 points.",
        widget=widgets.RadioSelect,
        choices=[[True, 'True'], [False, 'False']]
    )
    comp_check_goal = models.BooleanField(
        label="True or False: The game will continue for exactly 10 rounds.",
        widget=widgets.RadioSelect,
        choices=[[True, 'True'], [False, 'False']]
    )

    # Manipulation Check
    manip_check_strategy = models.LongStringField(
        label="What strategy did you use during the game? Please describe your approach.",
        blank=False
    )
    manip_check_opponent = models.LongStringField(
        label="What do you think was your opponent's strategy?",
        blank=False
    )
    manip_check_fairness = models.IntegerField(
        label="How fair did you perceive the game to be?",
        choices=[[1, '1 - Very unfair'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Very fair']],
        widget=widgets.RadioSelectHorizontal
    )

    # Mediators
    trust = models.IntegerField(
        label="To what extent did you trust your opponent?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal
    )
    cooperation_intent = models.IntegerField(
        label="To what extent did you intend to cooperate with your opponent?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal
    )
    expected_cooperation = models.IntegerField(
        label="To what extent did you expect your opponent to cooperate?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal
    )

    # Control Variables
    risk_attitude = models.IntegerField(
        label="How willing are you to take risks in general?",
        choices=[[0, '0 - Not at all willing'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'], [10, '10 - Very willing']],
        widget=widgets.RadioSelectHorizontal
    )
    game_experience = models.IntegerField(
        label="Have you played similar decision-making games before?",
        choices=[[1, 'Never'], [2, 'Once or twice'], [3, 'A few times'], [4, 'Many times']],
        widget=widgets.RadioSelect
    )
    attention_check = models.IntegerField(
        label="To ensure you are paying attention, please select '4' for this question.",
        choices=[[1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5']],
        widget=widgets.RadioSelectHorizontal
    )

    # Demographics
    age = models.IntegerField(label="What is your age?", min=18, max=100)
    gender = models.StringField(
        label="What is your gender?",
        choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'],
        widget=widgets.RadioSelect
    )
    education = models.StringField(
        label="What is the highest level of education you have completed?",
        choices=[
            'Less than high school',
            'High school diploma or equivalent',
            'Some college',
            'Bachelor\'s degree',
            'Master\'s degree',
            'Doctoral degree or higher'
        ],
        widget=widgets.RadioSelect
    )
    feedback = models.LongStringField(
        label="Do you have any comments or feedback about this study? (optional)",
        blank=True
    )

    def other_player(self):
        return self.get_others_in_group()[0]


# FUNCTIONS
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()
    else:
        subsession.group_like_round(1)


def set_payoffs(group: Group):
    for p in group.get_players():
        other = p.other_player()
        payoff_matrix = {
            'Action 1': {
                'Action 1': C.BOTH_COOPERATE_PAYOFF,
                'Action 2': C.BETRAYED_PAYOFF
            },
            'Action 2': {
                'Action 1': C.BETRAY_PAYOFF,
                'Action 2': C.BOTH_DEFECT_PAYOFF
            }
        }
        p.round_payoff = payoff_matrix[p.decision][other.decision]
        p.total_payoff = sum([player.round_payoff for player in p.in_all_rounds()])

    # Determine if game continues (random termination)
    if group.round_number < C.NUM_ROUNDS:
        group.game_continues = random.random() < C.CONTINUATION_PROBABILITY
    else:
        group.game_continues = False


def game_finished(player: Player):
    """Check if the game has ended in a previous round"""
    if player.round_number == 1:
        return False
    prev_group = player.in_round(player.round_number - 1).group
    return not prev_group.game_continues


def is_final_round(player: Player):
    """Check if this is the round where game just ended (for showing questionnaire)"""
    if player.round_number == 1:
        return False
    prev_group = player.in_round(player.round_number - 1).group
    return not prev_group.game_continues


# PAGES
class Instructions1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions2(Page):
    form_model = 'player'
    form_fields = ['comp_check_payoff']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        if values['comp_check_payoff'] != False:
            return 'Incorrect. If you choose Action 1 and the other participant chooses Action 2, you receive 12 points (you are betrayed), not 50 points. Please review the payoff table.'


class Instructions3(Page):
    form_model = 'player'
    form_fields = ['comp_check_goal']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        if values['comp_check_goal'] != False:
            return 'Incorrect. The number of rounds is not fixed. Each round has a 90% chance to continue and a 10% chance to end, so the total number of rounds is uncertain. Please review the instructions.'


class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']

    @staticmethod
    def is_displayed(player: Player):
        return not game_finished(player)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player: Player):
        return not game_finished(player)


class RoundResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return not game_finished(player)

    @staticmethod
    def vars_for_template(player: Player):
        opponent = player.other_player()
        return {
            'my_decision': player.decision,
            'opponent_decision': opponent.decision,
            'round_payoff': player.round_payoff,
            'total_payoff': player.total_payoff,
            'round_number': player.round_number,
            'continue_game': player.group.game_continues,
            'game_ends': not player.group.game_continues,
            'same_choice': player.decision == opponent.decision,
            'both_cooperate': player.decision == "Action 1" and opponent.decision == "Action 1",
            'both_defect': player.decision == "Action 2" and opponent.decision == "Action 2",
            'i_cooperate_he_defects': player.decision == "Action 1" and opponent.decision == "Action 2",
            'i_defect_he_cooperates': player.decision == "Action 2" and opponent.decision == "Action 1",
        }


class ManipCheck(Page):
    form_model = 'player'
    form_fields = ['manip_check_strategy', 'manip_check_opponent', 'manip_check_fairness']

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)


class Mediators(Page):
    form_model = 'player'
    form_fields = ['trust', 'cooperation_intent', 'expected_cooperation']

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)


class Controls(Page):
    form_model = 'player'
    form_fields = ['risk_attitude', 'game_experience', 'attention_check']

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'feedback']

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)


class Thanks(Page):
    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)

    @staticmethod
    def vars_for_template(player: Player):
        # Get total payoff from all played rounds
        all_rounds = player.in_all_rounds()
        final_payoff = 0
        total_rounds_played = 0
        for p in all_rounds:
            # Only count rounds where a decision was actually made
            if p.field_maybe_none('decision') is not None:
                final_payoff += p.round_payoff
                total_rounds_played += 1
        return {
            'final_payoff': final_payoff,
            'total_rounds_played': total_rounds_played
        }


page_sequence = [
    Instructions1,
    Instructions2,
    Instructions3,
    Decision,
    ResultsWaitPage,
    RoundResults,
    ManipCheck,
    Mediators,
    Controls,
    Demographics,
    Thanks,
]
