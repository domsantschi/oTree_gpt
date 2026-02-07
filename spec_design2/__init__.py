from otree.api import *
import random
import string  # Missing import for string module
import time  # Import time module for tracking time spent on pages

doc = """
Single player variant of the investment game. The player acts as an investor
who can invest money, which gets multiplied. The return is automatically calculated.
"""

class C(BaseConstants):
    NAME_IN_URL = 'spec_design2'
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
    budgeting_participant_code = models.StringField(
        blank=True,
        doc="Participant code from the budgeting study to link sessions"
    )
    
    gender = models.StringField(
        label="Gender",
        choices=["Male", "Female", "Other", "Prefer not to say"],
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
            "High School / Baccalauréat",
            "Bachelor's Degree",
            "Master's Degree",
            "Doctoral Degree (PhD)",
            "Other",
        ],
    )
    work_experience = models.IntegerField(
        label="Years of Full-Time Work Experience (Total)",
        min=0,
        doc="Total years of full-time work experience"
    )
    rm_experience = models.IntegerField(
        label="Years of Risk Management Experience",
        min=0,
        doc="Years of work experience specifically in risk management"
    )
    industry_experience = models.IntegerField(
        label="Years of experience in insurance, risk management, or technology/AI",
        min=0,
        doc="Years of full-time work experience in insurance, risk management, or technology/AI industry"
    )
    familiarity_insurance = models.IntegerField(
        label="I am familiar with insurance",
        min=1,
        max=7,
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal,
        doc="Level of familiarity with insurance"
    )
    familiarity_ai = models.IntegerField(
        label="I am familiar with artificial intelligence (AI)",
        min=1,
        max=7,
        choices=[[1, '1 - Strongly disagree'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7 - Strongly agree']],
        widget=widgets.RadioSelectHorizontal,
        doc="Level of familiarity with artificial intelligence"
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
    
    # Manipulation checks
    specdesign_check = models.StringField(
        label="Did you get access to a speculative What If scenario with images during the study?",
        choices=["Speculative Design Absent", "Speculative Design Present"],
        doc="Manipulation check for speculative design condition"
    )
    construal_check = models.StringField(
        label="Which task did you pursue?",
        choices=["Concrete Construal", "Abstract Construal"],
        doc="Manipulation check for construal level condition"
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
    prize_email = models.StringField(
        label="Email address for prize consideration",
        blank=True,
        doc="Email address for participants who want to be considered for the CHF 50 bonus prize"
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
        label="What is 'risk identification' in the context of product development?",
        choices=[
            "Waiting for problems to occur before addressing them",
            "Proactively identifying potential issues before they materialize",
            "Documenting risks after product failure",
            "Ignoring potential problems to save time",
        ],
        widget=widgets.RadioSelect,
    )
    
    screening_q3 = models.StringField(
        label="When developing an AI-related insurance product, what type of risks should be considered?",
        choices=[
            "Only financial and regulatory risks",
            "Only technical and operational risks",
            "Multiple types including ethical, safety, regulatory, and social risks",
            "Only customer safety risks",
        ],
        widget=widgets.RadioSelect,
    )
    
    # Track screening result
    passed_screening = models.BooleanField(initial=True)
    
    # Track consent decision
    declined_consent = models.BooleanField(initial=False)
    
    # Mediators - Information Perspective
    creative_thinking = models.IntegerField(
        label="Creative thinking about risks",
        min=1,
        max=7,
        doc="The information helped me think more creatively about potential risks"
    )
    imagination = models.IntegerField(
        label="Imagination of possibilities",
        min=1,
        max=7,
        doc="The information encouraged me to imagine possibilities I wouldn't have thought of otherwise"
    )
    broader_implications = models.IntegerField(
        label="Broader implications consideration",
        min=1,
        max=7,
        doc="The information helped me consider broader implications beyond immediate effects"
    )
    
    # Mediators - Information Format
    story_format = models.IntegerField(
        label="Story format effectiveness",
        min=1,
        max=7,
        doc="The story-like format made the risks easier to identify"
    )
    real_world_relatable = models.IntegerField(
        label="Real-world relatability",
        min=1,
        max=7,
        doc="The narrative made the risks more relatable to real-world situations"
    )
    processing_effectiveness = models.IntegerField(
        label="Information processing effectiveness",
        min=1,
        max=7,
        doc="The scenario helped me process information related to potential risks more effectively"
    )
    
    # Mediators - Speculative Design Impact
    scenario_creativity = models.IntegerField(
        label="Scenario augmented creativity",
        min=1,
        max=7,
        doc="The what-if scenario augmented my creativity to identify risks"
    )
    risk_accessibility = models.IntegerField(
        label="Risk accessibility",
        min=1,
        max=7,
        doc="The what-if scenario made the risks of the product innovation more accessible"
    )
    risk_tangibility = models.IntegerField(
        label="Risk tangibility",
        min=1,
        max=7,
        doc="The what-if scenario made the risks of the new product innovation more tangible"
    )
    
    mediator_attention_check = models.IntegerField(
        label="To show you are reading carefully, please select 'Agree' for this item.",
        min=1,
        max=7,
        choices=[
            [1, 'Strongly disagree'],
            [2, 'Disagree'],
            [3, 'Somewhat disagree'],
            [4, 'Neutral'],
            [5, 'Somewhat agree'],
            [6, 'Agree'],
            [7, 'Strongly agree']
        ],
        doc="Attention check for mediators section"
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
    
    creativity = models.IntegerField(
        label="Self-rated creativity level",
        min=1,
        max=7,
        doc="Self-rated level of creativity compared to others"
    )
    
    attention_check = models.IntegerField(
        label="To demonstrate that you are paying attention, please select 'Agree' for this question.",
        min=1,
        max=7,
        choices=[
            [1, 'Strongly disagree'],
            [2, 'Disagree'],
            [3, 'Somewhat disagree'],
            [4, 'Neutral'],
            [5, 'Somewhat agree'],
            [6, 'Agree'],
            [7, 'Strongly agree']
        ],
        doc="Attention check question"
    )
    
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
    screening_page_time = models.FloatField(doc="Time spent on screening page in seconds")
    introduction_page_time = models.FloatField(doc="Time spent on introduction page in seconds")
    background_page_time = models.FloatField(doc="Time spent on background page in seconds")
    clt_condition_page_time = models.FloatField(doc="Time spent on construal level condition page in seconds")
    spec_condition_page_time = models.FloatField(doc="Time spent on speculative design condition page in seconds")
    assessment_page_time = models.FloatField(doc="Time spent on assessment page in seconds")
    mediators_page_time = models.FloatField(doc="Time spent on mediators page in seconds")
    controls_page_time = models.FloatField(doc="Time spent on controls page in seconds")
    characteristics_page_time = models.FloatField(doc="Time spent on characteristics page in seconds")
    manip_check_page_time = models.FloatField(doc="Time spent on manipulation check page in seconds")
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
            
            # Check if participant came from budgeting study and save linking code
            if 'budgeting_participant_code' in p.participant.vars:
                p.budgeting_participant_code = p.participant.vars['budgeting_participant_code']
                print(f"Player {i+1} linked to budgeting participant: {p.budgeting_participant_code}")
            
            # Check if construal level was already assigned in budgeting study
            if 'construal_level' in p.participant.vars:
                # Map from budgeting format to spec_design2 format
                budgeting_construal = p.participant.vars['construal_level']
                if budgeting_construal == 'concrete':
                    construal_level = 'Concrete Construal'
                else:  # 'abstract'
                    construal_level = 'Abstract Construal'
                # Still randomly assign speculative design
                speculative_design = random.choice(speculative_design_conditions)
            else:
                # If no prior assignment, randomly assign both conditions
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
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None
    
    @staticmethod
    def error_message(player: Player, values):
        # Correct answers
        correct_answers = {
            'screening_q1': 'Planning, research, and initial design activities before product launch',
            'screening_q2': 'Proactively identifying potential issues before they materialize',
            'screening_q3': 'Multiple types including ethical, safety, regulatory, and social risks',
        }
        
        # Check each answer and build error message
        errors = []
        if values['screening_q1'] != correct_answers['screening_q1']:
            errors.append('Question 1 is incorrect. Please review and try again.')
        if values['screening_q2'] != correct_answers['screening_q2']:
            errors.append('Question 2 is incorrect. Please review and try again.')
        if values['screening_q3'] != correct_answers['screening_q3']:
            errors.append('Question 3 is incorrect. Please review and try again.')
        
        if errors:
            return ' '.join(errors)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.screening_page_time = time.time() - player.participant._start_time
        # Always mark as passed since they can't proceed without correct answers
        player.passed_screening = True
        print(f"Participant {player.participant.label}: Passed screening")

class ScreenedOut(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Never display - participants must answer correctly to proceed
        return False
    
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
        player.clt_condition_page_time = time.time() - player.participant._start_time
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
        player.spec_condition_page_time = time.time() - player.participant._start_time

class Mediators(Page):
    form_model = 'player'
    form_fields = [
        'scenario_creativity',
        'risk_accessibility',
        'risk_tangibility',
        'mediator_attention_check',
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def error_message(player: Player, values):
        if values['mediator_attention_check'] != 6:  # 6 corresponds to 'Agree'
            return 'Question 4 is incorrect. Please review and try again.'

    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None
 
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.mediators_page_time = time.time() - player.participant._start_time

class Manip_Check(Page):
    form_model = 'player'
    form_fields = ['specdesign_check', 'construal_check']
    
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
        player.manip_check_page_time = time.time() - player.participant._start_time
        # Log manipulation check responses
        print(f"Participant {player.participant.label}: Specdesign check = {player.specdesign_check}, Construal check = {player.construal_check}")

class Controls(Page):
    form_model = 'player'
    form_fields = [
        'manipulation_effort',
        'manipulation_difficulty',
        'attention_check',
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening
    
    @staticmethod
    def error_message(player: Player, values):
        if values['attention_check'] != 6:  # 6 corresponds to 'Agree'
            return 'Question 3 is incorrect. Please review and try again.'
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.controls_page_time = time.time() - player.participant._start_time

class Characteristics(Page):
    form_model = 'player'
    form_fields = [
        'risk_taking', 
        'risk_avoidance',
        'creativity',
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
        player.characteristics_page_time = time.time() - player.participant._start_time

class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'qualification',
        'work_experience',
        'rm_experience',
        'industry_experience',
        'familiarity_insurance',
        'familiarity_ai',
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
    form_fields = ['prize_email', 'feedback']  # Capture email and feedback in the database
    
    @staticmethod
    def is_displayed(player: Player):
        return player.passed_screening

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            participant_id=player.participant.part_id
        )
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import time
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Save timing
        player.thanks_page_time = time.time() - player.participant._start_time
        # Save feedback to the database
        feedback = player.feedback
        if feedback:
            print(f"Feedback received: {feedback}")

class Redirect(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Don't display redirect page
        return False

# Update the page sequence
page_sequence = [
    Consent,
    Screening,
    ScreenedOut,
    Introduction,
    Background,
    CLT_Condition,
    Spec_Condition,
    Assessment,
    Mediators,
    Controls,
    Characteristics,
    Manip_Check,
    Demographics,
    Thanks,
    Redirect
]