from dotenv import load_dotenv
load_dotenv()

from otree.api import *
from os import environ
from openai import OpenAI
import random
import json
from pydantic import BaseModel 
from datetime import datetime, timezone
import math
# import tiktoken
# from codecarbon import EmissionsTracker

# # Initialize the emissions tracker
# tracker = EmissionsTracker()
# tracker.start()

doc = """
LLM chat with multiple agents, based on Cline McKenna's work.
"""

author = 'Dominic Santschi dominic.santschi@unisg.ch'

########################################################
# Constants                                            #
########################################################

class C(BaseConstants):
    NAME_IN_URL = 'exp'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # Fixed values for calculations
    BEGINNING_INVENTORY_COST = 646000
    BEGINNING_INVENTORY_EMISSIONS = 168
    ENDING_INVENTORY_COST = 4486000
    ENDING_INVENTORY_EMISSIONS = 1166

    # LLM vars
    ## bot label and temperature
    ### message frequency to check for message (in seconds)
    BOT_MSG_FREQUENCY = 6

    ### red bot
    BOT_LABEL1 = 'Red'
    BOT_TEMP1 = 1
    
    ### black bot
    BOT_LABEL2 = 'Black'
    BOT_TEMP2 = 1

    ### green bot
    BOT_LABEL3 = 'Green'
    BOT_TEMP3 = 1

    # 3d environment vars
    ROOM_LENGTH = 60
    ROOM_WIDTH = 40
    ROOM_HEIGHT = 14
    NPC_JITTER = 3
    NPC_PERSONAL_SPACE = 20
    RED_POS = {'x': -20, 'y': 2, 'z': -8}
    BLACK_POS = {'x': 10, 'y': 2, 'z': 12}
    GREEN_POS = {'x': 17, 'y': 2, 'z': -5}
    PLAYER_POS = {'x': 0, 'y': 2, 'z': 0}    # Fixed player starting position at center

    # Debug settings (coordinates and distance lines)
    DEBUG = False

    ## openAI key
    OPENAI_KEY = environ.get('OPENAI_KEY')

    ## model
    MODEL = "gpt-4o-mini"

    ## set system prompt for agents
    ## according to OpenAI's documentation, this should be less than ~1500 words
    ## set system prompt for bots
    ### red bot
    SYS_RED = f"""You are {BOT_LABEL1} Bot, a specialist in Direct materials used for Acme LLC's Cost of Goods Sold Budget. Speak in professional, concise language. You are assisting the management accountant in preparing the Cost of Goods Sold Budget and its corresponding CO2 Emission Budget for the Year Ending December 31, 2025. Based on your expertise, the direct materials used will be $10,280,000 for 2025. Here is what you know:
    - The Beginning finished-goods inventory, January 1, 2025, was $646,000 USD with total CO2 emissions of 168 mt (based on an average emission intensity of 0.26 kg/$).
    - The Ending finished-goods inventory, December 31, 2025, must be $750,000 USD with total CO2 emissions of 195 mt.
    - Your expertise is in Direct materials used, and you can provide insights or calculations related to this area.

    If the user asks something outside your expertise, simply tell them you are not sure and suggest consulting another bot.

    Each user input will be a nested list of JSON objects containing:
    - their sender identifier, which shows who sent the message
    - instructions for responding
    - tone to use
    - text you will be responding to

    IMPORTANT: This list will be the entire message history between all actors in a conversation. Messages sent by you are labeled in the 'Sender' field as {BOT_LABEL1}. Other actors will be labeled differently (e.g., 'P1', 'B1', etc.).
    
    As output, you MUST provide a JSON object with:
    - 'sender': your assigned sender identifier
    - 'msgId': your assigned message ID
    - 'tone': your assigned tone
    - 'text': your response (limit to 140 characters)"""

    SYS_BLACK = f"""You are {BOT_LABEL2} Bot, a specialist in Direct manufacturing labor for Acme LLC's Cost of Goods Sold Budget. Speak in professional, concise language. You are assisting the management accountant in preparing the Cost of Goods Sold Budget and its corresponding CO2 Emission Budget for the Year Ending December 31, 2025. Based on your expertise, the direct manufacturing labor will be $6,000,000 for 2025. Here is what you know:
    - The Beginning finished-goods inventory, January 1, 2025, was $646,000 USD with total CO2 emissions of 168 mt (based on an average emission intensity of 0.26 kg/$).
    - The Ending finished-goods inventory, December 31, 2025, must be $750,000 USD with total CO2 emissions of 195 mt.
    - Your expertise is in Direct manufacturing labor, and you can provide insights or calculations related to this area.

    If the user asks something outside your expertise, simply tell them you are not sure and suggest consulting another bot.

    Each user input will be a nested list of JSON objects containing:
    - their sender identifier, which shows who sent the message
    - instructions for responding
    - tone to use
    - text you will be responding to

    IMPORTANT: This list will be the entire message history between all actors in a conversation. Messages sent by you are labeled in the 'Sender' field as {BOT_LABEL2}. Other actors will be labeled differently (e.g., 'P1', 'B1', etc.).
    
    As output, you MUST provide a JSON object with:
    - 'sender': your assigned sender identifier
    - 'msgId': your assigned message ID
    - 'tone': your assigned tone
    - 'text': your response (limit to 140 characters)"""

    SYS_GREEN = f"""You are {BOT_LABEL3} Bot, a specialist in Manufacturing overhead for Acme LLC's Cost of Goods Sold Budget. Speak in professional, concise language. You are assisting the management accountant in preparing the Cost of Goods Sold Budget and its corresponding CO2 Emission Budget for the Year Ending December 31, 2025. Based on your expertise, the manufacturing overhead used will be $12,000,000 for 2025. Here is what you know:
    - The Beginning finished-goods inventory, January 1, 2025, was $646,000 USD with total CO2 emissions of 168 mt (based on an average emission intensity of 0.26 kg/$).
    - The Ending finished-goods inventory, December 31, 2025, must be $750,000 USD with total CO2 emissions of 195 mt.
    - Your expertise is in Manufacturing overhead, and you can provide insights or calculations related to this area.

    If the user asks something outside your expertise, simply tell them you are not sure and suggest consulting another bot.

    Each user input will be a nested list of JSON objects containing:
    - their sender identifier, which shows who sent the message
    - instructions for responding
    - tone to use
    - text you will be responding to

    IMPORTANT: This list will be the entire message history between all actors in a conversation. Messages sent by you are labeled in the 'Sender' field as {BOT_LABEL3}. Other actors will be labeled differently (e.g., 'P1', 'B1', etc.).
    
    As output, you MUST provide a JSON object with:
    - 'sender': your assigned sender identifier
    - 'msgId': your assigned message ID
    - 'tone': your assigned tone
    - 'text': your response (limit to 140 characters)"""

########################################################
# OpenAI Setup                                         #
########################################################

# specify json schema for bot messages
class MsgOutputSchema(BaseModel):
    sender: str
    msgId: str
    tone: str
    text: str

# function to run messages 
## when triggered, this function will run the system prompt and the user message, which will contain the entire message history, rather than building on dialogue one line at a time

# bot llm function
def runGPT(inputMessage, tone, botLabel):

    # grab bot vars from constants
    botLabel = botLabel
    if botLabel == C.BOT_LABEL1:
        botTemp = C.BOT_TEMP1
        botPrompt = C.SYS_RED
    elif botLabel == C.BOT_LABEL2:
        botTemp = C.BOT_TEMP2
        botPrompt = C.SYS_BLACK
    elif botLabel == C.BOT_LABEL3:
        botTemp = C.BOT_TEMP3
        botPrompt = C.SYS_GREEN

    # assign message id and bot label
    dateNow = str(datetime.now(tz=timezone.utc).timestamp())
    botMsgId = botLabel + '-' + str(dateNow)

    # grab text that participant inputs and format for llm
    instructions = f"""
        Provide a json object with the following schema (DO NOT CHANGE ASSIGNED VALUES):
            'sender': {botLabel} (string),
            'msgId': {botMsgId} (string), 
            'tone': {tone} (string), 
            'text': Your response to the user's message in a {tone} tone (string), 
    """

    # overwrite instructions for each dictionary
    for x in inputMessage:
        x['instructions'] = json.dumps(instructions)


    # create input message with a nested structure
    nestedInput = [{'role': 'user', 'content': json.dumps(inputMessage)}]
    
    # combine input message with assigned prompt
    inputMsg = [{'role': 'system', 'content': botPrompt}] + nestedInput

    # openai client and response creation
    client = OpenAI(api_key=C.OPENAI_KEY)
    response = client.chat.completions.create(
        model=C.MODEL,
        temperature=botTemp,
        messages=inputMsg,
        functions=[{
            "name": "msg_output_schema",
            "parameters": MsgOutputSchema.model_json_schema()
        }],
        function_call={"name": "msg_output_schema"}
    )

    # grab text output
    msgOutput = response.choices[0].message.function_call.arguments

    # return the response json
    return msgOutput


########################################################
# NPC bot functions                                    #
########################################################

# initial positions
def initializeNPCPositions():
    """Initialize fixed positions for all characters."""
    return {
        'red': C.RED_POS,
        'green': C.GREEN_POS,
        'black': C.BLACK_POS,
        'player': C.PLAYER_POS  # Use fixed player position instead of random
    }

def calculate_distance(position1, position2):
    # Convert string values to float if needed
    x1 = float(position1['x']) if isinstance(position1['x'], str) else position1['x']
    z1 = float(position2['z']) if isinstance(position1['z'], str) else position1['z']
    x2 = float(position2['x']) if isinstance(position2['x'], str) else position2['x']
    z2 = float(position2['z']) if isinstance(position2['z'], str) else position2['z']
    
    return math.sqrt((x1 - x2)**2 + (z1 - z2)**2)

def calculate_npc_distances(player_pos):
    """Calculate distances from player position to all NPCs
    Args:
        player_pos (dict): Player position with 'x', 'y', 'z' coordinates
    Returns:
        dict: Distances to each NPC (red, black, green)
    """
    return {
        'Red': calculate_distance(player_pos, C.RED_POS),
        'Black': calculate_distance(player_pos, C.BLACK_POS),
        'Green': calculate_distance(player_pos, C.GREEN_POS)
    }




########################################################
# Models                                               #
########################################################

class Subsession(BaseSubsession):
    pass

def creating_session(subsession: Subsession):
    players = subsession.get_players()
    
    # Initialize participant fields
    for p in players:
        p.participant.failed_knowledge_check = False
        
        # Randomly assign impact_transparency condition
        p.participant.vars['impact_transparency'] = random.choice(['costs', 'co2'])

    # Example: Randomly assign conditions to players
    conditions = ['Cost Impact Focus', 'Environmental Impact Focus']
    for p in players:
        p.condition = random.choice(conditions)

        # Assign tone for the conversation
        tones = ['neutral']
        p.tone = random.choice(tones)

class Group(BaseGroup):
    pass    

class Player(BasePlayer):
    # Existing fields
    tone = models.StringField()
    phase = models.IntegerField(initial=0)
    cachedMessages = models.LongStringField(initial='[]')
    cachedMessagesRed = models.LongStringField(initial='[]')  # Cached messages for Red bot
    cachedMessagesBlack = models.LongStringField(initial='[]')  # Cached messages for Black bot
    cachedMessagesGreen = models.LongStringField(initial='[]')  # Cached messages for Green bot
    condition = models.StringField()
    pos_data_history = models.LongStringField(initial='[]')  # Field to store position history

    # Knowledge check fields
    q1 = models.StringField(
        choices=['a', 'b', 'c'],
        label="When should a company prepare budgets?",
    )
    q2 = models.StringField(
        choices=['a', 'b', 'c'],
        label="What is the formula for Cost of Goods Sold (COGS)?",
    )
    q3 = models.StringField(
        choices=['a', 'b', 'c'],
        label="Which of the following is a component of the operating budget?",
    )

    # New fields for Exp_Results
    justification = models.LongStringField(
        label="Provide a justification for your choice",
    )

    # Inputs from the Decision page
    budgeted_cost = models.CurrencyField(
        label="Budgeted Cost of Goods Sold (USD)",
        min=0
    )
    budgeted_emissions = models.FloatField(
        label="Budgeted CO2 Emissions (metric tons)",
        min=0
    )

    # Automatically calculated values
    cost_of_goods_sold = models.CurrencyField()
    cost_of_goods_sold_emissions = models.FloatField()

    # New fields for Checks page
    impact_focus = models.StringField(
        choices=['costs', 'co2'],
        label="What are the two factors that will be used for your performance evaluation and the determination of your compensation?",
    )
    impact_transparency = models.StringField(
        choices=['costs', 'co2', 'none'],  # Add 'none' as a valid choice
        label="When interacting with your virtual colleagues, did you receive any information about the impact of your queries?",
    )

    # New fields for Controls page
    age = models.StringField(
        choices=[
            'less_than_25', '25_34', '35_44', '45_54', '55_64', '65_74', 'above_74'
        ],
        label="What is your age?",
    )
    gender = models.StringField(
        choices=['male', 'female', 'other'],
        label="What is your gender?",
    )
    qualification = models.StringField(
        choices=['diploma', 'bachelor', 'masters', 'doctoral', 'none'],
        label="What is your highest academic qualification?",
    )
    controlling_experience = models.IntegerField(
        label="How many years of full-time working experience in a controlling role do you have?",
        min=0,
    )


########################################################
# Extra models                                         #
########################################################

# message information
class MessageData(ExtraModel):
    # Data links
    player = models.Link(Player)

    # Message info
    msgId = models.StringField()
    timestamp = models.StringField()
    sender = models.StringField()
    tone = models.StringField()
    fullText = models.StringField()  # Store the full botText JSON object
    msgText = models.StringField()  # Store the 'text' field from the botText

    # NPC target
    target = models.StringField()

# message reaction information
class CharPositionData(ExtraModel):
    # data links
    player = models.Link(Player)

    # reaction info
    msgId = models.StringField()
    timestamp = models.StringField()
    posPlayer = models.StringField()
    posRed = models.StringField()
    posBlack = models.StringField()
    posGreen = models.StringField()

    # New fields
    closestNPC = models.StringField()  # Closest NPC
    textPosition = models.StringField()  # Position from which the player texted


########################################################
# Custom export                                        #
########################################################

# custom export of chatLog
def custom_export(players):
    # Header row
    yield [
        'sessionId',
        'participantId',
        'posDataHistory',  # Include position history
        'cachedMessagesRed',  # Include Red bot's conversation thread
        'cachedMessagesBlack',  # Include Black bot's conversation thread
        'cachedMessagesGreen',  # Include Green bot's conversation thread
        'msgId',
        'timestamp',
        'sender',
        'tone',
        'fullText',  # Include the full botText JSON object
        'msgText',
    ]

    # Export data for each player
    for player in players:
        participant = player.participant
        session = player.session

        # Retrieve all messages for the player
        messages = MessageData.filter(player=player)

        for message in messages:
            yield [
                session.code,
                participant.code,
                player.pos_data_history,  # Include the position history
                player.cachedMessagesRed,  # Include Red bot's conversation thread
                player.cachedMessagesBlack,  # Include Black bot's conversation thread
                player.cachedMessagesGreen,  # Include Green bot's conversation thread
                message.msgId,
                message.timestamp,
                message.sender,
                message.tone,
                message.fullText,  # Include the full botText JSON object
                message.msgText,
            ]


########################################################
# Methods                                              #
########################################################

def calculate_cost_of_goods_sold(player: Player):
    """Calculate the Cost of Goods Sold and its emissions."""
    # Retrieve constants
    beginning_inventory = C.BEGINNING_INVENTORY_COST
    ending_inventory = C.ENDING_INVENTORY_COST

    # Retrieve player inputs
    direct_materials = player.participant.vars.get('direct_materials', 0)
    direct_labor = player.participant.vars.get('direct_labor', 0)
    manufacturing_overhead = player.participant.vars.get('manufacturing_overhead', 0)

    # Calculate cost of goods manufactured
    cost_of_goods_manufactured = direct_materials + direct_labor + manufacturing_overhead

    # Calculate cost of goods available for sale
    cost_of_goods_available = beginning_inventory + cost_of_goods_manufactured

    # Calculate cost of goods sold
    cost_of_goods_sold = cost_of_goods_available - ending_inventory
    player.cost_of_goods_sold = cost_of_goods_sold

    # Calculate emissions
    beginning_emissions = C.BEGINNING_INVENTORY_EMISSIONS
    ending_emissions = C.ENDING_INVENTORY_EMISSIONS
    emissions_factor = 0.00026  # Emissions per dollar

    cost_of_goods_available_emissions = beginning_emissions + (cost_of_goods_manufactured * emissions_factor)
    cost_of_goods_sold_emissions = cost_of_goods_available_emissions - ending_emissions
    player.cost_of_goods_sold_emissions = cost_of_goods_sold_emissions


########################################################
# Pages                                                #
########################################################

class Introduction(Page):
    pass

class Background(Page):
    pass

class Knowledge(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        """Check if the player passed the knowledge test."""
        # Define the correct answers
        correct_answers = {
            'q1': 'b',  # Budgeting helps to improve resource planning.
            'q2': 'a',  # Cost of Goods Sold Budget.
            'q3': 'a',  # Cost of Goods Available for Sale – Ending Inventory.
        }

        # Check if the player's answers match the correct answers
        if (
            player.q1 != correct_answers['q1'] or
            player.q2 != correct_answers['q2'] or
            player.q3 != correct_answers['q3']
        ):
            # Mark the participant as having failed the knowledge check
            player.participant.failed_knowledge_check = True

class Sorry(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Display the Thanks page in two cases:
        # 1. If the player failed the knowledge check
        # 2. If this is the final page after the Controls page
        if player.participant.failed_knowledge_check:
            return True

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            participant_id=player.participant.code,
            failed_knowledge_check=player.participant.failed_knowledge_check,
            is_final=not player.participant.failed_knowledge_check
        )

class Condition1(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            condition=player.condition
        )

class Explainer(Page):
    pass

class chat(Page):

    form_model = 'player'
    timeout_seconds = 60  # Set the timeout for the chat page

    @staticmethod
    def vars_for_template(player):
        condition = player.participant.vars.get('impact_transparency', 'costs')
        return dict(
            condition=condition,
            total_tokens=0,  # Initial value
            total_emissions=0,  # Initial value
        )

    # vars that we will pass to chat.html
    @staticmethod
    def js_vars(player):
        # playerId as seen in chat
        currentPlayer = 'P' + str(player.id_in_group)
        
        return dict(
            id_in_group=player.id_in_group,
            playerId=currentPlayer,
            condition=player.participant.vars.get('impact_transparency', 'costs'),  # Add this line
            bot_label1=C.BOT_LABEL1,
            bot_label2=C.BOT_LABEL2,
            roomLength=C.ROOM_LENGTH,
            roomWidth=C.ROOM_WIDTH,
            roomHeight=C.ROOM_HEIGHT,
            npcPersonalSpace=C.NPC_PERSONAL_SPACE,
            npcJitter=C.NPC_JITTER,
            debug=C.DEBUG,
        )

    # live method functions
    @staticmethod
    def live_method(player: Player, data):
        
        # if no new data, just return cached messages
        if not data:
            return {player.id_in_group: dict(
                messages=json.loads(player.cachedMessages),
                reactions=[]
            )}
        
        # if we have new data, process it and update cache
        messages = json.loads(player.cachedMessages)

        # create current player identifier
        currentPlayer = 'P' + str(player.id_in_group)

        # grab tone from data
        tone = player.tone
        
        # handle different event types
        if 'event' in data:

            # grab event type
            event = data['event']
            
            # handle player input logic
            if event == 'text':
                
                # get data from request
                text = data.get('text', '')
                posData = data.get('pos', {})
                currentPlayer = 'P' + str(player.id_in_group)
                messages = json.loads(player.cachedMessages)
                
                # calculate distance to NPCs
                print('Player pos:', posData)
                npcDistances = calculate_npc_distances(posData)
                print('NPC distances:', npcDistances)

                # determine closest NPC (within 10 units of distance)
                min_distance = min(npcDistances.values())
                closestNPC = None if min_distance > 10 else [x for x in npcDistances if npcDistances[x] == min_distance][0]
                print('Closest NPC:', closestNPC)

                # create message id
                dateNow = str(datetime.now(tz=timezone.utc).timestamp())
                msgId = currentPlayer + '-' + dateNow
                
                # create message
                msg = {'role': 'user', 'content': json.dumps({
                    'sender': currentPlayer,
                    'msgId': msgId,
                    'tone': tone,
                    'text': text,
                })}
                
                # save to database
                MessageData.create(
                    player=player,
                    sender=currentPlayer,
                    msgId=msgId,
                    timestamp=dateNow,
                    tone=tone,
                    fullText=json.dumps(msg),
                    msgText=text,
                    target=closestNPC,
                )
                
                # append to messages
                messages.append(msg)
                
                # update cache
                player.cachedMessages = json.dumps(messages)
                
                # return output to chat.html
                return {player.id_in_group: dict(
                    event='text',
                    selfText=text,
                    sender=currentPlayer,
                    msgId=msgId,
                    tone=tone,
                    phase=player.phase,
                    target=closestNPC
                )}

            # handle bot messages
            elif event == 'botMsg':
                # Get data from the request
                botId = data.get('botId')
                dateNow = str(datetime.now(tz=timezone.utc).timestamp())

                if botId:
                    # Run the GPT function to generate the bot's response
                    botText = runGPT(messages, tone, botId)
                    print('botId:', botId)
                    print('botText:', botText)

                    # Extract output
                    botContent = json.loads(botText)
                    outputText = botContent['text']
                    botMsgId = botContent['msgId']
                    botMsg = {'role': 'assistant', 'content': botText}

                    # Save the bot message to the appropriate thread
                    if botId == C.BOT_LABEL1:  # Red bot
                        cachedMessagesRed = json.loads(player.cachedMessagesRed)
                        cachedMessagesRed.append(botMsg)
                        player.cachedMessagesRed = json.dumps(cachedMessagesRed)
                    elif botId == C.BOT_LABEL2:  # Black bot
                        cachedMessagesBlack = json.loads(player.cachedMessagesBlack)
                        cachedMessagesBlack.append(botMsg)
                        player.cachedMessagesBlack = json.dumps(cachedMessagesBlack)
                    elif botId == C.BOT_LABEL3:  # Green bot
                        cachedMessagesGreen = json.loads(player.cachedMessagesGreen)
                        cachedMessagesGreen.append(botMsg)
                        player.cachedMessagesGreen = json.dumps(cachedMessagesGreen)

                    # Save the bot message to the database
                    MessageData.create(
                        player=player,
                        sender=botId,
                        msgId=botMsgId,
                        timestamp=dateNow,
                        tone=tone,
                        fullText=json.dumps(botContent),  # Save the full botText JSON object
                        msgText=outputText,  # Save only the 'text' field
                        target=botId
                    )

                    # Append the bot message to the cached messages
                    messages.append(botMsg)

                    # Return data to chat.html
                    return {player.id_in_group: dict(
                        event='botText',
                        botMsgId=botMsgId,
                        text=outputText,
                        tone=tone,
                        sender=botId,
                        phase=player.phase
                    )}


                # if botId is None, then no NPC is close enough to chat
                else:
                    print('Not near any NPCs!')
            
                
            
            # handle position check updates
            elif event == 'posCheck':
                # Get position data from the request
                pos_data = data.get('pos', {})
                print('Received posData:', pos_data)

                # Append the position data to the player's position history
                pos_data_history = json.loads(player.pos_data_history)  # Load existing history
                pos_data_history.append(pos_data)  # Append new position
                player.pos_data_history = json.dumps(pos_data_history)  # Save updated history

                # Return acknowledgment to the client
                return {player.id_in_group: dict(
                    event='posCheck',
                    pos_data=pos_data
                )}
                
            # handle phase updates
            elif event == 'phase':
                
                # update phase
                # currentPhase = player.phase
                currentPhase = data["phase"]

                if currentPhase == 0:

                    # increment phase
                    currentPhase = 1
                    player.phase = currentPhase
                    print("Current phase:")
                    print(currentPhase)

                    # get time stamp
                    dateNow = str(datetime.now(tz=timezone.utc).timestamp())

                    # initialize npc bot posiitons
                    pos = initializeNPCPositions()
                    redPos = pos['red']
                    blackPos = pos['black']
                    greenPos = pos['green']
                    playerPos = pos['player']

                    # save to database
                    CharPositionData.create(
                        player=player,
                        msgId='initial',
                        timestamp=dateNow,
                        posPlayer=json.dumps(playerPos),
                        posRed=json.dumps(redPos),
                        posBlack=json.dumps(blackPos),
                        posGreen=json.dumps(greenPos),
                    )

                    return {player.id_in_group: dict(
                        event='phase',
                        phase=currentPhase,
                        posPlayer=json.dumps(playerPos),
                        posRed=json.dumps(redPos),
                        posBlack=json.dumps(blackPos),
                        posGreen=json.dumps(greenPos),
                    )}
                
                
                else:
                    pass


class Decision(Page):
    form_model = 'player'
    form_fields = ['budgeted_cost', 'budgeted_emissions', 'justification']

    @staticmethod
    def vars_for_template(player: Player):
        # Ensure cost_of_goods_sold and emissions are calculated
        calculate_cost_of_goods_sold(player)

        # Retrieve chat messages for the current player
        chat_messages = MessageData.filter(player=player)

        # Format the messages for display
        formatted_messages = [
            {
                'sender': msg.sender,
                'text': msg.msgText,
                'timestamp': msg.timestamp,
            }
            for msg in chat_messages
        ]

        return dict(
            cost_of_goods_sold=player.cost_of_goods_sold,
            cost_of_goods_sold_emissions=player.cost_of_goods_sold_emissions,
            chat_messages=formatted_messages,  # Pass chat messages to the template
        )

class Controls(Page):
    form_model = 'player'
    form_fields = [
        'age',
        'gender',
        'qualification',
        'controlling_experience',
    ]

class Checks(Page):
    form_model = 'player'
    form_fields = [
        'impact_focus',
        'impact_transparency',
    ]

class Thanks(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Display the Thanks page in two cases:
        # 1. If the player failed the knowledge check
        # 2. If this is the final page after the Controls page
        if player.participant.failed_knowledge_check:
            return True

        # Ensure this is the final page in the sequence
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            participant_id=player.participant.code,
            failed_knowledge_check=player.participant.failed_knowledge_check,
        )

# --- Page Sequence -----------------------------------------------------------

page_sequence = [
    Introduction,
    Background,
    Knowledge,
    Sorry,  # Redirect failed participants here
    Condition1,
    Explainer,
    chat,
    Decision,
    Checks,
    Controls,
    Thanks,
]