import string
import random
from otree.api import *

doc = """
Single player variant of the investment game. The player acts as an investor
who can invest money, which gets multiplied. The return is automatically calculated.
"""

class C(BaseConstants):
    NAME_IN_URL = 'stakeholder'
    PLAYERS_PER_GROUP = None  # Single-player game
    NUM_ROUNDS = 1
    ENDOWMENT = cu(100)
    MULTIPLIER = 1
    RETURN_RATE = 0.5  # 50% of the multiplied amount is returned

def create_id():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    id_public = ''.join(random.choices(chars, k=4))
    id_private = ''.join(random.choices(chars, k=4))
    return "{} {}".format(id_public, id_private)

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    sent_amount = models.CurrencyField(
        min=cu(0),
        max=C.ENDOWMENT,
        doc="""Amount to invest:""",
        label="Please enter an amount from 0 to 100:",
    )
    returned_amount = models.CurrencyField()  # Automatically calculated

class Player(BasePlayer):
    # Field to store whether checks come before assessment
    checks_before_assessment = models.BooleanField(initial=None)
    
    # Add the missing 'stakeholder_consensus' field
    stakeholder_consensus = models.StringField(
        label="Stakeholder Consensus",
        choices=["Low Stakeholder Consensus", "High Stakeholder Consensus"],
    )    # Existing fields
    condition = models.StringField(
        label="Condition assigned to the player",
        choices=["Low Stakeholder Relevance", "High Stakeholder Relevance"],
    )
    
    # Fields to store user inputs
    predicted_price = models.FloatField(
        label="Your target price prediction",
        min=0.00,
        max=100.00
    )
    justifications = models.LongStringField(
        label="Please provide your written justifications for your assessment."
    )
    
    # Fields for Controls
    risk_attitudes = models.IntegerField(
        label="Are you generally a person who is willing to take risks or do you try to avoid taking risks?",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
    )
    
    esg_familiarity = models.IntegerField(
        label="What is your level of familiarity with ESG Disclosures?",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
    )
    
    disclosure_credibility = models.IntegerField(
        label="How do you assess the credibility of Acme's Disclosures?",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
    )
    esg_relevance = models.IntegerField(
        label="How strongly do you personally agree that companies should sacrifice profitability to promote ESG themes?",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
    )

    # Single-choice questions
    stakeholder_attributes = models.StringField(
        label="Which of the following describes the relevance of the stakeholders consulted for the ESG prioritization initiative?",
        choices=[
            "Low power, legitimacy, and urgency",
            "High power, legitimacy, and urgency",
        ],
        widget=widgets.RadioSelect,
    )
    trendline = models.StringField(
        label="Which of the following describes the trendline of the stakeholder consensus depicted in Acme's ESG theme prioritization chart?",
        choices=[
            "Low correlation",
            "High correlation",
        ],
        widget=widgets.RadioSelect,
    )

    # Add these fields to the Player class:
    internal_stakeholders_responses = models.StringField(
        label="Internal stakeholders selections",
        blank=True
    )
    external_stakeholders_responses = models.StringField(
        label="External stakeholders selections", 
        blank=True
    )
    internal_stakeholders_other_text = models.StringField(
        label="If other internal stakeholder, please explain:",
        blank=True
    )
    external_stakeholders_other_text = models.StringField(
        label="If other external stakeholder, please explain:",
        blank=True
    )
    
    age = models.StringField(
        label="What is your age?",
        choices=[
            "Less than 18 years old",
            "18-24 years old",
            "25-34 years old",
            "35-50 years old",
            "51-65 years old",
            "Above 65 years old",
        ],
        widget=widgets.RadioSelect,
    )
    gender = models.StringField(
        label="What is your gender?",
        choices=["Male", "Female", "Prefer not to say"],
        widget=widgets.RadioSelect,
    )
    qualification = models.StringField(
        label="Please select the highest academic qualification that you have.",
        choices=[
            "Diploma",
            "Bachelor Degree",
            "Masters Degree",
            "Doctoral Degree",
            "None of the above",
        ],
        widget=widgets.RadioSelect,
    )
    finance_experience = models.IntegerField(
        label="How many years of full-time working experience in a financial analyst role do you have?",
        min=0,
    )
    investment_research = models.StringField(
        label="How involved are you with investment research?",
        choices=[
            "Not at all",
            "Very little",
            "Not much",
            "Neutral",
            "Somewhat",
            "Quite a bit",
            "A lot",
        ],
        widget=widgets.RadioSelectHorizontal,  # Use horizontal layout for Likert scale
    )
    risk_assessments = models.StringField(
        label="How involved are you with risk assessments?",
        choices=[
            "Not at all",
            "Very little",
            "Not much",
            "Neutral",
            "Somewhat",
            "Quite a bit",
            "A lot",
        ],
        widget=widgets.RadioSelectHorizontal,  # Use horizontal layout for Likert scale
    )

    # New field to store feedback
    feedback = models.LongStringField(
        label="Participant feedback",
        blank=True,  # Optional field
    )

# --- Functions ----------------------------------------------------------------

# Function for testing

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        conditions = ['Low Stakeholder Relevance', 'High Stakeholder Relevance']
        stakeholder_consensus_conditions = ['Low Stakeholder Consensus', 'High Stakeholder Consensus']
        
        # Create all combinations of conditions
        combined_conditions = []
        for c in conditions:
            for sc in stakeholder_consensus_conditions:
                combined_conditions.append((c, sc))
        
        # Shuffle the conditions
        random.shuffle(combined_conditions)
        
        for i, p in enumerate(subsession.get_players()):
            p.participant.wealth = cu(0)
            p.participant.part_id = create_id()
            
            # Assign conditions
            condition, stakeholder_consensus = combined_conditions[i % len(combined_conditions)]
            p.condition = condition
            p.stakeholder_consensus = stakeholder_consensus
            
            # Randomly determine if checks come before or after assessment
            p.checks_before_assessment = random.choice([True, False])


# # Function for live experiment << random assignment
# def creating_session(subsession: Subsession):
#     if subsession.round_number == 1:
#         for p in subsession.get_players():
#             p.participant.wealth = cu(0)
#             p.participant.part_id = create_id()
#             # Randomly assign a condition
#             p.condition = random.choice(['Low Stakeholder Relevance', 'High Stakeholder Relevance'])
#             # Randomly assign Stakeholder Consensus (Condition 3 or 4)
#             p.stakeholder_consensus = random.choice(['Negative Stakeholder Consensus', 'Positive Stakeholder Consensus'])

## Not needed for single player game

# def set_payoffs(group: Group):
#     player = group.get_player_by_id(1)
#     multiplied_amount = group.sent_amount * C.MULTIPLIER
#     group.returned_amount = multiplied_amount * C.RETURN_RATE
#     player.payoff = C.ENDOWMENT - group.sent_amount + group.returned_amount
#     player.participant.wealth += player.payoff

# --- Pages --------------------------------------------------------------------

class Welcome(Page):
    pass

class Introduction(Page):
    pass

class Background(Page):
    pass

class Condition1(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            condition=player.condition
        )

class Condition2(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            condition=player.condition,
            stakeholder_consensus=player.stakeholder_consensus,  # Pass stakeholder_consensus to the template
        )

class Assessment(Page):
    form_model = 'player'
    form_fields = [
        'predicted_price',
        'justifications',
    ]

class Checks(Page):
    form_model = 'player'
    form_fields = [
        'stakeholder_attributes',
        'trendline',
    ]
            
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Process the internal stakeholders string
        if player.internal_stakeholders_responses:
            # Parse the string of T/F values to determine which options were selected
            options = ["Investors", "Suppliers", "Customers", "Regulators", 
                      "NGOs", "Community", "Media", "Other"]
            
            selected = []
            for i, char in enumerate(player.internal_stakeholders_responses):
                if char == 'T' and i < len(options):
                    selected.append(options[i])
            
            # If "Other" was selected, add the text response
            if "Other" in selected and player.internal_stakeholders_other_text:
                selected[-1] = f"Other: {player.internal_stakeholders_other_text}"
            
            print(f"Internal stakeholders selected: {', '.join(selected)}")
        
        # Process the external stakeholders string
        if player.external_stakeholders_responses:
            # Parse the string of T/F values to determine which options were selected
            options = ["Employees", "Executive Management", "Board of Directors", 
                      "Chairman", "CEO", "Other"]
            
            selected = []
            for i, char in enumerate(player.external_stakeholders_responses):
                if char == 'T' and i < len(options):
                    selected.append(options[i])
            
            # If "Other" was selected, add the text response
            if "Other" in selected and player.external_stakeholders_other_text:
                selected[-1] = f"Other: {player.external_stakeholders_other_text}"
            
            print(f"External stakeholders selected: {', '.join(selected)}")

class StakeholderSelection(Page):
    form_model = 'player'
    form_fields = [
        'internal_stakeholders_responses',
        'external_stakeholders_responses',
        'internal_stakeholders_other_text',
        'external_stakeholders_other_text'
    ]
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Process the internal stakeholders string
        if player.field_maybe_none('internal_stakeholders_responses'):
            options = ["Investors", "Suppliers", "Customers", "Regulators", 
                      "NGOs", "Community", "Media", "Other"]
            
            selected = []
            for i, char in enumerate(player.internal_stakeholders_responses):
                if char == 'T' and i < len(options):
                    selected.append(options[i])
            
            if "Other" in selected and player.field_maybe_none('internal_stakeholders_other_text'):
                selected[-1] = f"Other: {player.internal_stakeholders_other_text}"
            
            print(f"Internal stakeholders selected: {', '.join(selected)}")
        
        # Process the external stakeholders string
        if player.field_maybe_none('external_stakeholders_responses'):
            options = ["Employees", "Executive Management", "Board of Directors", 
                      "Chairman", "CEO", "Other"]
            
            selected = []
            for i, char in enumerate(player.external_stakeholders_responses):
                if char == 'T' and i < len(options):
                    selected.append(options[i])
            
            if "Other" in selected and player.field_maybe_none('external_stakeholders_other_text'):
                selected[-1] = f"Other: {player.external_stakeholders_other_text}"
            
            print(f"External stakeholders selected: {', '.join(selected)}")

class Controls(Page):
    form_model = 'player'
    form_fields = [
        'risk_attitudes',
        'esg_familiarity', 
        'disclosure_credibility',
        'esg_relevance'
    ]

class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'age',
        'gender',
        'qualification',
        'finance_experience',
        'investment_research',
        'risk_assessments',
    ]

class Thanks(Page):
    form_model = 'player'
    form_fields = ['feedback']  # Capture feedback in the database

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            participant_id=player.participant.part_id
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Save feedback to the database
        feedback = player.feedback
        if feedback:
            print(f"Feedback received: {feedback}")

# Create two separate classes for the two versions of both Assessment and Checks

class ChecksBefore(Page):
    form_model = 'player'
    form_fields = [
        'stakeholder_attributes',
        'trendline',
    ]
    
    @staticmethod
    def is_displayed(player):
        return player.checks_before_assessment
        
    def get_template_name(self):
        return 'stakeholder/Checks.html'

class ChecksAfter(Page):
    form_model = 'player'
    form_fields = [
        'stakeholder_attributes',
        'trendline',
    ]
    
    @staticmethod
    def is_displayed(player):
        return not player.checks_before_assessment
        
    def get_template_name(self):
        return 'stakeholder/Checks.html'

class AssessmentBefore(Page):
    form_model = 'player'
    form_fields = [
        'predicted_price',
        'justifications',
    ]
    
    @staticmethod
    def is_displayed(player):
        return not player.checks_before_assessment
        
    def get_template_name(self):
        return 'stakeholder/Assessment.html'

class AssessmentAfter(Page):
    form_model = 'player'
    form_fields = [
        'predicted_price',
        'justifications',
    ]
    
    @staticmethod
    def is_displayed(player):
        return player.checks_before_assessment
        
    def get_template_name(self):
        return 'stakeholder/Assessment.html'

# Define the page sequence with both possible paths explicitly included
page_sequence = [
    Welcome,
    Introduction,
    Background,
    Condition1,
    Condition2,
    # Path 1: Checks before Assessment (only one path will be shown)
    ChecksBefore,      # Only shown if checks_before_assessment is True
    AssessmentAfter,   # Only shown if checks_before_assessment is True
    # Path 2: Assessment before Checks (only one path will be shown)
    AssessmentBefore,  # Only shown if checks_before_assessment is False
    ChecksAfter,       # Only shown if checks_before_assessment is False
    # Continue with normal flow
    StakeholderSelection,
    Controls,
    Demographics,
    Thanks,
]