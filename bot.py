import logging
import spacy
import re
import random
from iexfinance.stocks import Stock
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu import config
from rasa_nlu.model import Trainer
INIT = 0

# Define the CHOOSE_COFFEE state
CHOOSE_COFFEE = 1

# Define the ORDERED state
NEXT = 2
ORDER = 3
MORE1 = 4
MORE2 = 5
# Define the policy rules

state = INIT
new = "default"
before_sym = 'none'
before_com = 'none'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = "953755326:AAFEJ6PW2wVuLjDs3HLuPRnSf1QLgJMkQmU"

# Create a trainer
trainer = Trainer(config.load("config_spacy.yml"))

# Load the training data
training_data = load_data('demo-rasa.json')

# Create an interpreter by training the model
interpreter = trainer.train(training_data)

class LastMessage:
    mes = None

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, you can ask me about finance!")

def replace_pronouns(message):#反问
    if '\b(I)\b' in message:
        # Replace 'me' with 'you'
        return message.replace('me','you')
    if '\b(my)\b' in message:
        # Replace 'my' with 'your'
        return message.replace('my','your')
    if '\b(your)\b' in message:
        # Replace 'your' with 'my'
        return message.replace('your','my')
    if 'you' in message:
        # Replace 'you' with 'me'
        return message.replace('you','I')
    return message

def match_intent(message):#正常交流
    matched_intent = None
    for intent, pattern in patterns.items():
        msg=message.lower()
        if pattern.search(msg):
            matched_intent = intent
    return matched_intent


def find_name(message):#找名字
    name = None
    first=message[0].lower()
    message = first + message[1:]
    print(message)
    name_keyword = re.compile("(my name)|call|i'm")
    name_pattern = re.compile('([A-Z]{1}[a-z]*)')
    if name_keyword.search(message):
        name_words =name_pattern.findall(message)
        if len(name_words) > 0:
            name = ' '.join(name_words)
    print(name)
    return name

def communicate(message,intent):
    print(intent)
    name = find_name(message) 
    print(intent)
    if name is None:
        key = "default"
        print(intent)
        print("1")
        if intent in responses:
            key = intent
        response=random.choice(responses[key])
    else:
        response=random.choice(responses['answer']).format(name)
    return response

def interprett(message):#找股票
    msg = message.lower()
    if 'apple' in msg:
        return 'AAPL','Apple'
    elif 'amazon' in msg:
        return 'AMZN','Amazon'
    elif 'facebook' in msg:
        return 'FB','Facebook'
    elif 'tesla' in msg:
        return 'TSLA','Tesla'
    return 'none','none'

def price_search(message):
    sym,com = interprett(message)
    if com == 'none':
        com = before_com
    if sym == 'none':
        sym = before_sym
    print(com)
    sta = state
    if sym != 'none':
        a = Stock(sym, token="sk_cd1ee4400c84417caa776e1222f3d350")
        print(a.get_quote())
        word, data = divide(message)
        if data !='none':
            message=com + word + str(a.get_quote()[data])
        else:
            sta = MORE2
    else:
        sta = MORE1
    return message,com,sym,sta
def divide(message):
    msg = message.lower()
    if 'latest price' in msg:
        return "'s latest price is ",'latestPrice'
    elif 'extended price' in msg:
        return "'s extended price is ",'extendedPrice'
    elif 'high' in msg:
        return "'s high price is ",'high'
    elif 'low' in msg:
        return "'s low price is ",'low'
    elif 'open price' in msg:
        return "'s open price is ",'open'
    elif 'close price' in msg:
        return "'s close price is ",'close'
    else:
        return 'none','none'


def respond(bot, update):
    LastMessage.mes = update.message.text
    #bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
    print("Message is:{}".format(LastMessage.mes))
    global state
    global new
    global before_sym
    global before_com
    intent = (interpreter.parse(update.message.text))['intent']['name']
    r= (interpreter.parse(update.message.text))
    print(r)
    if (intent == 'price_search') | (intent == 'affirm') | (intent == 'deny'):
        print(intent)
        if intent == 'price_search':
            new,before_com,before_sym,state = price_search(update.message.text)
        policy = {
            (INIT, "price_search"): (CHOOSE_COFFEE, "ok, sure?"),
            (CHOOSE_COFFEE, "affirm"): (NEXT, new + "Do you want to know more?"),
            (NEXT, "price_search"): (INIT, new),
            (CHOOSE_COFFEE, "price_search"): (INIT, new),
            (MORE1, "price_search"):(CHOOSE_COFFEE,"ok, sure?"),
            (MORE2, "price_search"):(INIT,"what do you want to know about it?"),
            (NEXT, "deny"): (INIT, "byebye"),
            (NEXT, "affirm"): (CHOOSE_COFFEE, "what do you want to know?"),
            (CHOOSE_COFFEE, "deny"): (INIT, "byebye"),
        }
        new_state, update.message.text = policy[(state, intent)]
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
        state = new_state
        print("1")
    else:
        print(intent)
        print("2")
        print(intent)
        update.message.text=communicate(update.message.text,intent)
        print(intent)
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

        
keywords = {
            'greet': [r'\b(hello)\b', r"\b(hi)\b", r'\b（hey）\b',], 
            'thankyou': ['thank', 'thx'], 
            'ask':['your name'],
            'call':['tombli_bot'],
            'goodbye': ['bye', 'farewell']

           }
# Define a dictionary of patterns
patterns = {}

# Iterate over the keywords dictionary
#for intent , keys in keywords.items():
    # Create regular expressions and compile them into pattern objects
    #patterns[intent] = re.compile("|".join(keys))

responses = {'greet': ['Hello you! :)','Hello!'], 
             'thankyou': ["It's my pleasure", 'You are very welcome'], 
             'default': ['What do you mean?🤔','What are you talk about?','Sry I have no idea',"🙏"], 
             'answer': ['Hello, {0}!😄','{0},Nice to meet you!☺️'],
             'ask':['My name is Tombli_bot!😄'],
             'call':["I'm here, What can I do for you?"],
             'goodbye': ['Goodbye for now','See you later~']
            }



updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
chat_handler = MessageHandler(Filters.text, respond)
dispatcher.add_handler(chat_handler)
dispatcher.add_handler(start_handler)

updater.start_polling()
