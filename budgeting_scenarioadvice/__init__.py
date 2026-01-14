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
            'current_actual': 145,  # Most recent year's actual
            'target_year_actual': 155,  # The "true" actual for the forecasting year
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
            'current_actual': 165,  # Most recent year's actual
            'target_year_actual': 175,  # The "true" actual for the forecasting year
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
            'current_actual': 88,  # Most recent year's actual
            'target_year_actual': 92,  # The "true" actual for the forecasting year
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
        label="Which role were you assigned at the beginning of the study?",
        choices=[
            ['politician', 'Politician'],
            ['finance_director', 'Finance Director']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    manip_check_advice = models.StringField(
        label="Who provided the budget advice you received?",
        choices=[
            ['human_expert', 'A civil servant specialized in this account'],
            ['ai_model', 'An AI model specially trained for this account']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    # ===== Impartiality Mediators (only in final round) =====
    impartiality_unbiased = models.IntegerField(
        label="The advice I received was unbiased.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )
    impartiality_objective = models.IntegerField(
        label="The advice I received was objective.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )
    impartiality_fair = models.IntegerField(
        label="The advice I received was fair and balanced.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )

    # ===== Controls (only in final round) =====
    party_sympathy = models.StringField(
        label="Which Swiss political party do you most sympathize with?",
        choices=[
            'Grüne', 'SP', 'GLP', 'EVP', 'Mitte', 'FDP', 'SVP', 'Andere'
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    party_other = models.StringField(
        label="If you selected 'Andere', please specify:",
        blank=True
    )
    trust_in_government = models.IntegerField(
        label="How much do you trust the Swiss government?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )
    trust_in_ai = models.IntegerField(
        label="How much do you trust AI systems to provide accurate advice?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )
    risk_attitude = models.IntegerField(
        label="How willing are you to take risks in general?",
        choices=[[0, '0 - Not at all willing'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'], [10, '10 - Very willing']],
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )
    attention_check = models.IntegerField(
        label="If you are reading this carefully, please select 'Agree'.",
        choices=[[1, 'Strongly disagree'], [2, 'Disagree'], [3, 'Somewhat disagree'], [4, 'Neutral'], [5, 'Somewhat agree'], [6, 'Agree'], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )

    # ===== Demographics (only in final round) =====
    age = models.IntegerField(
        label="What is your age?",
        min=18,
        max=100,
        blank=True
    )
    gender = models.StringField(
        label="What is your gender?",
        choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'],
        widget=widgets.RadioSelect,
        blank=True
    )
    work_experience = models.IntegerField(
        label="How many years of work experience do you have?",
        min=0,
        max=60,
        blank=True
    )
    politics_experience = models.IntegerField(
        label="How many years of experience in politics or public administration do you have?",
        min=0,
        max=60,
        blank=True
    )
    budgeting_experience = models.IntegerField(
        label="How many years of experience with budgeting or financial planning do you have?",
        min=0,
        max=60,
        blank=True
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


def get_advice_text(player: Player):
    """Generate the advice text based on category"""
    category = get_category_data(player.round_number)
    recommended_estimate = category['recommended_estimate']
    recommended_buffer = category['recommended_buffer']
    recommended_budget = recommended_estimate + recommended_buffer
    buffer_percent = round((recommended_buffer / recommended_estimate) * 100, 1)
    
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
    return advice_text


def get_advisor_name(player: Player):
    """Get the name/title of the advisor based on condition"""
    category = get_category_data(player.round_number)
    if player.advice_condition == 'human_expert':
        return f"Civil Servant Specialized in {category['name']} Budget"
    else:
        return f"AI Model Trained for {category['name']} Forecasting"


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
    form_fields = ['initial_forecast', 'budget_adjustment', 'initial_justification']

    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._forecast_start = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.forecast_page_time = time.time() - player.participant._forecast_start

    @staticmethod
    def vars_for_template(player: Player):
        category = get_category_data(player.round_number)
        current_actual = category['current_actual']
        
        slider_min = max(0, int(current_actual * (1 - C.SLIDER_RANGE_PERCENT / 100)))
        slider_max = min(1000, int(current_actual * (1 + C.SLIDER_RANGE_PERCENT / 100)))
        adjustment_min = 0
        adjustment_max = int(current_actual * 1.0)

        role = player.role_condition.replace('_', ' ').title()

        return {
            'round_number': player.round_number,
            'total_rounds': C.NUM_ROUNDS,
            'category_name': category['name'],
            'category_icon': category['icon'],
            'current_actual': current_actual,
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
    def get_timeout_seconds(player: Player):
        player.participant._advice_start = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.advice_page_time = time.time() - player.participant._advice_start

    @staticmethod
    def vars_for_template(player: Player):
        category = get_category_data(player.round_number)
        advice_text = get_advice_text(player)
        advisor_name = get_advisor_name(player)
        
        final_budget = player.initial_forecast + player.budget_adjustment
        recommended_estimate = category['recommended_estimate']
        recommended_buffer = category['recommended_buffer']
        recommended_budget = recommended_estimate + recommended_buffer
        
        estimate_diff = player.initial_forecast - recommended_estimate
        buffer_diff = player.budget_adjustment - recommended_buffer
        budget_diff = final_budget - recommended_budget
        
        def format_diff(diff):
            if diff >= 0:
                return f"+CHF {diff:,},000"
            else:
                return f"CHF {diff:,},000"

        return {
            'round_number': player.round_number,
            'total_rounds': C.NUM_ROUNDS,
            'category_name': category['name'],
            'category_name_lower': category['name'].lower(),
            'category_icon': category['icon'],
            'advisor_name': advisor_name,
            'advice_text': advice_text,
            'advice_condition': player.advice_condition,
            'initial_forecast': player.initial_forecast,
            'budget_adjustment': player.budget_adjustment,
            'final_budget': final_budget,
            'recommended_estimate': recommended_estimate,
            'recommended_buffer': recommended_buffer,
            'recommended_budget': recommended_budget,
            'estimate_diff_display': format_diff(estimate_diff),
            'buffer_diff_display': format_diff(buffer_diff),
            'budget_diff_display': format_diff(budget_diff),
        }


class ResubmissionDecision(Page):
    template_name = 'budgeting/pages/ResubmissionDecision.html'
    form_model = 'player'
    form_fields = ['resubmit_decision', 'revised_forecast', 'revised_adjustment', 'resubmission_justification']

    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._resubmission_start = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.resubmission_page_time = time.time() - player.participant._resubmission_start

    @staticmethod
    def vars_for_template(player: Player):
        category = get_category_data(player.round_number)
        current_actual = category['current_actual']
        
        slider_min = max(0, int(current_actual * (1 - C.SLIDER_RANGE_PERCENT / 100)))
        slider_max = min(1000, int(current_actual * (1 + C.SLIDER_RANGE_PERCENT / 100)))
        adjustment_min = 0
        adjustment_max = int(current_actual * 1.0)

        final_budget = player.initial_forecast + player.budget_adjustment
        recommended_estimate = category['recommended_estimate']
        recommended_buffer = category['recommended_buffer']
        recommended_budget = recommended_estimate + recommended_buffer
        
        estimate_diff = player.initial_forecast - recommended_estimate
        buffer_diff = player.budget_adjustment - recommended_buffer
        budget_diff = final_budget - recommended_budget
        
        def format_diff(diff):
            if diff >= 0:
                return f"+CHF {diff:,},000"
            else:
                return f"CHF {diff:,},000"

        return {
            'round_number': player.round_number,
            'total_rounds': C.NUM_ROUNDS,
            'category_name': category['name'],
            'category_icon': category['icon'],
            'initial_forecast': player.initial_forecast,
            'budget_adjustment': player.budget_adjustment,
            'final_budget': final_budget,
            'recommended_estimate': recommended_estimate,
            'recommended_buffer': recommended_buffer,
            'recommended_budget': recommended_budget,
            'estimate_diff_display': format_diff(estimate_diff),
            'buffer_diff_display': format_diff(buffer_diff),
            'budget_diff_display': format_diff(budget_diff),
            'slider_min': slider_min,
            'slider_max': slider_max,
            'adjustment_min': adjustment_min,
            'adjustment_max': adjustment_max,
            'current_actual': current_actual,
        }

    @staticmethod
    def error_message(player: Player, values):
        if values['resubmit_decision'] == True:
            if values['revised_forecast'] is None:
                return 'Please enter your revised forecast.'
            if values['revised_adjustment'] is None:
                return 'Please enter your revised buffer.'


class ResultsReveal(Page):
    template_name = 'budgeting/pages/ResultsReveal.html'

    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._results_start = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.results_page_time = time.time() - player.participant._results_start

    @staticmethod
    def vars_for_template(player: Player):
        category = get_category_data(player.round_number)
        actual_expense = category['target_year_actual']
        player.actual_expense = actual_expense
        
        # Calculate initial budget
        initial_budget = player.initial_forecast + player.budget_adjustment
        
        # Calculate final budget
        if player.resubmit_decision and player.revised_forecast is not None:
            final_forecast = player.revised_forecast
            final_adjustment = player.revised_adjustment or 0
        else:
            final_forecast = player.initial_forecast
            final_adjustment = player.budget_adjustment
        final_budget = final_forecast + final_adjustment
        
        # Calculate advisor recommendation
        recommended_estimate = category['recommended_estimate']
        recommended_buffer = category['recommended_buffer']
        advisor_budget = recommended_estimate + recommended_buffer
        
        # Calculate accuracies (deviation from actual)
        initial_deviation = initial_budget - actual_expense
        final_deviation = final_budget - actual_expense
        advisor_deviation = advisor_budget - actual_expense
        
        player.initial_accuracy = calculate_accuracy(initial_budget, actual_expense)
        player.final_accuracy = calculate_accuracy(final_budget, actual_expense)
        player.advisor_accuracy = calculate_accuracy(advisor_budget, actual_expense)
        
        def format_deviation(dev):
            if dev >= 0:
                return f"+CHF {dev:,},000 (over)"
            else:
                return f"CHF {dev:,},000 (under)"

        return {
            'round_number': player.round_number,
            'next_round_number': player.round_number + 1,
            'total_rounds': C.NUM_ROUNDS,
            'category_name': category['name'],
            'category_icon': category['icon'],
            'actual_expense': actual_expense,
            'initial_budget': initial_budget,
            'final_budget': final_budget,
            'advisor_budget': advisor_budget,
            'initial_deviation': format_deviation(initial_deviation),
            'final_deviation': format_deviation(final_deviation),
            'advisor_deviation': format_deviation(advisor_deviation),
            'initial_accuracy': player.initial_accuracy,
            'final_accuracy': player.final_accuracy,
            'advisor_accuracy': player.advisor_accuracy,
            'revised': player.resubmit_decision,
            'is_last_round': player.round_number == C.NUM_ROUNDS,
        }


class ManipulationCheck(Page):
    template_name = 'budgeting/pages/ManipulationCheck.html'
    form_model = 'player'
    form_fields = ['manip_check_role', 'manip_check_advice']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class Impartiality(Page):
    template_name = 'budgeting/pages/Impartiality.html'
    form_model = 'player'
    form_fields = ['impartiality_unbiased', 'impartiality_objective', 'impartiality_fair']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class Controls(Page):
    template_name = 'budgeting/pages/Controls.html'
    form_model = 'player'
    form_fields = ['party_sympathy', 'party_other', 'trust_in_government', 'trust_in_ai', 'risk_attitude', 'attention_check']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    @staticmethod
    def error_message(player: Player, values):
        if values['attention_check'] != 6:
            return 'Question 6 is incorrect. Please review and try again.'


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
    RoundIntro,
    InitialForecast,
    AdviceFeedback,
    ResubmissionDecision,
    ResultsReveal,
    ManipulationCheck,
    Impartiality,
    Controls,
    Demographics,
    Thanks,
]
