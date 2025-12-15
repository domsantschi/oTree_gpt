from otree.api import *
import random
import time

doc = """
CrossFit recovery app evaluation survey for CrossFit Bern.
Participants are randomly assigned to either view the actual app (Actual-Condition)
or provide expectations for what such an app should offer (Expected-Condition).
"""

class C(BaseConstants):
    NAME_IN_URL = 'crossflexed'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    
    # Demographics
    gender = models.StringField(
        label="What is your gender?",
        choices=["Male", "Female", "Other", "Prefer not to say"],
    )
    age = models.StringField(
        label="What is your age?",
        choices=[
            "Less than 18 years",
            "18-24 years",
            "25-34 years",
            "35-50 years",
            "51-65 years",
            "Over 65 years",
        ],
    )
    crossfit_experience = models.StringField(
        label="For how long have you been doing CrossFit?",
        choices=[
            "Less than 1 year",
            "1-3 years",
            "4-10 years",
            "More than 10 years",
        ],
    )
    
    # Context questions
    crossfit_frequency = models.StringField(
        label="On average, how many times per week do you go to CrossFit?",
        choices=["1", "2", "3", "4", "5+", "Prefer not to say"],
    )
    mobility_quality = models.StringField(
        label="How easy is it for you to recover from a CrossFit session?",
        choices=["Very difficult", "Difficult", "Moderate", "Easy", "Very easy", "Prefer not to say"],
    )
    cooldown_frequency = models.StringField(
        label="After a CrossFit session, how often do you perform a cooldown or post-workout stretching routine?",
        choices=["Never", "Rarely", "Sometimes", "Often", "Always", "Prefer not to say"],
    )
    cooldown_location = models.StringField(
        label="Where do you currently perform the cooldown or post-workout stretching routine?",
        choices=["At home", "At the gym", "Other"],
        blank=True,
    )
    cooldown_location_other = models.StringField(
        label="Please explain where:",
        blank=True,
    )
    
    # Condition type assignment (Actual vs Expected)
    condition_type = models.StringField(
        label="Condition Type",
        choices=["Actual-Condition", "Expected-Condition"],
        blank=True,
        doc="Randomly assigned condition type"
    )
    
    # App evaluation questions (Actual-Condition)
    app_general = models.IntegerField(
        label="The app provides guided cooldown and post‑workout routines.",
        min=1,
        max=5,
        doc="General functionality evaluation (1=Strongly disagree, 5=Strongly agree)"
    )
    app_wod_specific = models.IntegerField(
        label="The app provides recovery suggestions tailored to today's workout.",
        min=1,
        max=5,
        doc="WOD-specific tailoring evaluation (1=Strongly disagree, 5=Strongly agree)"
    )
    app_time_efficient = models.IntegerField(
        label="The suggested routines can be completed within about 10 minutes.",
        min=1,
        max=5,
        doc="Time efficiency evaluation (1=Strongly disagree, 5=Strongly agree)"
    )
    app_location = models.IntegerField(
        label="I can perform the suggested routines wherever I am.",
        min=1,
        max=5,
        doc="Location flexibility evaluation (1=Strongly disagree, 5=Strongly agree)"
    )
    app_design = models.IntegerField(
        label="The app looks mobile‑optimized and is easy to use.",
        min=1,
        max=5,
        doc="Design and usability evaluation (1=Strongly disagree, 5=Strongly agree)"
    )
    app_timing = models.IntegerField(
        label="The videos and exercises clearly show the duration I should spend on each movement.",
        min=1,
        max=5,
        doc="Timing clarity evaluation (1=Strongly disagree, 5=Strongly agree)"
    )
    app_videos = models.IntegerField(
        label="The recovery videos feature a real person demonstrating the movements.",
        min=1,
        max=5,
        doc="Video quality evaluation (1=Strongly disagree, 5=Strongly agree)"
    )
    app_instructions = models.IntegerField(
        label="Each exercise includes clear instructions and safety cues.",
        min=1,
        max=5,
        doc="Instruction clarity evaluation (1=Strongly disagree, 5=Strongly agree)"
    )
    
    # Expected app evaluation questions (Expected-Condition)
    expected_general = models.IntegerField(
        label="I expect CrossFit Bern to offer guided cooldown and post‑workout routines.",
        min=1,
        max=5,
        doc="Expected general functionality (1=Strongly disagree, 5=Strongly agree)"
    )
    expected_wod_specific = models.IntegerField(
        label="I expect the routines to be tailored to the workout of the day (WOD).",
        min=1,
        max=5,
        doc="Expected WOD-specific tailoring (1=Strongly disagree, 5=Strongly agree)"
    )
    expected_time_efficient = models.IntegerField(
        label="I expect the routines to be completable within about 10 minutes.",
        min=1,
        max=5,
        doc="Expected time efficiency (1=Strongly disagree, 5=Strongly agree)"
    )
    expected_location = models.IntegerField(
        label="I expect the routines to be doable anywhere (gym, home, outdoors).",
        min=1,
        max=5,
        doc="Expected location flexibility (1=Strongly disagree, 5=Strongly agree)"
    )
    expected_design = models.IntegerField(
        label="I expect a clean, mobile‑optimized interface that is easy to use.",
        min=1,
        max=5,
        doc="Expected design and usability (1=Strongly disagree, 5=Strongly agree)"
    )
    expected_timing = models.IntegerField(
        label="I expect videos and exercises to show exact durations for each movement.",
        min=1,
        max=5,
        doc="Expected timing clarity (1=Strongly disagree, 5=Strongly agree)"
    )
    expected_videos = models.IntegerField(
        label="I expect recovery videos to feature a real person demonstrating the movements.",
        min=1,
        max=5,
        doc="Expected video quality (1=Strongly disagree, 5=Strongly agree)"
    )
    expected_instructions = models.IntegerField(
        label="I expect each exercise to include clear instructions and basic safety cues.",
        min=1,
        max=5,
        doc="Expected instruction clarity (1=Strongly disagree, 5=Strongly agree)"
    )
    
    # Controls feedback
    stretching_solution_likelihood = models.StringField(
        label="If CrossFit Bern offered a post-recovery stretching solution, how likely are you to use it?",
        choices=["Never", "Rarely", "Sometimes", "Often", "After every workout", "Not sure"],
    )
    offer_improvement_assessment = models.StringField(
        label="To what extent would you assess the CrossFit-Bern offer to be improved thanks to this?",
        choices=["Not at all", "Rather not", "Neutral", "A bit", "A lot", "Prefer not to say"],
    )
    
    # Page timing fields
    introduction_page_time = models.FloatField(default=0)
    background_page_time = models.FloatField(default=0)
    condition1_page_time = models.FloatField(default=0)
    controls_page_time = models.FloatField(default=0)
    demographics_page_time = models.FloatField(default=0)
    thanks_page_time = models.FloatField(default=0)


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        player.condition_type = random.choice(['Actual-Condition', 'Expected-Condition'])


# --- Pages ---

class Introduction(Page):
    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.introduction_page_time = time.time() - player.participant._start_time


class Context(Page):
    form_model = 'player'
    form_fields = ['crossfit_frequency', 'mobility_quality', 'cooldown_frequency', 'cooldown_location', 'cooldown_location_other']
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.background_page_time = time.time() - player.participant._start_time
        # Ensure condition_type is set (in case creating_session didn't run)
        if not player.condition_type:
            player.condition_type = random.choice(['Actual-Condition', 'Expected-Condition'])


class Actual_Condition(Page):
    form_model = 'player'
    form_fields = [
        'app_general',
        'app_wod_specific',
        'app_time_efficient',
        'app_location',
        'app_design',
        'app_timing',
        'app_videos',
        'app_instructions',
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.condition_type == "Actual-Condition"
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._start_time = time.time()
        return None
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.condition1_page_time = time.time() - player.participant._start_time


class Expected_Condition(Page):
    form_model = 'player'
    form_fields = [
        'expected_general',
        'expected_wod_specific',
        'expected_time_efficient',
        'expected_location',
        'expected_design',
        'expected_timing',
        'expected_videos',
        'expected_instructions',
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.condition_type == "Expected-Condition"
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._start_time = time.time()
        return None
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.condition1_page_time = time.time() - player.participant._start_time


class Controls(Page):
    form_model = 'player'
    form_fields = [
        'stretching_solution_likelihood',
        'offer_improvement_assessment',
    ]
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.controls_page_time = time.time() - player.participant._start_time


class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'age',
        'gender',
        'crossfit_experience',
    ]
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.demographics_page_time = time.time() - player.participant._start_time


class Thanks(Page):
    @staticmethod
    def get_timeout_seconds(player: Player):
        player.participant._start_time = time.time()
        return None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.thanks_page_time = time.time() - player.participant._start_time


page_sequence = [
    Introduction,
    Context,
    Actual_Condition,
    Expected_Condition,
    Controls,
    Demographics,
    Thanks,
]