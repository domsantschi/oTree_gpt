from otree.api import *
from markupsafe import Markup
import random
import time

doc = """
Single-Round Budget Forecasting Experiment:
Participants complete a budget forecasting task for the Education expense category:
1. Best estimate + buffer + justification
2. Advice from Human Expert or AI Model
3. Decision to keep or revise submission
"""


class C(BaseConstants):
    NAME_IN_URL = 'budgeting'
    PLAYERS_PER_GROUP = None  # Single player
    NUM_ROUNDS = 1

    # Slider adjustment range (fixed amount above/below last year actual)
    SLIDER_RANGE_AMOUNT = 100000

    # Education category data
    CATEGORY = {
        'name': 'Education',
        'icon': '📚',
        'description': 'Public education spending including schools, universities, and educational programs',
        'historical_budget': [92000, 95000, 99000, 104000, 108000, 115000, 120000, 128000, 135000],
        'historical_actual': [85000, 88000, 90000, 92000, 95000, 98000, 100000, 103000, 106000],
        'last_year_actual': 106000,  # Y9 actual (most recent completed year)
        'comprehension_answer': 106000,  # Y9 actual for comprehension check
        'target_year_actual': 115000,  # The "true" actual for the forecasting year (Y10)
        'recommended_estimate': 110000,
        'recommended_buffer': 8000,
        'trend_description': 'Education expenses have consistently exceeded budgeted amounts by an average of 15-20% over the past decade, driven by growing enrollment and infrastructure needs.'
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # ===== Consent =====
    declined_consent = models.BooleanField(initial=False)

    # ===== Knowledge Check =====
    knowledge_q1 = models.StringField(
        label="Public sector entities such as cities and regional governments budget their revenues and expenses to _______.",
        choices=[
            ['a', 'Plan their financial capital need'],
            ['b', 'Reduce internal communications'],
            ['c', 'Forecast citizen wellbeing'],
        ],
        widget=widgets.RadioSelect
    )
    knowledge_q2 = models.StringField(
        label="Budgeting is important because _______.",
        choices=[
            ['a', 'Budgeting completely ignores the performance of the past'],
            ['b', 'Budgeting helps to improve resource planning'],
            ['c', 'Budgeting helps to market an organization to its customers'],
        ],
        widget=widgets.RadioSelect
    )
    knowledge_q3 = models.StringField(
        label="In budgeting of expenses, a safety buffer can be built in by _______.",
        choices=[
            ['a', 'Budgeting expenses higher than expected'],
            ['b', 'Budgeting expenses lower than expected'],
            ['c', 'Refraining from any budgeting activities'],
        ],
        widget=widgets.RadioSelect
    )

    # ===== Conditions (IVs) =====
    construal_level = models.StringField(
        choices=['concrete', 'abstract'],
        doc="IV1: Construal level condition (concrete=how, abstract=why)"
    )
    construal_response = models.LongStringField(
        label="Please describe your thoughts:",
        blank=False,
        doc="Participant's response to the construal level reflection task"
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
        max=500000,
        label="Your best estimate (CHF)"
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
        max=500000,
        label="Your revised forecast (CHF)",
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
    manip_check_construal = models.StringField(
        label="<b>At the beginning of the study, you were asked to reflect on...</b>",
        choices=[
            ['how', 'HOW the budgeting task is done (specific steps and processes)'],
            ['why', 'WHY the budgeting task is done (broader goals and purposes)']
        ],
        widget=widgets.RadioSelect
    )
    manip_check_advice = models.StringField(
        label=Markup("<b>Who provided the budget advice</b> you received?"),
        choices=[
            ['human_expert', Markup('A <b>Financial Controller</b> specialized in the budget category')],
            ['ai_model', Markup('An <b>AI Model</b> specialized in the budget category')]
        ],
        widget=widgets.RadioSelect
    )

    # ===== Advice Perception Mediators =====
    # Affective Trust (5 items)
    affective_trust_1 = models.IntegerField(
        label="If I share my concerns with the budget advisor, <b>I feel they would listen</b>.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    affective_trust_2 = models.IntegerField(
        label="When making important decisions, I feel <b>the advisor acts in the best interest of me</b> and other stakeholders.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    affective_trust_3 = models.IntegerField(
        label="I would feel a <b>sense of personal loss if the budget advisor were no longer available</b> in future.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    affective_trust_4 = models.IntegerField(
        label="In the future, <b>I feel I could count on the budget advisor</b> to consider how their decisions and actions will affect me and other stakeholders.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    affective_trust_5 = models.IntegerField(
        label="I feel the budget advisor would <b>display a warm and caring attitude</b> towards me and other stakeholders.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    
    # Cognitive Trust (5 items)
    cognitive_trust_1 = models.IntegerField(
        label="The budget advisor approaches their job with <b>professionalism and dedication</b>.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    cognitive_trust_2 = models.IntegerField(
        label="Given the budget advisor's track record, I see <b>no reason to doubt their competence</b> and preparation for the job.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    cognitive_trust_3 = models.IntegerField(
        label="<b>I can rely on the budget advisor</b> not to make my job of budgeting expenses more difficult by careless work.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    cognitive_trust_4 = models.IntegerField(
        label="<b>Most people</b>, even those who are not big fans of the budget advisor, <b>likely trust and respect their work</b>.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    cognitive_trust_5 = models.IntegerField(
        label="Others who must interact with the budget advisor likely <b>consider them to be trustworthy</b>.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    
    # Attention check for mediators
    mediator_attention_check = models.IntegerField(
        label="If you are reading this carefully, <b>please select 'Agree'</b>.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6 - Agree'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )

    # ===== Controls (only in final round) =====
    political_ideology = models.IntegerField(
        label="Where would you place yourself on the political spectrum?",
        choices=[[1, '1 - Very left-leaning'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Very right-leaning']],
        widget=widgets.RadioSelectHorizontal
    )
    trust_in_government = models.IntegerField(
        label="I trust human experts to provide accurate and reliable advice.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    trust_in_ai = models.IntegerField(
        label="I trust AI models to provide accurate and reliable advice.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    risk_attitude = models.IntegerField(
        label="I am generally willing to take risks.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    ai_familiarity = models.IntegerField(
        label="I regularly use AI tools (e.g., ChatGPT, Copilot) in my daily activities.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    attention_check = models.IntegerField(
        label="If you are reading this carefully, please select 'Neutral'.",
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4 - Neutral'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )

    # ===== Demographics (only in final round) =====
    age = models.StringField(
        label="What is your age?",
        choices=['18-24 years', '25-34 years', '35-50 years', '51-65 years', 'Over 65 years'],
        widget=widgets.RadioSelect
    )
    gender = models.StringField(
        label="What is your gender?",
        choices=['Male', 'Female', 'Other', 'Prefer not to say'],
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


# ===== FUNCTIONS =====

def creating_session(subsession: Subsession):
    """Randomly assign conditions to each player"""
    for player in subsession.get_players():
        # IV1: Construal level condition (concrete=how, abstract=why)
        player.construal_level = random.choice(['concrete', 'abstract'])
        # IV2: Advice source condition
        player.advice_condition = random.choice(['human_expert', 'ai_model'])
        # Set category name
        player.category_name = C.CATEGORY['name']


def get_category_data():
    """Get the category data"""
    return C.CATEGORY


# ===== PAGES =====

class Consent(Page):
    template_name = 'budgeting/pages/Consent.html'
    form_model = 'player'
    form_fields = ['declined_consent']


class KnowledgeCheck(Page):
    template_name = 'budgeting/pages/KnowledgeCheck.html'
    form_model = 'player'
    form_fields = ['knowledge_q1', 'knowledge_q2', 'knowledge_q3']

    @staticmethod
    def error_message(player: Player, values):
        # Correct answers: q1=a, q2=b, q3=a
        errors = []
        if values['knowledge_q1'] != 'a':
            errors.append('Question 1 is incorrect.')
        if values['knowledge_q2'] != 'b':
            errors.append('Question 2 is incorrect.')
        if values['knowledge_q3'] != 'a':
            errors.append('Question 3 is incorrect.')
        
        if errors:
            return 'Some answers are incorrect. Please review and try again: ' + ' '.join(errors)


class Instructions(Page):
    template_name = 'budgeting/pages/Instructions.html'


class Context(Page):
    template_name = 'budgeting/pages/Context.html'


class ConstrualLevel(Page):
    template_name = 'budgeting/pages/ConstrualLevel.html'
    form_model = 'player'
    form_fields = ['construal_response']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'construal_level': player.construal_level,
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
        category = get_category_data()
        correct_answer = category['comprehension_answer']
        if values.get('comprehension_check') != correct_answer:
            return f'Incorrect. Please check the historical data table and enter the actual expenses for Y9.'

    @staticmethod
    def vars_for_template(player: Player):
        category = get_category_data()
        last_year_actual = category['last_year_actual']
        
        slider_min = max(0, last_year_actual - C.SLIDER_RANGE_AMOUNT)
        slider_max = last_year_actual + C.SLIDER_RANGE_AMOUNT
        adjustment_min = 0
        adjustment_max = int(last_year_actual * 1.0)

        return {
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
        def format_diff(diff):
            if diff >= 0:
                return f"+CHF {diff:,}"
            else:
                return f"CHF {diff:,}"

        category = get_category_data()
        
        final_budget = player.initial_forecast + player.budget_adjustment
        recommended_estimate = category['recommended_estimate']
        recommended_buffer = category['recommended_buffer']
        recommended_budget = recommended_estimate + recommended_buffer
        buffer_percent = round((recommended_buffer / recommended_estimate) * 100, 1)
        
        estimate_diff = player.initial_forecast - recommended_estimate
        buffer_diff = player.budget_adjustment - recommended_buffer
        budget_diff = final_budget - recommended_budget
        
        advice_text = f"""
        <p><strong>Recommended Best Estimate:</strong> CHF {recommended_estimate:,}</p>
        <p><strong>Recommended Buffer:</strong> CHF {recommended_buffer:,} ({buffer_percent}%)</p>
        <p><strong>Recommended Budget:</strong> CHF {recommended_budget:,}</p>
        
        <p><strong>Rationale:</strong></p>
        <ul>
            <li><strong>Historical trend analysis:</strong> {category['trend_description']}</li>
            <li><strong>Estimate justification:</strong> Based on historical patterns and current economic indicators, 
            a best estimate of CHF {recommended_estimate:,} reflects the expected {category['name'].lower()} expenses 
            for the upcoming year.</li>
            <li><strong>Buffer rationale:</strong> A buffer of CHF {recommended_buffer:,} ({buffer_percent}%) 
            accounts for potential variations and uncertainties while maintaining fiscal prudence.</li>
        </ul>
        """
        
        data = {
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
            'advice_text': advice_text,
        }

        # Advisor name based on condition
        if player.advice_condition == 'human_expert':
            advisor_name = "Financial Controller"
        else:
            advisor_name = "AI Budget Forecasting Model"

        return {
            'advice_condition': player.advice_condition,
            'advisor_name': advisor_name,
            'data': data,
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
        def format_diff(diff):
            if diff >= 0:
                return f"+CHF {diff:,}"
            else:
                return f"CHF {diff:,}"

        category = get_category_data()
        last_year_actual = category['last_year_actual']
        
        slider_min = max(0, last_year_actual - C.SLIDER_RANGE_AMOUNT)
        slider_max = last_year_actual + C.SLIDER_RANGE_AMOUNT
        
        final_budget = player.initial_forecast + player.budget_adjustment
        recommended_estimate = category['recommended_estimate']
        recommended_buffer = category['recommended_buffer']
        recommended_budget = recommended_estimate + recommended_buffer
        
        budget_diff = final_budget - recommended_budget

        # Calculate buffer percentage from initial values
        if player.initial_forecast > 0:
            initial_buffer_percent = round((player.budget_adjustment / player.initial_forecast) * 100)
        else:
            initial_buffer_percent = 0

        # Advisor name based on condition
        if player.advice_condition == 'human_expert':
            advisor_name = "Financial Controller"
        else:
            advisor_name = "AI Model"

        return {
            'category_name': category['name'],
            'category_icon': category['icon'],
            'initial_forecast': player.initial_forecast,
            'budget_adjustment': player.budget_adjustment,
            'initial_buffer_percent': initial_buffer_percent,
            'final_budget': final_budget,
            'recommended_budget': recommended_budget,
            'budget_diff_display': format_diff(budget_diff),
            'slider_min': slider_min,
            'slider_max': slider_max,
            'last_year_actual': last_year_actual,
            'advisor_name': advisor_name,
        }

    @staticmethod
    def error_message(player: Player, values):
        if values.get('resubmit_decision') == True:
            if values.get('revised_forecast') is None:
                return 'Please enter your revised forecast.'
            if values.get('revised_adjustment') is None:
                return 'Please enter your revised buffer.'


class ManipulationCheck(Page):
    template_name = 'budgeting/pages/ManipulationCheck.html'
    form_model = 'player'
    form_fields = ['manip_check_advice']
    
    @staticmethod
    def error_message(player: Player, values):
        if not values.get('manip_check_advice'):
            return 'Please answer the question about who provided the budget advice.'


class Mediators(Page):
    template_name = 'budgeting/pages/Mediators.html'
    form_model = 'player'
    form_fields = ['affective_trust_1', 'affective_trust_2', 'affective_trust_3', 'affective_trust_4', 'affective_trust_5']


class Mediators2(Page):
    template_name = 'budgeting/pages/Mediators2.html'
    form_model = 'player'
    form_fields = ['cognitive_trust_1', 'cognitive_trust_2', 'cognitive_trust_3', 'cognitive_trust_4', 'cognitive_trust_5', 'mediator_attention_check']
    
    @staticmethod
    def error_message(player: Player, values):
        if values.get('mediator_attention_check') != 6:
            return 'Please read the questions carefully and try again.'


class Controls(Page):
    template_name = 'budgeting/pages/Controls.html'
    form_model = 'player'
    form_fields = ['political_ideology', 'trust_in_government', 'trust_in_ai', 'risk_attitude', 'ai_familiarity']
    
    @staticmethod
    def error_message(player: Player, values):
        if values.get('political_ideology') is None:
            return 'Please indicate your position on the political spectrum.'
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


class Thanks(Page):
    template_name = 'budgeting/pages/Thanks.html'
    form_model = 'player'
    form_fields = ['feedback']

    @staticmethod
    def js_vars(player: Player):
        return dict(
            completionlink=player.session.config.get('completionlink', '')
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect_url='https://ccma-experiments-37b86b110ea3.herokuapp.com/room/bif_distractor'
        )


page_sequence = [
    Consent,
    Instructions,
    KnowledgeCheck,
    Context,
    ConstrualLevel,
    InitialForecast,
    AdviceFeedback,
    ResubmissionDecision,
    Mediators,
    Mediators2,
    Controls,
    ManipulationCheck,
    Demographics,
    Thanks,
]
