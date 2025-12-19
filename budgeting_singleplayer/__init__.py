from otree.api import *
import random

doc = """
Single-Player Budget Forecasting Experiment:
Participants are randomly assigned to either be a Politician or Finance Director (IV1),
submit a budget forecast for municipal operating income with justification, receive advice 
from either a Human Expert or AI Model (IV2), and decide whether to revise their submission.
"""


class C(BaseConstants):
    NAME_IN_URL = 'budgeting_sp'
    PLAYERS_PER_GROUP = None  # Single player
    NUM_ROUNDS = 1

    # Slider adjustment range (percentage above/below forecast)
    SLIDER_RANGE_PERCENT = 50  # Players can adjust +/- 50% from forecast

    # Operating Income Data (in CHF thousands)
    ACCOUNT_NAME = 'Operating Income'
    FORECAST = 218  # Current year's actual operating income (reference for next year's forecast)
    
    # Historical data: 10 years of budgeted vs actual operating income
    # Data shows more annual variability with actual consistently exceeding budget
    HISTORICAL_BUDGET = [150, 151, 148, 152, 155, 158, 154, 160, 165, 170]  # Budgeted amounts with variation
    HISTORICAL_ACTUAL = [152, 155, 160, 165, 170, 180, 183, 193, 205, 218]  # Actual amounts with year-to-year variation
    HISTORICAL = HISTORICAL_ACTUAL[-5:]  # Last 5 years of actual income for display

    # Advice parameters
    RECOMMENDED_BEST_ESTIMATE = 100  # Recommended best estimate for next year (lower than current 218)
    RECOMMENDED_BUFFER = 10  # Buffer in CHF thousands (positive = budget above estimate)
    # Note: RECOMMENDED_BUDGET = RECOMMENDED_BEST_ESTIMATE + RECOMMENDED_BUFFER = 100 + 10 = 110


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

    # ===== Initial Forecast Page =====
    initial_forecast = models.IntegerField(
        min=0,
        max=1000,
        label="Your best estimate for next year's Operating Income (CHF thousands)"
    )
    budget_adjustment = models.IntegerField(
        label="Buffer for uncertainty (CHF thousands)",
        doc="Positive = increase budget above estimate, Negative = decrease below estimate"
    )
    initial_justification = models.LongStringField(
        label="Please justify your budget decision:",
        blank=False
    )

    # ===== Resubmission Decision Page =====
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
        label="Your revised budget adjustment (CHF thousands)",
        blank=True
    )
    resubmission_justification = models.LongStringField(
        label="Please explain your decision (whether you revised or kept your original submission):",
        blank=False
    )

    # ===== Manipulation Checks =====
    manip_check_role = models.StringField(
        label="Which role were you assigned at the beginning of the study?",
        choices=[
            ['politician', 'Politician'],
            ['finance_director', 'Finance Director']
        ],
        widget=widgets.RadioSelect
    )
    manip_check_advice = models.StringField(
        label="Who provided the budget advice you received?",
        choices=[
            ['human_expert', 'A civil servant specialized in this account'],
            ['ai_model', 'An AI model specially trained for this account']
        ],
        widget=widgets.RadioSelect
    )

    # ===== Impartiality Mediators (7-point Likert) =====
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

    # ===== Controls =====
    party_sympathy = models.StringField(
        label="Which Swiss political party do you most sympathize with?",
        choices=[
            'Grüne',
            'SP',
            'GLP',
            'EVP',
            'Mitte',
            'FDP',
            'SVP',
            'Andere'
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
        label="To ensure you are paying attention, please select '4' for this question.",
        choices=[[1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5']],
        widget=widgets.RadioSelectHorizontal
    )

    # ===== Demographics =====
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
    feedback = models.LongStringField(
        label="Do you have any comments or feedback about this study? (optional)",
        blank=True
    )


# ===== FUNCTIONS =====

def creating_session(subsession: Subsession):
    """Randomly assign conditions to each player"""
    for player in subsession.get_players():
        # IV1: Role condition
        player.role_condition = random.choice(['politician', 'finance_director'])
        # IV2: Advice source condition
        player.advice_condition = random.choice(['human_expert', 'ai_model'])
        
        # Store in participant vars for access across pages
        player.participant.vars['role_condition'] = player.role_condition
        player.participant.vars['advice_condition'] = player.advice_condition


def get_advice_text(player: Player):
    """Generate the advice text based on condition - same advice for all conditions"""
    recommended_estimate = C.RECOMMENDED_BEST_ESTIMATE
    recommended_buffer = C.RECOMMENDED_BUFFER
    recommended_budget = recommended_estimate + recommended_buffer
    buffer_amount = abs(recommended_buffer)
    buffer_percent = round((recommended_buffer / recommended_estimate) * 100, 1)

    # Determine buffer description based on sign
    if recommended_buffer >= 0:
        buffer_description = f"a buffer of CHF {buffer_amount:,},000 above best estimate"
    else:
        buffer_description = f"a conservative buffer of CHF {buffer_amount:,},000 below best estimate"

    advice_text = f"""
    <p><strong>Recommended Best Estimate:</strong> CHF {recommended_estimate:,},000</p>
    <p><strong>Recommended Buffer:</strong> CHF {recommended_buffer:,},000</p>
    <p><strong>Recommended Budget:</strong> CHF {recommended_budget:,},000</p>
    
    <p><strong>Rationale:</strong></p>
    <ul>
        <li><strong>Why lower than last year:</strong> While the current year's actual operating income reached CHF 218,000, 
        additional information about the municipality's economic outlook suggests a significant decline is expected next year. 
        Key factors include anticipated changes in local business activity, potential decreases in commercial tax revenues, 
        and economic headwinds affecting the region. Therefore, a best estimate of CHF {recommended_estimate:,},000 
        more accurately reflects next year's expected performance.</li>
        <li><strong>Why apply a buffer above the estimate:</strong> Despite expecting lower operating income, 
        there remains uncertainty in the forecast. Adding a modest buffer of CHF {buffer_amount:,},000 ({abs(buffer_percent)}%) 
        above the best estimate provides some cushion for potential variations while still maintaining fiscal prudence 
        given the challenging economic environment.</li>
        <li><strong>Balanced approach:</strong> Setting the budget at CHF {recommended_budget:,},000 balances the need 
        for realistic expectations with maintaining adequate resources for essential municipal services.</li>
    </ul>
    """
    return advice_text


def get_advisor_name(player: Player):
    """Get the name/title of the advisor based on condition"""
    if player.advice_condition == 'human_expert':
        return "Civil Servant Specialized in Municipal Finance"
    else:
        return "AI Model Trained for Municipal Revenue Forecasting"


# ===== PAGES =====

class Consent(Page):
    template_name = 'budgeting_singleplayer/pages/Consent.html'
    form_model = 'player'
    form_fields = ['declined_consent']


class Instructions(Page):
    template_name = 'budgeting_singleplayer/pages/Instructions.html'

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'forecast': C.FORECAST,
        }


class RoleAssignment(Page):
    template_name = 'budgeting_singleplayer/pages/RoleAssignment.html'

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


class InitialForecast(Page):
    template_name = 'budgeting_singleplayer/pages/InitialForecast.html'
    form_model = 'player'
    form_fields = ['initial_forecast', 'budget_adjustment', 'initial_justification']

    @staticmethod
    def vars_for_template(player: Player):
        forecast = C.FORECAST
        historical_budget = C.HISTORICAL_BUDGET
        historical_actual = C.HISTORICAL_ACTUAL
        slider_min = max(0, int(forecast * (1 - C.SLIDER_RANGE_PERCENT / 100)))
        slider_max = min(1000, int(forecast * (1 + C.SLIDER_RANGE_PERCENT / 100)))
        
        # Calculate adjustment range - buffer can only be positive (0 to 100%)
        adjustment_min = 0
        adjustment_max = int(forecast * 1.0)  # 100% of forecast

        # Format historical data for display
        historical_budget_formatted = ["{:,}".format(val * 1000) for val in historical_budget]
        historical_actual_formatted = ["{:,}".format(val * 1000) for val in historical_actual]
        historical_diff_formatted = ["{:,}".format((actual - budget) * 1000) 
                                      for budget, actual in zip(historical_budget, historical_actual)]

        role = player.role_condition.replace('_', ' ').title()

        return {
            'account_name': C.ACCOUNT_NAME,
            'forecast': forecast,
            'historical_budget': historical_budget,
            'historical_actual': historical_actual,
            'historical_budget_formatted': historical_budget_formatted,
            'historical_actual_formatted': historical_actual_formatted,
            'historical_diff_formatted': historical_diff_formatted,
            'year_indices': list(range(10)),
            'slider_min': slider_min,
            'slider_max': slider_max,
            'adjustment_min': adjustment_min,
            'adjustment_max': adjustment_max,
            'role': role,
        }


class AdviceFeedback(Page):
    template_name = 'budgeting_singleplayer/pages/AdviceFeedback.html'

    @staticmethod
    def vars_for_template(player: Player):
        advice_text = get_advice_text(player)
        advisor_name = get_advisor_name(player)
        
        # Calculate what the participant submitted
        final_budget = player.initial_forecast + player.budget_adjustment
        recommended_estimate = C.RECOMMENDED_BEST_ESTIMATE
        recommended_buffer = C.RECOMMENDED_BUFFER
        recommended_budget = recommended_estimate + recommended_buffer
        
        # Calculate differences for display
        estimate_diff = player.initial_forecast - recommended_estimate
        buffer_diff = player.budget_adjustment - recommended_buffer
        budget_diff = final_budget - recommended_budget
        
        # Format differences with +/- sign
        if estimate_diff >= 0:
            estimate_diff_display = f"+CHF {estimate_diff:,},000"
        else:
            estimate_diff_display = f"CHF {estimate_diff:,},000"
            
        if buffer_diff >= 0:
            buffer_diff_display = f"+CHF {buffer_diff:,},000"
        else:
            buffer_diff_display = f"CHF {buffer_diff:,},000"
            
        if budget_diff >= 0:
            budget_diff_display = f"+CHF {budget_diff:,},000"
        else:
            budget_diff_display = f"CHF {budget_diff:,},000"

        return {
            'advisor_name': advisor_name,
            'advice_text': advice_text,
            'advice_condition': player.advice_condition,
            'initial_forecast': player.initial_forecast,
            'budget_adjustment': player.budget_adjustment,
            'final_budget': final_budget,
            'recommended_estimate': recommended_estimate,
            'recommended_buffer': recommended_buffer,
            'recommended_budget': recommended_budget,
            'estimate_diff_display': estimate_diff_display,
            'buffer_diff_display': buffer_diff_display,
            'budget_diff_display': budget_diff_display,
        }


class ResubmissionDecision(Page):
    template_name = 'budgeting_singleplayer/pages/ResubmissionDecision.html'
    form_model = 'player'
    form_fields = ['resubmit_decision', 'revised_forecast', 'revised_adjustment', 'resubmission_justification']

    @staticmethod
    def vars_for_template(player: Player):
        forecast = C.FORECAST
        slider_min = max(0, int(forecast * (1 - C.SLIDER_RANGE_PERCENT / 100)))
        slider_max = min(1000, int(forecast * (1 + C.SLIDER_RANGE_PERCENT / 100)))
        adjustment_min = 0
        adjustment_max = int(forecast * 1.0)  # 100% of forecast

        final_budget = player.initial_forecast + player.budget_adjustment
        recommended_estimate = C.RECOMMENDED_BEST_ESTIMATE
        recommended_buffer = C.RECOMMENDED_BUFFER
        recommended_budget = recommended_estimate + recommended_buffer
        
        # Calculate differences for display
        estimate_diff = player.initial_forecast - recommended_estimate
        buffer_diff = player.budget_adjustment - recommended_buffer
        budget_diff = final_budget - recommended_budget
        
        # Format differences with +/- sign
        if estimate_diff >= 0:
            estimate_diff_display = f"+CHF {estimate_diff:,},000"
        else:
            estimate_diff_display = f"CHF {estimate_diff:,},000"
            
        if buffer_diff >= 0:
            buffer_diff_display = f"+CHF {buffer_diff:,},000"
        else:
            buffer_diff_display = f"CHF {buffer_diff:,},000"
            
        if budget_diff >= 0:
            budget_diff_display = f"+CHF {budget_diff:,},000"
        else:
            budget_diff_display = f"CHF {budget_diff:,},000"

        return {
            'initial_forecast': player.initial_forecast,
            'budget_adjustment': player.budget_adjustment,
            'final_budget': final_budget,
            'recommended_estimate': recommended_estimate,
            'recommended_buffer': recommended_buffer,
            'recommended_budget': recommended_budget,
            'estimate_diff_display': estimate_diff_display,
            'buffer_diff_display': buffer_diff_display,
            'budget_diff_display': budget_diff_display,
            'slider_min': slider_min,
            'slider_max': slider_max,
            'adjustment_min': adjustment_min,
            'adjustment_max': adjustment_max,
            'forecast': forecast,
        }

    @staticmethod
    def error_message(player: Player, values):
        if values['resubmit_decision'] == True:
            if values['revised_forecast'] is None:
                return 'Please enter your revised forecast.'
            if values['revised_adjustment'] is None:
                return 'Please enter your revised budget adjustment.'


class ManipulationCheck(Page):
    template_name = 'budgeting_singleplayer/pages/ManipulationCheck.html'
    form_model = 'player'
    form_fields = ['manip_check_role', 'manip_check_advice']


class Impartiality(Page):
    template_name = 'budgeting_singleplayer/pages/Impartiality.html'
    form_model = 'player'
    form_fields = ['impartiality_unbiased', 'impartiality_objective', 'impartiality_fair']


class Controls(Page):
    template_name = 'budgeting_singleplayer/pages/Controls.html'
    form_model = 'player'
    form_fields = ['party_sympathy', 'party_other', 'trust_in_government', 'trust_in_ai', 'risk_attitude', 'attention_check']


class Demographics(Page):
    template_name = 'budgeting_singleplayer/pages/Demographics.html'
    form_model = 'player'
    form_fields = ['age', 'gender', 'work_experience', 'politics_experience', 'budgeting_experience', 'feedback']


class Thanks(Page):
    template_name = 'budgeting_singleplayer/pages/Thanks.html'

    @staticmethod
    def vars_for_template(player: Player):
        # Calculate final budget for display
        if player.resubmit_decision and player.revised_forecast is not None:
            final_forecast = player.revised_forecast
            final_adjustment = player.revised_adjustment or 0
        else:
            final_forecast = player.initial_forecast
            final_adjustment = player.budget_adjustment
        
        final_budget = final_forecast + final_adjustment

        return {
            'final_forecast': final_forecast,
            'final_adjustment': final_adjustment,
            'final_budget': final_budget,
        }


page_sequence = [
    Consent,
    Instructions,
    RoleAssignment,
    InitialForecast,
    AdviceFeedback,
    ResubmissionDecision,
    ManipulationCheck,
    Impartiality,
    Controls,
    Demographics,
    Thanks,
]
