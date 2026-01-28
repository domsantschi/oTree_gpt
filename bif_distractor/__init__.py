from otree.api import *
import json

doc = """
BIF (Behavioral Identification Form) distractor task.
A single page with 10 BIF questions that redirects to spec_design2 upon completion.
"""


class C(BaseConstants):
    NAME_IN_URL = 'bif_distractor'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # BIF (Behavioral Identification Form) fields
    bif_1 = models.IntegerField(
        label="Picking an apple",
        choices=[[1, "Getting something to eat"], [0, "Pulling an apple off a branch"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 1"
    )
    bif_2 = models.IntegerField(
        label="Painting a room",
        choices=[[0, "Applying brush strokes"], [1, "Making the room look fresh"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 2"
    )
    bif_3 = models.IntegerField(
        label="Locking a door",
        choices=[[0, "Putting a key in the lock"], [1, "Securing the house"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 3"
    )
    bif_4 = models.IntegerField(
        label="Voting",
        choices=[[1, "Influencing the election"], [0, "Marking a ballot"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 4"
    )
    bif_5 = models.IntegerField(
        label="Filling out a personality test",
        choices=[[0, "Answering questions"], [1, "Revealing what you're like"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 5"
    )
    bif_6 = models.IntegerField(
        label="Greeting someone",
        choices=[[0, "Saying hello"], [1, "Showing friendliness"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 6"
    )
    bif_7 = models.IntegerField(
        label="Taking a test",
        choices=[[1, "Showing one's knowledge"], [0, "Answering questions"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 7"
    )
    bif_8 = models.IntegerField(
        label="Resisting temptation",
        choices=[[0, "Saying 'no'"], [1, "Showing moral courage"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 8"
    )
    bif_9 = models.IntegerField(
        label="Traveling by car",
        choices=[[0, "Following a map"], [1, "Seeing countryside"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 9"
    )
    bif_10 = models.IntegerField(
        label="Talking to a child",
        choices=[[1, "Teaching a child something"], [0, "Using simple words"]],
        widget=widgets.RadioSelect,
        doc="BIF Question 10"
    )
    
    # Calculated fields
    bif_score = models.IntegerField(
        initial=0,
        doc="Total BIF score (sum of all responses, 0-10)"
    )
    bif_responses = models.LongStringField(
        blank=True,
        doc="JSON string of BIF responses"
    )


# --- Pages --------------------------------------------------------------------

class BIF(Page):
    form_model = 'player'
    form_fields = [
        'bif_1', 'bif_2', 'bif_3', 'bif_4', 'bif_5',
        'bif_6', 'bif_7', 'bif_8', 'bif_9', 'bif_10',
    ]

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Calculate BIF score (sum of all responses)
        player.bif_score = (
            player.bif_1 + player.bif_2 + player.bif_3 + player.bif_4 + player.bif_5 +
            player.bif_6 + player.bif_7 + player.bif_8 + player.bif_9 + player.bif_10
        )
        
        # Store responses as JSON
        responses = {
            'bif_1': player.bif_1,
            'bif_2': player.bif_2,
            'bif_3': player.bif_3,
            'bif_4': player.bif_4,
            'bif_5': player.bif_5,
            'bif_6': player.bif_6,
            'bif_7': player.bif_7,
            'bif_8': player.bif_8,
            'bif_9': player.bif_9,
            'bif_10': player.bif_10,
        }
        player.bif_responses = json.dumps(responses)
        
        # Log BIF score
        print(f"Participant: BIF score = {player.bif_score}")


class Redirect(Page):
    """Redirect page that sends participants to spec_design2 session."""
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            redirect_url='https://ccma-experiments-37b86b110ea3.herokuapp.com/room/spec_design2'
        )


page_sequence = [BIF, Redirect]