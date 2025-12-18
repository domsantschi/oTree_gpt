from otree.api import *
import random
import time

doc = """
Budget Negotiation Experiment: Civil servants and politicians negotiate budget allocations
for alternating expense and revenue accounts. The game continues until a 5-minute timer expires.
"""


class C(BaseConstants):
    NAME_IN_URL = 'budgeting'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 50  # Maximum possible rounds

    # Game duration
    GAME_DURATION_MINUTES = 5
    GAME_DURATION_SECONDS = GAME_DURATION_MINUTES * 60

    # Slider adjustment range (percentage above/below forecast)
    SLIDER_RANGE_PERCENT = 50  # Players can adjust +/- 50% from forecast
    
    # Budget categories with forecasts from specialized civil servant (in CHF thousands)
    # 'forecast' is the best estimate from the specialized civil servant
    # Historical data patterns:
    # - Round 1 (education): positive linear trend
    # - Round 2 (property_taxes): negative linear trend
    # - Round 3+ (other accounts): increasing variability
    EXPENSE_ACCOUNTS = {
        'education': {'forecast': 252, 'historical': [232, 237, 242, 247, 252]},  # Round 1: positive linear trend (+5/year)
        'healthcare': {'forecast': 203, 'historical': [210, 195, 220, 185, 203]},  # Round 3: high variability
        'infrastructure': {'forecast': 205, 'historical': [180, 225, 190, 230, 205]},  # Round 5: very high variability
        'public_safety': {'forecast': 153, 'historical': [165, 140, 170, 135, 153]},  # Round 7: high variability
        'social_services': {'forecast': 103, 'historical': [85, 120, 90, 115, 103]},  # Round 9: high variability
        'administration': {'forecast': 102, 'historical': [110, 88, 118, 85, 102]},  # Round 11: high variability
    }

    REVENUE_ACCOUNTS = {
        'property_taxes': {'forecast': 305, 'historical': [325, 320, 315, 310, 305]},  # Round 2: negative linear trend (-5/year)
        'sales_taxes': {'forecast': 253, 'historical': [270, 235, 275, 230, 253]},  # Round 4: high variability
        'grants_transfers': {'forecast': 152, 'historical': [130, 175, 125, 180, 152]},  # Round 6: very high variability
        'fees_licenses': {'forecast': 102, 'historical': [115, 85, 120, 80, 102]},  # Round 8: high variability
        'other_revenues': {'forecast': 100, 'historical': [75, 125, 70, 130, 100]},  # Round 10: very high variability
        'investment_income': {'forecast': 95, 'historical': [110, 75, 115, 70, 95]},  # Round 12: high variability
    }


class Subsession(BaseSubsession):
    # Store game start time in the first subsession (round 1)
    # All rounds reference round 1's start time
    game_start_time = models.FloatField(initial=0)
    game_end_time = models.FloatField(initial=0)


class Group(BaseGroup):
    current_account_type = models.StringField(initial='expense')  # 'expense' or 'revenue'
    current_account_name = models.StringField(initial='')
    round_start_time = models.FloatField(initial=0)
    round_end_time = models.FloatField(initial=0)
    agreed_amount = models.IntegerField(initial=0)
    forecast_amount = models.IntegerField(initial=0)  # Best estimate from specialized civil servant
    round_deviation = models.IntegerField(initial=0)  # Deviation from forecast for this round
    round_completed = models.BooleanField(initial=False)


class Player(BasePlayer):
    player_role = models.StringField(choices=['finance_director', 'politician'])

    # Consent
    declined_consent = models.BooleanField(initial=False)

    # Budget proposals
    proposed_amount = models.IntegerField(min=0, max=1000, initial=0)
    agreed = models.BooleanField(initial=False)
    proposal_submitted = models.BooleanField(initial=False)
    agreement_submitted = models.BooleanField(initial=False)
    alternate_amount = models.IntegerField(min=0, max=1000, initial=0, blank=True)

    # Round results
    round_score = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)

    # Comprehension checks
    comp_check_payoff = models.BooleanField(
        label="True or False: Better performance means having agreed amounts that are closer to the specialized civil servant's forecasts.",
        widget=widgets.RadioSelect,
        choices=[[True, 'True'], [False, 'False']]
    )
    comp_check_goal = models.BooleanField(
        label="True or False: The game will continue for exactly 5 minutes.",
        widget=widgets.RadioSelect,
        choices=[[True, 'True'], [False, 'False']]
    )

    # Questionnaire fields
    manip_check_strategy = models.LongStringField(
        label="What strategy did you use during the negotiations?",
        blank=False
    )
    manip_check_opponent = models.LongStringField(
        label="What do you think was your partner's strategy?",
        blank=False
    )
    manip_check_fairness = models.IntegerField(
        label="How fair did you perceive the negotiation process to be?",
        choices=[[1, '1 - Very unfair'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Very fair']],
        widget=widgets.RadioSelectHorizontal
    )

    trust = models.IntegerField(
        label="To what extent did you trust your partner?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal
    )
    cooperation_intent = models.IntegerField(
        label="To what extent did you intend to cooperate with your partner?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal
    )
    expected_cooperation = models.IntegerField(
        label="To what extent did you expect your partner to cooperate?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal
    )

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


# HELPER FUNCTIONS
def format_time_remaining(seconds: float) -> str:
    """Format seconds as 'X min YY sec'"""
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    secs = total_seconds % 60
    if minutes > 0:
        return f"{minutes} min {secs:02d} sec"
    else:
        return f"{secs} sec"


# FUNCTIONS
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()
        # Assign roles and persist them on the participant so they are available in later rounds
        for group in subsession.get_groups():
            players = group.get_players()
            players[0].player_role = 'finance_director'
            players[1].player_role = 'politician'
            players[0].participant.vars['role'] = 'finance_director'
            players[1].participant.vars['role'] = 'politician'
        # Timer will start after participants finish the instructions (set in Instructions3.before_next_page)
    else:
        subsession.group_like_round(1)
        # Restore player roles from participant.vars for non-first rounds
        for p in subsession.get_players():
            role = p.participant.vars.get('role')
            if role:
                p.player_role = role


def get_current_account(group: Group):
    """Determine which account to negotiate in this round"""
    round_num = group.round_number
    if round_num % 2 == 1:  # Odd rounds: expenses
        account_type = 'expense'
        accounts = list(C.EXPENSE_ACCOUNTS.keys())
    else:  # Even rounds: revenues
        account_type = 'revenue'
        accounts = list(C.REVENUE_ACCOUNTS.keys())

    # Cycle through accounts
    account_index = ((round_num - 1) // 2) % len(accounts)
    account_name = accounts[account_index]

    return account_type, account_name


def initialize_round(group: Group):
    """Set up the current round's account"""
    account_type, account_name = get_current_account(group)
    group.current_account_type = account_type
    group.current_account_name = account_name
    group.round_start_time = time.time()
    group.round_completed = False
    group.agreed_amount = 0
    group.round_deviation = 0
    
    # Get the forecast from the specialized civil servant
    if account_type == 'expense':
        group.forecast_amount = C.EXPENSE_ACCOUNTS[account_name]['forecast']
    else:
        group.forecast_amount = C.REVENUE_ACCOUNTS[account_name]['forecast']

    # Initialize player proposals and submission flags
    for player in group.get_players():
        player.proposed_amount = 0
        player.agreed = False
        player.proposal_submitted = False
        player.agreement_submitted = False
        player.alternate_amount = 0


def calculate_round_score(group: Group, player: Player):
    """Mark round as completed - no longer used for scoring"""
    if not group.round_completed:
        return 0
    
    # Return 1 to mark completion (used for counting completed rounds)
    return 1


def calculate_total_deviation(player: Player):
    """
    Calculate total deviation from forecasts across all completed rounds.
    Performance is measured by how close agreed amounts are to the specialized civil servant's forecasts.
    """
    total_deviation = 0
    rounds_completed = 0
    round_details = []  # List of (account_name, forecast, agreed, deviation) tuples
    
    for p in player.in_all_rounds():
        if p.group.round_completed and p.group.agreed_amount > 0:
            rounds_completed += 1
            deviation = abs(p.group.agreed_amount - p.group.forecast_amount)
            total_deviation += deviation
            round_details.append({
                'account': p.group.current_account_name.replace('_', ' ').title(),
                'account_type': p.group.current_account_type.title(),
                'forecast': p.group.forecast_amount,
                'agreed': p.group.agreed_amount,
                'deviation': deviation
            })
    
    # Calculate average deviation per round (if any rounds completed)
    avg_deviation = total_deviation / rounds_completed if rounds_completed > 0 else 0
    
    return total_deviation, avg_deviation, rounds_completed, round_details


def finalize_round(group: Group, resolved_amount: float):
    """Finalize round with resolved agreed amount and calculate deviation from forecast"""
    group.agreed_amount = int(round(resolved_amount))
    group.round_deviation = abs(group.agreed_amount - group.forecast_amount)
    group.round_end_time = time.time()
    group.round_completed = True
    for player in group.get_players():
        player.round_score = calculate_round_score(group, player)
        player.total_score += player.round_score
        # reset submission flags for next round (reinitialized by initialize_round)
        player.proposal_submitted = False
        player.agreement_submitted = False


def finalize_round_by_timeout(group: Group):
    """Finalize round when time expires using available proposals"""
    players = group.get_players()
    proposals = [p.proposed_amount for p in players if p.proposed_amount > 0]
    if proposals:
        resolved_amount = int(round(sum(proposals) / len(proposals)))
    else:
        resolved_amount = 0
    finalize_round(group, resolved_amount)


def get_game_start_time(player: Player):
    """Get the game start time from round 1's subsession"""
    # Get the round 1 subsession for this app specifically
    round_1_player = player.in_round(1)
    return round_1_player.subsession.game_start_time


def game_time_remaining(player: Player):
    """Check how much time remains in the 5-minute game window"""
    start_time = get_game_start_time(player)
    if start_time == 0:
        return C.GAME_DURATION_SECONDS

    elapsed = time.time() - start_time
    remaining = C.GAME_DURATION_SECONDS - elapsed
    return max(0, remaining)


def game_finished(player: Player):
    """Check if the game has ended"""
    return game_time_remaining(player) <= 0


def is_final_round(player: Player):
    """Check if this is the final round (game just ended)"""
    return game_finished(player)


# PAGES
class Consent(Page):
    template_name = 'budgeting/pages/Consent.html'
    form_model = 'player'
    form_fields = ['declined_consent']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class RoleAssignment(Page):
    template_name = 'budgeting/pages/RoleAssignment.html'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        role_raw = player.player_role or player.participant.vars.get('role', 'unassigned')
        role_display = role_raw.replace('_', ' ').title() if isinstance(role_raw, str) else 'Unassigned'
        role_descriptions = {
            'finance_director': 'You are a Finance Director. Your goal is to ensure stable, efficient budget allocations that align with operational needs.',
            'politician': 'You are a Politician. Your goal is to allocate budgets in ways that create visible impact and appeal to voters.'
        }
        
        # Determine the other player's role
        other_role_raw = 'politician' if role_raw == 'finance_director' else 'finance_director'
        other_role_display = other_role_raw.replace('_', ' ').title()
        
        # Format other role description from the perspective of the current player
        other_role_descriptions_formatted = {
            'finance_director': 'The other participant\'s goal as a Finance Director is to ensure stable, efficient budget allocations that align with operational needs.',
            'politician': 'The other participant\'s goal as a Politician is to allocate budgets in ways that create visible impact and appeal to voters.'
        }
        
        return {
            'role': role_display,
            'role_description': role_descriptions.get(role_raw, ''),
            'other_role': other_role_display,
            'other_role_description': other_role_descriptions_formatted.get(other_role_raw, '')
        }


class Instructions1(Page):
    template_name = 'budgeting/pages/Instructions1.html'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        role_raw = player.player_role or player.participant.vars.get('role', 'unassigned')
        return {
            'role': role_raw.replace('_', ' ').title() if isinstance(role_raw, str) else 'Unassigned'
        }


class Instructions2(Page):
    template_name = 'budgeting/pages/Instructions2.html'
    form_model = 'player'
    form_fields = ['comp_check_payoff']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        role_raw = player.player_role or player.participant.vars.get('role', 'unassigned')
        return {
            'role': role_raw.replace('_', ' ').title() if isinstance(role_raw, str) else 'Unassigned'
        }

    @staticmethod
    def error_message(player: Player, values):
        if values['comp_check_payoff'] != True:
            return 'Incorrect. Better performance means lower deviation from the specialized civil servant\'s forecasts. The closer your agreed amounts are to the forecasts, the better. Please review the performance metrics.'


class Instructions3(Page):
    template_name = 'budgeting/pages/Instructions3.html'
    form_model = 'player'
    form_fields = ['comp_check_goal']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        if values['comp_check_goal'] != True:
            return 'Incorrect. The game lasts exactly 5 minutes. You will complete as many budget negotiation rounds as possible within this time limit. Please review the instructions.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass


class StartGame(WaitPage):
    """Wait for both players to be ready before starting Round 1 and the timer"""
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        # Start the overall game timer when both players are ready for Round 1
        # Store it on round 1's subsession so it persists across all rounds
        round_1_subsession = group.subsession
        round_1_subsession.game_start_time = time.time()
        # Initialize round for all groups
        for g in group.subsession.get_groups():
            initialize_round(g)


class BudgetNegotiation(Page):
    """Proposal submission page. Players submit their proposal first."""
    template_name = 'budgeting/pages/BudgetNegotiation.html'
    form_model = 'player'
    form_fields = ['proposed_amount']

    @staticmethod
    def get_timeout_seconds(player: Player):
        return game_time_remaining(player)

    @staticmethod
    def is_displayed(player: Player):
        return not game_finished(player)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        account_type, account_name = get_current_account(group)

        if account_type == 'expense':
            account_data = C.EXPENSE_ACCOUNTS[account_name]
            account_title = account_name.replace('_', ' ').title()
        else:
            account_data = C.REVENUE_ACCOUNTS[account_name]
            account_title = account_name.replace('_', ' ').title()

        time_remaining = game_time_remaining(player)

        role_raw = player.player_role or player.participant.vars.get('role', 'unassigned')
        role_display = role_raw.replace('_', ' ').title() if isinstance(role_raw, str) else 'Unassigned'
        
        # Calculate slider min/max based on forecast and allowed range
        forecast = account_data['forecast']
        slider_min = max(0, int(forecast * (1 - C.SLIDER_RANGE_PERCENT / 100)))
        slider_max = min(1000, int(forecast * (1 + C.SLIDER_RANGE_PERCENT / 100)))

        # Format historical data in full numbers with commas
        historical_formatted = ["{:,}".format(val * 1000) for val in account_data['historical']]
        
        return {
            'account_type': account_type,
            'formatted_account_type': account_type.title(),
            'account_name': account_name,
            'account_title': account_title,
            'forecast': forecast,
            'slider_min': slider_min,
            'slider_max': slider_max,
            'historical_data': account_data['historical'],
            'historical_formatted': historical_formatted,
            'time_remaining': format_time_remaining(time_remaining),
            'time_remaining_seconds': int(time_remaining),
            'round_number': player.round_number,
            'role': role_display,
            'partner_proposal': player.other_player().proposed_amount if player.other_player().proposed_amount > 0 else None,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Mark that the player submitted a proposal
        player.proposal_submitted = True
        
        # Set a default value if timed out without submission (use forecast as default)
        if timeout_happened and player.proposed_amount == 0:
            player.proposed_amount = player.group.forecast_amount

        # If game time expired, finalize based on available proposals
        if game_finished(player):
            finalize_round_by_timeout(player.group)


class WaitForProposals(WaitPage):
    """Wait for both players to submit proposals before proceeding to Agreement."""

    @staticmethod
    def after_all_players_arrive(group: Group):
        # Nothing to do yet; this simply synchronizes players before agreement
        pass


class Agreement(Page):
    """Decision page: after both submitted proposals, players indicate agreement or submit an alternate proposal."""
    template_name = 'budgeting/pages/Agreement.html'
    form_model = 'player'
    form_fields = ['agreed', 'alternate_amount']

    @staticmethod
    def get_timeout_seconds(player: Player):
        return game_time_remaining(player)

    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        # Show agreement page when game is active and round not completed
        # This allows looping back if players don't both agree
        return (not game_finished(player)) and not group.round_completed

    @staticmethod
    def vars_for_template(player: Player):
        time_remaining = game_time_remaining(player)
        group = player.group
        account_type, account_name = get_current_account(group)
        
        # Get role displays
        your_role = player.player_role or player.participant.vars.get('role', 'unassigned')
        partner_role = player.other_player().player_role or player.other_player().participant.vars.get('role', 'unassigned')
        your_role_display = your_role.replace('_', ' ').title() if isinstance(your_role, str) else 'Unassigned'
        partner_role_display = partner_role.replace('_', ' ').title() if isinstance(partner_role, str) else 'Unassigned'
        
        # Calculate lower budget
        lower_budget = min(player.proposed_amount, player.other_player().proposed_amount)
        
        # Calculate slider min/max for alternate proposals
        forecast = group.forecast_amount
        slider_min = max(0, int(forecast * (1 - C.SLIDER_RANGE_PERCENT / 100)))
        slider_max = min(1000, int(forecast * (1 + C.SLIDER_RANGE_PERCENT / 100)))
        
        # Calculate deviations from forecast for display
        your_deviation = player.proposed_amount - forecast
        partner_deviation = player.other_player().proposed_amount - forecast
        
        return {
            'partner_proposal': player.other_player().proposed_amount,
            'your_proposal': player.proposed_amount,
            'your_deviation': your_deviation,
            'partner_deviation': partner_deviation,
            'your_role': your_role_display,
            'partner_role': partner_role_display,
            'lower_budget': lower_budget,
            'forecast': forecast,
            'slider_min': slider_min,
            'slider_max': slider_max,
            'account_name': account_name,
            'account_title': account_name.replace('_', ' ').title(),
            'account_type': account_type,
            'formatted_account_type': account_type.title(),
            'time_remaining': format_time_remaining(time_remaining),
            'time_remaining_seconds': int(time_remaining),
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.agreement_submitted = True
        
        # If timed out, default to agreeing with lower budget
        if timeout_happened:
            player.agreed = True
            player.alternate_amount = 0

        # If game time expired, finalize based on available proposals
        if game_finished(player):
            finalize_round_by_timeout(player.group)


class WaitForAgreement(WaitPage):
    """Wait for both players to submit their agreement decision."""

    @staticmethod
    def is_displayed(player: Player):
        # Only show if game is not finished and round is not completed
        return not game_finished(player) and not player.group.round_completed

    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        
        # If game time is up, finalize with average of proposals
        if game_time_remaining(players[0]) <= 0:
            proposals = [p.proposed_amount for p in players if p.proposed_amount > 0]
            if proposals:
                resolved = int(round(sum(proposals) / len(proposals)))
            else:
                resolved = 0
            finalize_round(group, resolved)
            return
        
        # Check if both players agreed with the lower budget
        if all(p.agreed for p in players):
            # Both agreed - finalize the round with the lower budget
            amounts = [p.proposed_amount for p in players]
            resolved = min(amounts)
            finalize_round(group, resolved)
        else:
            # At least one player wants to resubmit
            # Update proposals with alternate amounts if provided
            for p in players:
                if not p.agreed and p.alternate_amount > 0:
                    p.proposed_amount = p.alternate_amount
                # Reset for next iteration
                p.agreement_submitted = False
                p.agreed = False
                p.alternate_amount = 0


class RoundResults(Page):
    template_name = 'budgeting/pages/RoundResults.html'

    @staticmethod
    def is_displayed(player: Player):
        return not game_finished(player) and player.group.round_completed

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Prepare next round if the game hasn't finished
        if not game_finished(player):
            initialize_round(player.group)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        account_type, account_name = get_current_account(group)
        time_remaining = game_time_remaining(player)
        
        # Calculate total deviation from forecasts
        total_deviation, avg_deviation, rounds_completed, round_details = calculate_total_deviation(player)
        
        # Format numbers with thousands separator
        agreed_formatted = "{:,}".format(group.agreed_amount * 1000)
        forecast_formatted = "{:,}".format(group.forecast_amount * 1000)
        round_deviation_formatted = "{:,}".format(group.round_deviation * 1000)
        total_deviation_formatted = "{:,}".format(total_deviation * 1000)
        avg_deviation_formatted = "{:,.0f}".format(avg_deviation * 1000) if rounds_completed > 0 else "0"

        return {
            'account_type': account_type,
            'account_title': account_name.replace('_', ' ').title(),
            'agreed_amount': group.agreed_amount,
            'agreed_formatted': agreed_formatted,
            'forecast_amount': group.forecast_amount,
            'forecast_formatted': forecast_formatted,
            'round_deviation': group.round_deviation,
            'round_deviation_formatted': round_deviation_formatted,
            'rounds_completed': rounds_completed,
            'total_deviation': total_deviation,
            'total_deviation_formatted': total_deviation_formatted,
            'avg_deviation': round(avg_deviation, 1),
            'avg_deviation_formatted': avg_deviation_formatted,
            'time_remaining': format_time_remaining(time_remaining),
            'time_remaining_seconds': int(time_remaining),
            'round_number': player.round_number,
        }


class GameOver(Page):
    template_name = 'budgeting/pages/GameOver.html'

    @staticmethod
    def is_displayed(player: Player):
        return game_finished(player)

    @staticmethod
    def vars_for_template(player: Player):
        # Calculate total deviation from forecasts
        total_deviation, avg_deviation, rounds_completed, round_details = calculate_total_deviation(player)
        
        # Format numbers with thousands separator
        total_deviation_formatted = "{:,}".format(total_deviation * 1000)
        avg_deviation_formatted = "{:,.1f}".format(avg_deviation * 1000) if rounds_completed > 0 else "0"
        
        # Calculate final score (total deviation / rounds completed)
        final_score = (total_deviation / rounds_completed) if rounds_completed > 0 else 0
        final_score_formatted = "{:,.0f}".format(final_score * 1000)

        return {
            'rounds_completed': rounds_completed,
            'total_deviation': total_deviation,
            'total_deviation_formatted': total_deviation_formatted,
            'avg_deviation': round(avg_deviation, 1),
            'avg_deviation_formatted': avg_deviation_formatted,
            'final_score': final_score,
            'final_score_formatted': final_score_formatted,
            'round_details': round_details,
        }


class ManipCheck(Page):
    template_name = 'budgeting/pages/ManipCheck.html'
    form_model = 'player'
    form_fields = ['manip_check_strategy', 'manip_check_opponent', 'manip_check_fairness']

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)


class Mediators(Page):
    template_name = 'budgeting/pages/Mediators.html'
    form_model = 'player'
    form_fields = ['trust', 'cooperation_intent', 'expected_cooperation']

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)


class Controls(Page):
    template_name = 'budgeting/pages/Controls.html'
    form_model = 'player'
    form_fields = ['risk_attitude', 'game_experience', 'attention_check']

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)


class Demographics(Page):
    template_name = 'budgeting/pages/Demographics.html'
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'feedback']

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)


class Thanks(Page):
    template_name = 'budgeting/pages/Thanks.html'

    @staticmethod
    def is_displayed(player: Player):
        return is_final_round(player)

    @staticmethod
    def vars_for_template(player: Player):
        total_deviation, avg_deviation, rounds_completed, round_details = calculate_total_deviation(player)
        total_deviation_formatted = "{:,}".format(total_deviation * 1000)

        return {
            'rounds_completed': rounds_completed,
            'total_deviation_formatted': total_deviation_formatted,
        }


page_sequence = [
    Consent,
    RoleAssignment,
    Instructions1,
    Instructions2,
    Instructions3,
    StartGame,
    BudgetNegotiation,
    WaitForProposals,
    # Multiple Agreement iterations to allow back-and-forth negotiation
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    Agreement, WaitForAgreement,
    RoundResults,
    GameOver,
    ManipCheck,
    Mediators,
    Controls,
    Demographics,
    Thanks,
]
