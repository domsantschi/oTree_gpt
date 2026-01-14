from otree.api import *
import random
import time

doc = """
Multi-Round Budget Forecasting Experiment:
Participants complete 3 rounds of budget forecasting for different public expense categories:
Education, Infrastructure, and Security. Each round includes:
1. Best estimate + buffer + justification
2. Advice from Human Expert or AI Model
3. Decision to keep or revise submission
4. Revelation of actual expenses and accuracy comparison
"""


class C(BaseConstants):
    NAME_IN_URL = 'budgeting'
    PLAYERS_PER_GROUP = None  # Single player
    NUM_ROUNDS = 3

    # Slider adjustment range (percentage above/below forecast)
    SLIDER_RANGE_PERCENT = 50

    # Define the three expense categories with their data
    CATEGORIES = {
        1: {
            'name': 'Education',
            'icon': '📚',
            'description': 'Public education spending including schools, universities, and educational programs',
            'historical_budget': [85, 88, 90, 92, 95, 98, 100, 103, 106, 110],
            'historical_actual': [92, 95, 99, 104, 108, 115, 120, 128, 135, 145],
            'last_year_actual': 145,  # Y-1 actual (most recent completed year)
            'target_year_actual': 155,  # The "true" actual for the forecasting year (Y)
            'recommended_estimate': 150,
            'recommended_buffer': 8,
            'trend_description': 'Education expenses have consistently exceeded budgeted amounts by an average of 15-20% over the past decade, driven by growing enrollment and infrastructure needs.'
        },
        2: {
            'name': 'Infrastructure',
            'icon': '🏗️',
            'description': 'Public infrastructure spending including roads, bridges, utilities, and maintenance',
            'historical_budget': [120, 125, 128, 132, 138, 142, 148, 155, 160, 168],
            'historical_actual': [118, 122, 130, 128, 145, 138, 155, 148, 172, 165],
            'last_year_actual': 165,  # Y-1 actual (most recent completed year)
            'target_year_actual': 175,  # The "true" actual for the forecasting year (Y)
            'recommended_estimate': 170,
            'recommended_buffer': 10,
            'trend_description': 'Infrastructure spending shows high volatility, with actual expenses sometimes exceeding and sometimes falling below budget depending on project timelines and emergency repairs.'
        },
        3: {
            'name': 'Security',
            'icon': '🛡️',
            'description': 'Public security spending including police, emergency services, and public safety programs',
            'historical_budget': [60, 62, 64, 66, 68, 70, 72, 75, 78, 82],
            'historical_actual': [58, 60, 62, 65, 67, 71, 74, 78, 82, 88],
            'last_year_actual': 88,  # Y-1 actual (most recent completed year)
            'target_year_actual': 92,  # The "true" actual for the forecasting year (Y)
            'recommended_estimate': 90,
            'recommended_buffer': 5,
            'trend_description': 'Security expenses have shown steady growth slightly above budgeted amounts, with an average overrun of 5-8% due to increasing operational costs.'
        }
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # ===== Consent =====
    declined_consent = models.BooleanField(initial=False)

    # ===== Conditions (IVs) =====
    role_condition = models.StringField(
        choices=['politician', 'finance_director'],
        doc="IV1: Role assigned to participant"
    )
    advice_condition = models.StringField(
        choices=['human_expert', 'ai_model'],
        doc="IV2: Source of advice shown to participant"
    )

    # ===== Round-specific fields =====
    category_name = models.StringField(doc="Name of the expense category for this round")
    
    # Initial Forecast
    initial_forecast = models.IntegerField(
        min=0,
        max=1000,
        label="Your best estimate (CHF thousands)"
    )
    budget_adjustment = models.IntegerField(
        label="Buffer for uncertainty (CHF thousands)",
        doc="Buffer to add to best estimate"
    )
    initial_justification = models.LongStringField(
        label="Please justify your budget decision:",
        blank=False
    )
    comprehension_check = models.IntegerField(
        label="What were the actual expenses in the most recent year (Y-1)? (in CHF thousands)",
        doc="Control question to verify participant read the data"
    )

    # Resubmission Decision
    resubmit_decision = models.BooleanField(
        label="Based on the advice, do you want to revise your budget submission?",
        choices=[[True, 'Yes, I want to revise my submission'], [False, 'No, I will keep my original submission']],
        widget=widgets.RadioSelect
    )
    revised_forecast = models.IntegerField(
        min=0,
        max=1000,
        label="Your revised forecast (CHF thousands)",
        blank=True
    )
    revised_adjustment = models.IntegerField(
        label="Your revised buffer (CHF thousands)",
        blank=True
    )
    resubmission_justification = models.LongStringField(
        label="Please explain your decision:",
        blank=False
    )

    # Accuracy results (stored after reveal)
    actual_expense = models.IntegerField(doc="Actual expense for the target year", blank=True)
    initial_accuracy = models.FloatField(doc="Accuracy of initial estimate (absolute % deviation)", blank=True)
    final_accuracy = models.FloatField(doc="Accuracy of final estimate (absolute % deviation)", blank=True)
    advisor_accuracy = models.FloatField(doc="Accuracy of advisor recommendation (absolute % deviation)", blank=True)

    # ===== Manipulation Checks (only in final round) =====
    manip_check_role = models.StringField(
        label="Which <b>role were you assigned</b> at the beginning of the study?",
        choices=[
            ['politician', 'Politician'],
            ['finance_director', 'Finance Director']
        ],
        widget=widgets.RadioSelect
    )
    manip_check_advice = models.StringField(
        label="Who <b>provided the budget advice</b> you received?",
        choices=[
            ['human_expert', 'A civil servant specialized in each budget category'],
            ['ai_model', 'An AI model specialized in each budget category']
        ],
        widget=widgets.RadioSelect
    )

    # ===== Impartiality Mediators (only in final round) =====
    impartiality_unbiased = models.IntegerField(
        label="The advice I received was unbiased.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    impartiality_objective = models.IntegerField(
        label="The advice I received was objective.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    impartiality_fair = models.IntegerField(
        label="The advice I received was fair and balanced.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )

    # ===== Controls (only in final round) =====
    party_sympathy = models.StringField(
        label="Which Swiss political party do you most sympathize with?",
        choices=[
            'Grüne', 'SP', 'GLP', 'EVP', 'Mitte', 'FDP', 'SVP', 'Andere'
        ],
        widget=widgets.RadioSelect
    )
    party_other = models.StringField(
        label="If you selected 'Andere', please specify:",
        blank=True
    )
    trust_in_government = models.IntegerField(
        label="How much do you trust the Swiss government?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal
    )
    trust_in_ai = models.IntegerField(
        label="How much do you trust AI systems to provide accurate advice?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal
    )
    risk_attitude = models.IntegerField(
        label="How willing are you to take risks in general?",
        choices=[[0, '0 - Not at all willing'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'], [10, '10 - Very willing']],
        widget=widgets.RadioSelectHorizontal
    )
    attention_check = models.IntegerField(
        label="If you are reading this carefully, please select 'Neutral'.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )

    # ===== Demographics (only in final round) =====
    age = models.IntegerField(
        label="What is your age?",
        min=18,
        max=100
    )
    gender = models.StringField(
        label="What is your gender?",
        choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'],
        widget=widgets.RadioSelect
    )
    work_experience = models.IntegerField(
        label="How many years of work experience do you have?",
        min=0,
        max=60
    )
    politics_experience = models.IntegerField(
        label="How many years of experience in politics or public administration do you have?",
        min=0,
        max=60
    )
    budgeting_experience = models.IntegerField(
        label="How many years of experience with budgeting or financial planning do you have?",
        min=0,
        max=60
    )
    
    # Feedback (only in final round)
    feedback = models.LongStringField(
        label="Do you have any comments or feedback about this study? (optional)",
        blank=True
    )

    # Page timing
    forecast_page_time = models.FloatField(blank=True)
    advice_page_time = models.FloatField(blank=True)
    resubmission_page_time = models.FloatField(blank=True)
    results_page_time = models.FloatField(blank=True)

    # ===== Round 1 Resubmission (stored on round 3 player) =====
    resubmit_decision_r1 = models.BooleanField(
        label="Do you want to revise your Education budget?",
        choices=[[True, 'Yes, revise'], [False, 'No, keep original']],
        widget=widgets.RadioSelect
    )
    revised_forecast_r1 = models.IntegerField(min=0, max=1000, blank=True)
    revised_adjustment_r1 = models.IntegerField(blank=True)
    resubmission_justification_r1 = models.LongStringField(
        label="Explain your decision for Education:"
    )

    # ===== Round 2 Resubmission (stored on round 3 player) =====
    resubmit_decision_r2 = models.BooleanField(
        label="Do you want to revise your Infrastructure budget?",
        choices=[[True, 'Yes, revise'], [False, 'No, keep original']],
        widget=widgets.RadioSelect
    )
    revised_forecast_r2 = models.IntegerField(min=0, max=1000, blank=True)
    revised_adjustment_r2 = models.IntegerField(blank=True)
    resubmission_justification_r2 = models.LongStringField(
        label="Explain your decision for Infrastructure:"
    )

    # ===== Round 3 Resubmission (uses existing fields) =====
    resubmit_decision_r3 = models.BooleanField(
        label="Do you want to revise your Security budget?",
        choices=[[True, 'Yes, revise'], [False, 'No, keep original']],
        widget=widgets.RadioSelect
    )
    revised_forecast_r3 = models.IntegerField(min=0, max=1000, blank=True)
    revised_adjustment_r3 = models.IntegerField(blank=True)
    resubmission_justification_r3 = models.LongStringField(
        label="Explain your decision for Security:"
    )


# ===== FUNCTIONS =====

def creating_session(subsession: Subsession):
    """Randomly assign conditions to each player (only in round 1)"""
    if subsession.round_number == 1:
        for player in subsession.get_players():
            # IV1: Role condition
            player.role_condition = random.choice(['politician', 'finance_director'])
            # IV2: Advice source condition
            player.advice_condition = random.choice(['human_expert', 'ai_model'])
            
            # Store in participant vars for access across rounds
            player.participant.vars['role_condition'] = player.role_condition
            player.participant.vars['advice_condition'] = player.advice_condition
    else:
        # Copy conditions from participant vars
        for player in subsession.get_players():
            player.role_condition = player.participant.vars.get('role_condition')
            player.advice_condition = player.participant.vars.get('advice_condition')
    
    # Set category name for each player in this round
    for player in subsession.get_players():
        category = C.CATEGORIES[subsession.round_number]
        player.category_name = category['name']


def get_category_data(round_number):
    """Get the category data for a specific round"""
    return C.CATEGORIES[round_number]


def calculate_accuracy(estimate, actual):
    """Calculate accuracy as absolute percentage deviation"""
    if actual == 0:
        return 0
    return round(abs((estimate - actual) / actual) * 100, 2)


# ===== PAGES =====

class Consent(Page):
    template_name = 'budgeting/pages/Consent.html'
    form_model = 'player'
    form_fields = ['declined_consent']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions(Page):
    template_name = 'budgeting/pages/Instructions.html'
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'num_rounds': C.NUM_ROUNDS,
            'categories': [C.CATEGORIES[i]['name'] for i in range(1, C.NUM_ROUNDS + 1)],
        }


class RoleAssignment(Page):
    template_name = 'budgeting/pages/RoleAssignment.html'
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        role = player.role_condition
        role_display = role.replace('_', ' ').title()

        role_descriptions = {
            'finance_director': """
                <p>As a <strong>Finance Director</strong>, your responsibility is to ensure stable, efficient budget 
                allocations that align with operational needs and fiscal prudence.</p>
                <p>You are expected to:</p>
                <ul>
                    <li>Prioritize accuracy in forecasting</li>
                    <li>Maintain budget discipline</li>
                    <li>Ensure resources are allocated efficiently</li>
                    <li>Balance risk management with cost-effectiveness</li>
                </ul>
            """,
            'politician': """
                <p>As a <strong>Politician</strong>, your responsibility is to allocate budgets in ways that 
                serve the public interest and address citizen needs.</p>
                <p>You are expected to:</p>
                <ul>
                    <li>Consider the impact on public services</li>
                    <li>Balance various stakeholder interests</li>
                    <li>Ensure adequate funding for essential services</li>
                    <li>Be accountable to voters for budget decisions</li>
                </ul>
            """
        }

        return {
            'role': role_display,
            'role_description': role_descriptions.get(role, ''),
        }


class RoundIntro(Page):
    template_name = 'budgeting/pages/RoundIntro.html'

    @staticmethod
    def vars_for_template(player: Player):
        category = get_category_data(player.round_number)
        progress_percentage = round((player.round_number / C.NUM_ROUNDS) * 100)
        return {
            'round_number': player.round_number,
            'total_rounds': C.NUM_ROUNDS,
            'category_name': category['name'],
            'category_icon': category['icon'],
            'category_description': category['description'],
            'progress_percentage': progress_percentage,
        }


class InitialForecast(Page):
    template_name = 'budgeting/pages/InitialForecast.html'
    form_model = 'player'
    form_fields = ['comprehension_check', 'initial_forecast', 'budget_adjustment', 'initial_justification']

    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._forecast_start = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.forecast_page_time = time.time() - player.participant._forecast_start

    @staticmethod
    def error_message(player: Player, values):
        category = get_category_data(player.round_number)
        correct_answer = category['last_year_actual']
        if values.get('comprehension_check') != correct_answer:
            return f'Incorrect. Please check the historical data table and enter the actual expenses for Y-1.'

    @staticmethod
    def vars_for_template(player: Player):
        category = get_category_data(player.round_number)
        last_year_actual = category['last_year_actual']
        
        slider_min = max(0, int(last_year_actual * (1 - C.SLIDER_RANGE_PERCENT / 100)))
        slider_max = min(1000, int(last_year_actual * (1 + C.SLIDER_RANGE_PERCENT / 100)))
        adjustment_min = 0
        adjustment_max = int(last_year_actual * 1.0)

        role = player.role_condition.replace('_', ' ').title()

        return {
            'round_number': player.round_number,
            'total_rounds': C.NUM_ROUNDS,
            'category_name': category['name'],
            'category_icon': category['icon'],
            'last_year_actual': last_year_actual,
            'historical_budget': category['historical_budget'],
            'historical_actual': category['historical_actual'],
            'trend_description': category['trend_description'],
            'slider_min': slider_min,
            'slider_max': slider_max,
            'adjustment_min': adjustment_min,
            'adjustment_max': adjustment_max,
            'role': role,
        }


class AdviceFeedback(Page):
    template_name = 'budgeting/pages/AdviceFeedback.html'

    @staticmethod
    def is_displayed(player: Player):
        # Only show after all 3 forecasts are submitted (in round 3)
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._advice_start = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.advice_page_time = time.time() - player.participant._advice_start

    @staticmethod
    def vars_for_template(player: Player):
        def format_diff(diff):
            if diff >= 0:
                return f"+CHF {diff:,},000"
            else:
                return f"CHF {diff:,},000"

        # Gather data for all 3 rounds
        all_rounds_data = []
        for round_num in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(round_num)
            category = get_category_data(round_num)
            
            final_budget = p.initial_forecast + p.budget_adjustment
            recommended_estimate = category['recommended_estimate']
            recommended_buffer = category['recommended_buffer']
            recommended_budget = recommended_estimate + recommended_buffer
            buffer_percent = round((recommended_buffer / recommended_estimate) * 100, 1)
            
            estimate_diff = p.initial_forecast - recommended_estimate
            buffer_diff = p.budget_adjustment - recommended_buffer
            budget_diff = final_budget - recommended_budget
            
            advice_text = f"""
            <p><strong>Recommended Best Estimate:</strong> CHF {recommended_estimate:,},000</p>
            <p><strong>Recommended Buffer:</strong> CHF {recommended_buffer:,},000 ({buffer_percent}%)</p>
            <p><strong>Recommended Budget:</strong> CHF {recommended_budget:,},000</p>
            
            <p><strong>Rationale:</strong></p>
            <ul>
                <li><strong>Historical trend analysis:</strong> {category['trend_description']}</li>
                <li><strong>Estimate justification:</strong> Based on historical patterns and current economic indicators, 
                a best estimate of CHF {recommended_estimate:,},000 reflects the expected {category['name'].lower()} expenses 
                for the upcoming year.</li>
                <li><strong>Buffer rationale:</strong> A buffer of CHF {recommended_buffer:,},000 ({buffer_percent}%) 
                accounts for potential variations and uncertainties while maintaining fiscal prudence.</li>
            </ul>
            """
            
            all_rounds_data.append({
                'round_number': round_num,
                'category_name': category['name'],
                'category_name_lower': category['name'].lower(),
                'category_icon': category['icon'],
                'initial_forecast': p.initial_forecast,
                'budget_adjustment': p.budget_adjustment,
                'final_budget': final_budget,
                'recommended_estimate': recommended_estimate,
                'recommended_buffer': recommended_buffer,
                'recommended_budget': recommended_budget,
                'estimate_diff_display': format_diff(estimate_diff),
                'buffer_diff_display': format_diff(buffer_diff),
                'budget_diff_display': format_diff(budget_diff),
                'advice_text': advice_text,
            })

        # Advisor name based on condition
        if player.advice_condition == 'human_expert':
            advisor_name = "Civil Servant Budget Specialists"
        else:
            advisor_name = "AI Budget Forecasting Models"

        return {
            'total_rounds': C.NUM_ROUNDS,
            'advice_condition': player.advice_condition,
            'advisor_name': advisor_name,
            'all_rounds_data': all_rounds_data,
        }


class ResubmissionDecision(Page):
    template_name = 'budgeting/pages/ResubmissionDecision.html'
    form_model = 'player'
    form_fields = [
        'resubmit_decision_r1', 'revised_forecast_r1', 'revised_adjustment_r1', 'resubmission_justification_r1',
        'resubmit_decision_r2', 'revised_forecast_r2', 'revised_adjustment_r2', 'resubmission_justification_r2',
        'resubmit_decision_r3', 'revised_forecast_r3', 'revised_adjustment_r3', 'resubmission_justification_r3',
    ]

    @staticmethod
    def is_displayed(player: Player):
        # Only show after all 3 forecasts are submitted (in round 3)
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._resubmission_start = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.resubmission_page_time = time.time() - player.participant._resubmission_start
        
        # Copy revision data to the appropriate round players for data consistency
        # Round 1
        p1 = player.in_round(1)
        p1.resubmit_decision = player.resubmit_decision_r1 or False
        if player.resubmit_decision_r1:
            p1.revised_forecast = player.revised_forecast_r1
            p1.revised_adjustment = player.revised_adjustment_r1
        p1.resubmission_justification = player.resubmission_justification_r1 or ''
        
        # Round 2
        p2 = player.in_round(2)
        p2.resubmit_decision = player.resubmit_decision_r2 or False
        if player.resubmit_decision_r2:
            p2.revised_forecast = player.revised_forecast_r2
            p2.revised_adjustment = player.revised_adjustment_r2
        p2.resubmission_justification = player.resubmission_justification_r2 or ''
        
        # Round 3 (current player)
        player.resubmit_decision = player.resubmit_decision_r3 or False
        if player.resubmit_decision_r3:
            player.revised_forecast = player.revised_forecast_r3
            player.revised_adjustment = player.revised_adjustment_r3
        player.resubmission_justification = player.resubmission_justification_r3 or ''

    @staticmethod
    def vars_for_template(player: Player):
        def format_diff(diff):
            if diff >= 0:
                return f"+CHF {diff:,},000"
            else:
                return f"CHF {diff:,},000"

        # Gather data for all 3 rounds
        all_rounds_data = []
        for round_num in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(round_num)
            category = get_category_data(round_num)
            last_year_actual = category['last_year_actual']
            
            slider_min = max(0, int(last_year_actual * (1 - C.SLIDER_RANGE_PERCENT / 100)))
            slider_max = min(1000, int(last_year_actual * (1 + C.SLIDER_RANGE_PERCENT / 100)))
            
            final_budget = p.initial_forecast + p.budget_adjustment
            recommended_estimate = category['recommended_estimate']
            recommended_buffer = category['recommended_buffer']
            recommended_budget = recommended_estimate + recommended_buffer
            
            estimate_diff = p.initial_forecast - recommended_estimate
            buffer_diff = p.budget_adjustment - recommended_buffer
            budget_diff = final_budget - recommended_budget
            
            all_rounds_data.append({
                'round_number': round_num,
                'category_name': category['name'],
                'category_icon': category['icon'],
                'initial_forecast': p.initial_forecast,
                'budget_adjustment': p.budget_adjustment,
                'final_budget': final_budget,
                'recommended_estimate': recommended_estimate,
                'recommended_buffer': recommended_buffer,
                'recommended_budget': recommended_budget,
                'estimate_diff_display': format_diff(estimate_diff),
                'buffer_diff_display': format_diff(buffer_diff),
                'budget_diff_display': format_diff(budget_diff),
                'slider_min': slider_min,
                'slider_max': slider_max,
                'last_year_actual': last_year_actual,
            })

        return {
            'total_rounds': C.NUM_ROUNDS,
            'all_rounds_data': all_rounds_data,
        }

    @staticmethod
    def error_message(player: Player, values):
        errors = []
        
        # Validate Round 1 revision
        if values.get('resubmit_decision_r1') == True:
            if values.get('revised_forecast_r1') is None:
                errors.append('Please enter your revised forecast for Education.')
            if values.get('revised_adjustment_r1') is None:
                errors.append('Please enter your revised buffer for Education.')
        
        # Validate Round 2 revision
        if values.get('resubmit_decision_r2') == True:
            if values.get('revised_forecast_r2') is None:
                errors.append('Please enter your revised forecast for Infrastructure.')
            if values.get('revised_adjustment_r2') is None:
                errors.append('Please enter your revised buffer for Infrastructure.')
        
        # Validate Round 3 revision
        if values.get('resubmit_decision_r3') == True:
            if values.get('revised_forecast_r3') is None:
                errors.append('Please enter your revised forecast for Security.')
            if values.get('revised_adjustment_r3') is None:
                errors.append('Please enter your revised buffer for Security.')
        
        if errors:
            return ' '.join(errors)


class ResultsReveal(Page):
    template_name = 'budgeting/pages/ResultsReveal.html'

    @staticmethod
    def is_displayed(player: Player):
        # Only show after resubmission decisions (in round 3)
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._results_start = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.results_page_time = time.time() - player.participant._results_start

    @staticmethod
    def vars_for_template(player: Player):
        def format_deviation(dev):
            if dev >= 0:
                return f"+CHF {dev:,},000 (over)"
            else:
                return f"CHF {dev:,},000 (under)"

        # Calculate results for all 3 rounds
        all_rounds_data = []
        for round_num in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(round_num)
            category = get_category_data(round_num)
            actual_expense = category['target_year_actual']
            p.actual_expense = actual_expense
            
            # Calculate initial budget
            initial_budget = p.initial_forecast + p.budget_adjustment
            
            # Calculate final budget
            if p.resubmit_decision and p.revised_forecast is not None:
                final_forecast = p.revised_forecast
                final_adjustment = p.revised_adjustment or 0
            else:
                final_forecast = p.initial_forecast
                final_adjustment = p.budget_adjustment
            final_budget = final_forecast + final_adjustment
            
            # Calculate advisor recommendation
            recommended_estimate = category['recommended_estimate']
            recommended_buffer = category['recommended_buffer']
            advisor_budget = recommended_estimate + recommended_buffer
            
            # Calculate accuracies (deviation from actual)
            initial_deviation = initial_budget - actual_expense
            final_deviation = final_budget - actual_expense
            advisor_deviation = advisor_budget - actual_expense
            
            p.initial_accuracy = calculate_accuracy(initial_budget, actual_expense)
            p.final_accuracy = calculate_accuracy(final_budget, actual_expense)
            p.advisor_accuracy = calculate_accuracy(advisor_budget, actual_expense)
            
            all_rounds_data.append({
                'round_number': round_num,
                'category_name': category['name'],
                'category_icon': category['icon'],
                'actual_expense': actual_expense,
                'initial_budget': initial_budget,
                'final_budget': final_budget,
                'advisor_budget': advisor_budget,
                'initial_deviation': format_deviation(initial_deviation),
                'final_deviation': format_deviation(final_deviation),
                'advisor_deviation': format_deviation(advisor_deviation),
                'initial_accuracy': p.initial_accuracy,
                'final_accuracy': p.final_accuracy,
                'advisor_accuracy': p.advisor_accuracy,
                'revised': p.resubmit_decision,
            })

        # Calculate overall averages
        avg_initial_accuracy = sum(r['initial_accuracy'] for r in all_rounds_data) / len(all_rounds_data)
        avg_final_accuracy = sum(r['final_accuracy'] for r in all_rounds_data) / len(all_rounds_data)
        avg_advisor_accuracy = sum(r['advisor_accuracy'] for r in all_rounds_data) / len(all_rounds_data)

        return {
            'total_rounds': C.NUM_ROUNDS,
            'all_rounds_data': all_rounds_data,
            'avg_initial_accuracy': round(avg_initial_accuracy, 2),
            'avg_final_accuracy': round(avg_final_accuracy, 2),
            'avg_advisor_accuracy': round(avg_advisor_accuracy, 2),
        }


class ManipulationCheck(Page):
    template_name = 'budgeting/pages/ManipulationCheck.html'
    form_model = 'player'
    form_fields = ['manip_check_role', 'manip_check_advice']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    @staticmethod
    def error_message(player: Player, values):
        if not values.get('manip_check_role'):
            return 'Please answer the question about your assigned role.'
        if not values.get('manip_check_advice'):
            return 'Please answer the question about who provided the budget advice.'


class Impartiality(Page):
    template_name = 'budgeting/pages/Impartiality.html'
    form_model = 'player'
    form_fields = ['impartiality_unbiased', 'impartiality_objective', 'impartiality_fair', 'attention_check']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    @staticmethod
    def error_message(player: Player, values):
        if values.get('impartiality_unbiased') is None:
            return 'Please rate whether the advice was unbiased.'
        if values.get('impartiality_objective') is None:
            return 'Please rate whether the advice was objective.'
        if values.get('impartiality_fair') is None:
            return 'Please rate whether the advice was fair and balanced.'
        if values.get('attention_check') is None:
            return 'Please answer all questions.'
        if values['attention_check'] != 4:
            return 'Please read all questions carefully and answer accurately.'


class Controls(Page):
    template_name = 'budgeting/pages/Controls.html'
    form_model = 'player'
    form_fields = ['party_sympathy', 'party_other', 'trust_in_government', 'trust_in_ai', 'risk_attitude']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    @staticmethod
    def error_message(player: Player, values):
        if not values.get('party_sympathy'):
            return 'Please select a political party or indicate "Andere".'
        if values['party_sympathy'] == 'Andere' and not values.get('party_other'):
            return 'Please specify your political party preference.'
        if values.get('trust_in_government') is None:
            return 'Please rate your trust in the Swiss government.'
        if values.get('trust_in_ai') is None:
            return 'Please rate your trust in AI systems.'
        if values.get('risk_attitude') is None:
            return 'Please rate your willingness to take risks.'


class Demographics(Page):
    template_name = 'budgeting/pages/Demographics.html'
    form_model = 'player'
    form_fields = ['age', 'gender', 'work_experience', 'politics_experience', 'budgeting_experience']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class Thanks(Page):
    template_name = 'budgeting/pages/Thanks.html'
    form_model = 'player'
    form_fields = ['feedback']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        # Gather summary from all rounds
        all_rounds = player.in_all_rounds()
        round_summaries = []
        
        for p in all_rounds:
            category = get_category_data(p.round_number)
            if p.resubmit_decision and p.revised_forecast is not None:
                final_budget = p.revised_forecast + (p.revised_adjustment or 0)
            else:
                final_budget = p.initial_forecast + p.budget_adjustment
            
            round_summaries.append({
                'round': p.round_number,
                'category': category['name'],
                'icon': category['icon'],
                'final_budget': final_budget,
                'actual': p.actual_expense,
                'accuracy': p.final_accuracy,
            })
        
        # Calculate average accuracy
        avg_accuracy = sum(r['accuracy'] for r in round_summaries) / len(round_summaries)
        
        return {
            'round_summaries': round_summaries,
            'avg_accuracy': round(avg_accuracy, 2),
        }

    @staticmethod
    def js_vars(player: Player):
        return dict(
            completionlink=player.session.config.get('completionlink', '')
        )


page_sequence = [
    Consent,
    Instructions,
    RoleAssignment,
    # RoundIntro,
    InitialForecast,
    AdviceFeedback,
    ResubmissionDecision,
    # ResultsReveal,
    ManipulationCheck,
    Impartiality,
    Controls,
    Demographics,
    Thanks,
]
