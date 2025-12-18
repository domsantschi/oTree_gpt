from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


class Constants(BaseConstants):
    name_in_url = 'prisoner'
    players_per_group = 2
    num_rounds = 1

    # payoff if 1 player defects and the other cooperates
    betray_payoff = 50
    betrayed_payoff = 12

    # payoff if both players cooperate or both defect
    both_cooperate_payoff = 32
    both_defect_payoff = 25


class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    decision = models.StringField(
        choices=['Action 1', 'Action 2'],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):

        payoff_matrix = {
            'Action 1':
                {
                    'Action 1': Constants.both_cooperate_payoff,
                    'Action 2': Constants.betrayed_payoff
                },
            'Action 2':
                {
                    'Action 1': Constants.betray_payoff,
                    'Action 2': Constants.both_defect_payoff
                }
        }

        self.payoff = payoff_matrix[self.decision][self.other_player().decision]