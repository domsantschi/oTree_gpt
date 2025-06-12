from otree.api import *
import random
import string  # Missing import for string module

doc = """
Single player variant of the investment game. The player acts as an investor
who can invest money, which gets multiplied. The return is automatically calculated.
"""

class C(BaseConstants):
    NAME_IN_URL = 'spec_design'
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
    gender = models.StringField(
        label="Gender",
        choices=["Male", "Female", "Other"],
    )
    age = models.StringField(
        label="Age",
        choices=[
            "Less than 25 years old",
            "25-34 years old",
            "35-44 years old",
            "45-54 years old",
            "55-64 years old",
            "65-74 years old",
            "Above 74 years old",
        ],
    )
    qualification = models.StringField(
        label="Highest Level of Education",
        choices=[
            "Diploma",
            "Bachelor Degree",
            "Masters Degree",
            "Doctoral Degree",
            "None of the above",
        ],
    )
    work_experience = models.IntegerField(
        label="Years of Full-Time Work Experience",
        min=0,
    )
    management_experience = models.IntegerField(
        label="Years of Management Experience",
        min=0,
    )
    time_horizon = models.StringField(
        label="Time Horizon",
        choices=["Short-term risks", "Long-term risks"],
    )
    speculative_design = models.StringField(
        label="Speculative Design",
        choices=["Speculative Design Absent", "Speculative Design Present"],
    )
    condition = models.StringField(
        label="Time Horizon",
        choices=["Short-term risks", "Long-term risks"],
    )
    risk_event_1 = models.IntegerField(
        label="Risk Event 1 Allocation",
        min=0,
        initial=0
    )
    risk_event_2 = models.IntegerField(
        label="Risk Event 2 Allocation",
        min=0,
        initial=0
    )
    risk_event_3 = models.IntegerField(
        label="Risk Event 3 Allocation",
        min=0,
        initial=0
    )
    risk_event_4 = models.IntegerField(
        label="Risk Event 4 Allocation",
        min=0,
        initial=0
    )
    feedback = models.LongStringField(
        label="Any feedback about the study?",
        blank=True
    )
    blind_spot_detection = models.IntegerField(
        label="Risk Identification",
        min=1,
        max=7,
        doc="To what extent did the speculative design artifact help identify risks"
    )
    narrative_accessibility = models.IntegerField(
        label="Narrative Accessibility",
        min=1,
        max=7,
        doc="To what extent did the artifact make the risk scenario easier to understand"
    )
    risk_embodiment = models.IntegerField(
        label="Risk Embodiment",
        min=1,
        max=7,
        doc="To what extent did the artifact make abstract risks feel more concrete"
    )

# --- Functions ----------------------------------------------------------------

# Function for testing

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        conditions = ['Short-term risks', 'Long-term risks']
        speculative_design_conditions = ['Speculative Design Absent', 'Speculative Design Present']
        
        # Ensure each condition is assigned once across four sessions
        combined_conditions = [
            (c, sc) for c in conditions for sc in speculative_design_conditions
        ]
        random.shuffle(combined_conditions)

        for i, p in enumerate(subsession.get_players()):
            p.participant.wealth = cu(0)
            p.participant.part_id = create_id()
            condition, speculative_design = combined_conditions[i % len(combined_conditions)]
            p.condition = condition
            p.speculative_design = speculative_design

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

class Assessment(Page):
    form_model = 'player'
    form_fields = [
        'risk_event_1',
        'risk_event_2',
        'risk_event_3',
        'risk_event_4',
    ]

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Calculate total allocation
        total_allocation = (
            player.risk_event_1 +
            player.risk_event_2 +
            player.risk_event_3 +
            player.risk_event_4
        )
        print(f"Total allocation: {total_allocation}")
        # Ensure total allocation does not exceed 100,000
        if total_allocation > 100000:
            raise ValueError("Total allocation exceeds the budget of 100,000 dollars.")

class Condition2(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            condition=player.condition,
            speculative_design=player.speculative_design,  # Pass speculative_design to the template
        )

class Controls(Page):
    form_model = 'player'
    form_fields = [
        'blind_spot_detection',
        'narrative_accessibility',
        'risk_embodiment',
    ]

class Checks(Page):
    form_model = 'player'
    form_fields = [
        'time_horizon',
        'speculative_design',
    ]

class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'gender',
        'age',
        'qualification',
        'work_experience',
        'management_experience',
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

# Update the page sequence
page_sequence = [
    Welcome,
    Introduction,
    Background,
    Condition1,
    Condition2,
    Assessment,
    Checks,
    Controls,
    Demographics,
    Thanks,
]