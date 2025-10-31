from otree.api import *
import random
import string  # Missing import for string module
import time  # Import time module for tracking time spent on pages

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
    
    prolific_id = models.StringField(default=str(" "))
    
    gender = models.StringField(
        label="Gender",
        choices=["Male", "Female", "Other"],
    )
    age = models.StringField(
        label="Age",
        choices=[
            "18-24 years",
            "25-34 years",
            "35-50 years",
            "51-65 years",
            "Over 65 years",
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
    rm_experience = models.IntegerField(
        label="Years of Risk Management Experience",
        min=0,
    )
    english_native = models.StringField(
        label="Is English your native language?",
        choices=["Yes", "No"],
    )
    
    # Experimental conditions
    construal_level = models.StringField(
        label="Construal Level",
        choices=["Concrete Construal", "Abstract Construal"],
    )
    speculative_design = models.StringField(
        label="Speculative Design",
        choices=["Speculative Design Absent", "Speculative Design Present"],
    )
    
    # Behavior Identification Form (BIF) - Vallacher & Wegner (1989)
    bif_score = models.IntegerField(
        initial=0,
        doc="Total BIF score (0-25): number of abstract responses chosen"
    )
    bif_responses = models.LongStringField(
        blank=True,
        doc="JSON string containing individual BIF responses (0=concrete, 1=abstract)"
    )
    
    # Text responses for construal level manipulation
    construal_response = models.LongStringField(
        label="Your response",
        blank=False,
    )
    feedback = models.LongStringField(
        label="Any feedback about the study?",
        blank=True
    )
    
    # Screening questions
    screening_q1 = models.StringField(
        label="In new product development, what does the 'preparation phase' typically involve?",
        choices=[
            "Planning, research, and initial design activities before product launch",
            "Market launch and sales activities",
            "Post-market surveillance and feedback collection",
            "End-of-life product retirement",
        ],
        widget=widgets.RadioSelect,
    )
    
    screening_q2 = models.StringField(
        label="What is 'risk anticipation' in the context of product development?",
        choices=[
            "Waiting for problems to occur before addressing them",
            "Proactively identifying potential issues before they materialize",
            "Documenting risks after product failure",
            "Ignoring potential problems to save time",
        ],
        widget=widgets.RadioSelect,
    )
    
    screening_q3 = models.StringField(
        label="When developing a food innovation, what type of risks should be considered?",
        choices=[
            "Only financial and regulatory risks",
            "Only technical and operational risks",
            "Multiple types including ethical, safety, regulatory, and social risks",
            "Only patient safety risks",
        ],
        widget=widgets.RadioSelect,
    )
    
    # Track screening result
    passed_screening = models.BooleanField(initial=True)
    
    # Track consent decision
    declined_consent = models.BooleanField(initial=False)
    
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
    
    # Manipulation effort questions
    manipulation_effort = models.IntegerField(
        label="How much effort did it take to complete the manipulation task?",
        min=1,
        max=7,
        doc="Effort required to complete manipulation task: 1=Extremely effortless, 7=Extremely effortful"
    )
    manipulation_difficulty = models.IntegerField(
        label="How difficult was it to complete the manipulation task?",
        min=1,
        max=7,
        doc="Difficulty of manipulation task: 1=Extremely easy, 7=Extremely difficult"
    )
    
    # Risk willingness questions (for Checks page)
    risk_taking = models.IntegerField(
        label="Willingness to undertake risky business propositions",
        min=1,
        max=7,
        doc="Self-rated willingness to undertake risky business propositions compared to others"
    )
    risk_avoidance = models.IntegerField(
        label="Willingness to avoid risky business propositions (reverse scaled)",
        min=1,
        max=7,
        doc="Self-rated willingness to avoid risky business propositions compared to others"
    )
    
    # Willingness to pay questions (immediate vs distant)
    wtp_pizza_immediate = models.FloatField(
        label="WTP for pizza meal (immediate)",
        min=0,
        doc="Willingness to pay for pizza meal at restaurant today"
    )
    wtp_pizza_distant = models.FloatField(
        label="WTP for pizza meal (distant)",
        min=0,
        doc="Willingness to pay for pizza meal at restaurant in 6 months"
    )
    wtp_genai_immediate = models.FloatField(
        label="WTP for Gen-AI subscription (immediate)",
        min=0,
        doc="Willingness to pay for monthly Gen-AI subscription today"
    )
    wtp_genai_distant = models.FloatField(
        label="WTP for Gen-AI subscription (distant)",
        min=0,
        doc="Willingness to pay for monthly Gen-AI subscription in 6 months"
    )
    wtp_movie_immediate = models.FloatField(
        label="WTP for movie at cinema (immediate)",
        min=0,
        doc="Willingness to pay for movie at cinema today"
    )
    wtp_movie_distant = models.FloatField(
        label="WTP for movie at cinema (distant)",
        min=0,
        doc="Willingness to pay for movie at cinema in 6 months"
    )
    wtp_book_immediate = models.FloatField(
        label="WTP for book at bookstore (immediate)",
        min=0,
        doc="Willingness to pay for book at bookstore today"
    )
    wtp_book_distant = models.FloatField(
        label="WTP for book at bookstore (distant)",
        min=0,
        doc="Willingness to pay for book at bookstore in 6 months"
    )
    
    # Expected payment for services (immediate vs distant)
    exp_driving_immediate = models.FloatField(
        label="Expected payment for driving (immediate)",
        min=0,
        doc="Expected payment for driving a stranger to a restaurant today"
    )
    exp_driving_distant = models.FloatField(
        label="Expected payment for driving (distant)",
        min=0,
        doc="Expected payment for driving a stranger to a restaurant in 6 months"
    )
    exp_email_immediate = models.FloatField(
        label="Expected payment for email review (immediate)",
        min=0,
        doc="Expected payment for reviewing a stranger's email today"
    )
    exp_email_distant = models.FloatField(
        label="Expected payment for email review (distant)",
        min=0,
        doc="Expected payment for reviewing a stranger's email in 6 months"
    )
    exp_lending_immediate = models.FloatField(
        label="Expected payment for lending (immediate)",
        min=0,
        doc="Expected payment for borrowing a stranger USD 10 today"
    )
    exp_lending_distant = models.FloatField(
        label="Expected payment for lending (distant)",
        min=0,
        doc="Expected payment for borrowing a stranger USD 10 in 6 months"
    )
    exp_book_immediate = models.FloatField(
        label="Expected payment for book suggestion (immediate)",
        min=0,
        doc="Expected payment for suggesting a book to a stranger today"
    )
    exp_book_distant = models.FloatField(
        label="Expected payment for book suggestion (distant)",
        min=0,
        doc="Expected payment for suggesting a book to a stranger in 6 months"
    )
    
    # PANAS Scale - 20 items measuring positive and negative affect
    panas_interested = models.IntegerField(label="Interested", min=1, max=5)
    panas_distressed = models.IntegerField(label="Distressed", min=1, max=5)
    panas_excited = models.IntegerField(label="Excited", min=1, max=5)
    panas_upset = models.IntegerField(label="Upset", min=1, max=5)
    panas_strong = models.IntegerField(label="Strong", min=1, max=5)
    panas_guilty = models.IntegerField(label="Guilty", min=1, max=5)
    panas_scared = models.IntegerField(label="Scared", min=1, max=5)
    panas_hostile = models.IntegerField(label="Hostile", min=1, max=5)
    panas_enthusiastic = models.IntegerField(label="Enthusiastic", min=1, max=5)
    panas_proud = models.IntegerField(label="Proud", min=1, max=5)
    panas_irritable = models.IntegerField(label="Irritable", min=1, max=5)
    panas_alert = models.IntegerField(label="Alert", min=1, max=5)
    panas_ashamed = models.IntegerField(label="Ashamed", min=1, max=5)
    panas_inspired = models.IntegerField(label="Inspired", min=1, max=5)
    panas_nervous = models.IntegerField(label="Nervous", min=1, max=5)
    panas_determined = models.IntegerField(label="Determined", min=1, max=5)
    panas_attentive = models.IntegerField(label="Attentive", min=1, max=5)
    panas_jittery = models.IntegerField(label="Jittery", min=1, max=5)
    panas_active = models.IntegerField(label="Active", min=1, max=5)
    panas_afraid = models.IntegerField(label="Afraid", min=1, max=5)
    # Risk identification - count and descriptions
    risk_count = models.IntegerField(
        initial=0,
        doc="Total number of risks identified by participant"
    )
    risk_descriptions = models.LongStringField(
        blank=True,
        doc="JSON string containing all risk descriptions"
    )

    # Page timing fields
    consent_page_time = models.FloatField(doc="Time spent on consent page in seconds")
    introduction_page_time = models.FloatField(doc="Time spent on introduction page in seconds")
    background_page_time = models.FloatField(doc="Time spent on background page in seconds")
    condition1_page_time = models.FloatField(doc="Time spent on condition 1 page in seconds")
    condition2_page_time = models.FloatField(doc="Time spent on condition 2 page in seconds")
    assessment_page_time = models.FloatField(doc="Time spent on assessment page in seconds")
    bif_page_time = models.FloatField(doc="Time spent on BIF page in seconds")
    checks_page_time = models.FloatField(doc="Time spent on checks page in seconds")
    panas_page_time = models.FloatField(doc="Time spent on PANAS page in seconds")
    controls_page_time = models.FloatField(doc="Time spent on controls page in seconds")
    demographics_page_time = models.FloatField(doc="Time spent on demographics page in seconds")
    thanks_page_time = models.FloatField(doc="Time spent on thanks page in seconds")

# --- Functions ----------------------------------------------------------------

# Function for testing

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        construal_conditions = ['Concrete Construal', 'Abstract Construal']
        speculative_design_conditions = ['Speculative Design Absent', 'Speculative Design Present']
        
        # Ensure each condition is assigned once across four sessions
        combined_conditions = [
            (c, sc) for c in construal_conditions for sc in speculative_design_conditions
        ]
        random.shuffle(combined_conditions)

        for i, p in enumerate(subsession.get_players()):
            p.participant.wealth = cu(0)
            p.participant.part_id = create_id()
            construal_level, speculative_design = combined_conditions[i % len(combined_conditions)]
            p.construal_level = construal_level
            p.speculative_design = speculative_design
            print(f"Player {i+1} assigned: Construal Level = {construal_level}, Speculative Design = {speculative_design}")

# --- Pages --------------------------------------------------------------------

class Consent(Page):
    form_model = 'player'
    form_fields = ['declined_consent']
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        import time
        player.consent_page_time = time.time() - player.participant._start_time
        
        # Log consent decision
        if player.declined_consent:
            print(f"Participant {player.participant.label}: Declined consent")
        else:
            print(f"Participant {player.participant.label}: Accepted consent")

class Screening(Page):
    form_model = 'player'
    form_fields = ['screening_q1', 'screening_q2', 'screening_q3']
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Correct answers
        correct_answers = {
            'screening_q1': 'Planning, research, and initial design activities before product launch',
            'screening_q2': 'Proactively identifying potential issues before they materialize',
            'screening_q3': 'Multiple types including ethical, safety, regulatory, and social risks',
        }
        
        # Check if all answers are correct
        all_correct = (
            player.screening_q1 == correct_answers['screening_q1'] and
            player.screening_q2 == correct_answers['screening_q2'] and
            player.screening_q3 == correct_answers['screening_q3']
        )
        
        player.passed_screening = all_correct
        
        # Debug print
        print(f"Participant {player.participant.label}: Screening result = {all_correct}")

class ScreenedOut(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Only show this page if participant failed screening
        return not player.passed_screening
    
    @staticmethod
    def js_vars(player):
        # Return the Prolific rejection URL
        return dict(
            rejection_url='https://app.prolific.com/submissions/complete?cc=C1ANUFSO'
        )

class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Only show this page if participant passed screening
        return player.passed_screening
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        import time
        player.introduction_page_time = time.time() - player.participant._start_time
    
    @staticmethod
    def before_next_page(self, timeout_happened):
        self.prolific_id = self.participant.label
pass

class Background(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.background_page_time = time.time() - player.participant._start_time

class CLT_Condition(Page):
    form_model = 'player'
    form_fields = ['construal_response']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            construal_level=player.construal_level
        )
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.condition1_page_time = time.time() - player.participant._start_time
        # Log the construal response
        print(f"Participant {player.participant.label}: Construal response = {player.construal_response}")

class Assessment(Page):
    form_model = 'player'
    form_fields = ['risk_count', 'risk_descriptions']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening

    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Save timing
        player.assessment_page_time = time.time() - player.participant._start_time
        # Log the number of risks identified
        print(f"Participant {player.participant.label}: Identified {player.risk_count} risks")

class Spec_Condition(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            speculative_design=player.speculative_design,
        )
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.condition2_page_time = time.time() - player.participant._start_time

class Controls(Page):
    form_model = 'player'
    form_fields = [
        'blind_spot_detection',
        'narrative_accessibility',
        'risk_embodiment',
        'manipulation_effort',
        'manipulation_difficulty',
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening

    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None
 
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.controls_page_time = time.time() - player.participant._start_time

class BIF(Page):
    form_model = 'player'
    form_fields = ['bif_score', 'bif_responses']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.bif_page_time = time.time() - player.participant._start_time
        # Log BIF score
        print(f"Participant {player.participant.label}: BIF score = {player.bif_score}/10")

class Checks(Page):
    form_model = 'player'
    form_fields = [
        'risk_taking', 
        'risk_avoidance',
        'wtp_pizza_immediate',
        'wtp_pizza_distant',
        'wtp_genai_immediate',
        'wtp_genai_distant',
        'wtp_movie_immediate',
        'wtp_movie_distant',
        'wtp_book_immediate',
        'wtp_book_distant',
        'exp_driving_immediate',
        'exp_driving_distant',
        'exp_email_immediate',
        'exp_email_distant',
        'exp_lending_immediate',
        'exp_lending_distant',
        'exp_book_immediate',
        'exp_book_distant'
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.checks_page_time = time.time() - player.participant._start_time

class PANAS(Page):
    form_model = 'player'
    form_fields = [
        'panas_inspired',
        'panas_alert',
        'panas_excited',
        'panas_enthusiastic',
        'panas_determined',
        'panas_afraid',
        'panas_upset',
        'panas_nervous',
        'panas_scared',
        'panas_distressed'
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.panas_page_time = time.time() - player.participant._start_time

class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'gender',
        'age',
        'qualification',
        'work_experience',
        'rm_experience',
        'english_native',
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.demographics_page_time = time.time() - player.participant._start_time

class Thanks(Page):
    form_model = 'player'
    form_fields = ['feedback']  # Capture feedback in the database
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            participant_id=player.participant.part_id
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Save timing
        player.thanks_page_time = time.time() - player.participant._start_time
        # Save feedback to the database
        feedback = player.feedback
        if feedback:
            print(f"Feedback received: {feedback}")
    
    @staticmethod              
    def js_vars(player):
        return dict(
            completionlink=
              player.subsession.session.config['completionlink']
        )
    pass

class Redirect(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    pass

# Update the page sequence
page_sequence = [
    Consent,
    Screening,
    ScreenedOut,
    Introduction,
    Background,
    Spec_Condition,
    CLT_Condition,
    Assessment,
    Controls, 
    BIF,
    Checks,
    PANAS,
    Demographics,
    Thanks,
    Redirect
]