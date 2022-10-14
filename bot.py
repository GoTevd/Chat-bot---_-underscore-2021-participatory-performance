from telebot import TeleBot
from texts import Texts
from keyboard import Keyboard
from config import botToken
from mongo import Mongo
from track import main_track_steps
from os import listdir
from datetime import datetime
import random
import threading

bot = TeleBot(botToken, threaded=False)
usersWithQuestions = {}
usersInMainTrack = {}
usersInRandomTrack = {}
usersCreatingTrack = {}
usersSendingClue = {}
mashaChatId = 152303263
startTime = datetime(2021, 5, 5, 15, 15, 0)
mainImg = open('main.jpg', 'rb')

def resetUserStatus(chatId):
    usersSendingClue.pop(chatId, None)
    usersWithQuestions.pop(chatId, None)
    usersCreatingTrack.pop(chatId, None)
    usersInMainTrack.pop(chatId, None)
    usersInRandomTrack.pop(chatId, None)

@bot.message_handler(commands=['start'])
def cmd_welcome(message):
    bot.delete_message(message.chat.id, message.message_id)
    Mongo.getOrCreateUser(message.chat.id)
    await_start(message.chat.id)


def await_start(chatId):
    if datetime.now() < startTime:
        bot.send_message(chatId, Texts.awaiting_start_text, reply_markup=Keyboard.keyboard_start)
    else:
        start(chatId)

def start(chatId):
    bot.send_message(chatId, Texts.welcome_text)
    mainImg.seek(0)
    bot.send_photo(chatId, mainImg, reply_markup=Keyboard.keyboard_main)

@bot.message_handler(func=lambda message: True)
def handleMessage(message):
    chatId = message.chat.id
    bot.delete_message(chatId, message.message_id)
    if chatId in usersWithQuestions:
        receiverId = Mongo.askQuestion(chatId, message.text)
        bot.delete_message(chatId, usersWithQuestions[chatId])
        usersWithQuestions.pop(chatId)
        if receiverId is None:
            print("no users to send question to")
            return
        print("sending question from {0} to {1}".format(chatId, receiverId))
        bot.send_message(receiverId, "Вам сообщение от анонима: {0}".format(message.text))
        Mongo.updateNavigation(chatId, 'main_menu')
        mainImg.seek(0)
        bot.send_photo(chatId, mainImg, reply_markup=Keyboard.keyboard_main)
    elif chatId in usersCreatingTrack:
        bot.delete_message(chatId, usersCreatingTrack[chatId])
        msg = bot.send_message(chatId, Texts.track_next_step_text, reply_markup=Keyboard.keyboard_create_track)
        usersCreatingTrack[chatId][0] = msg.message_id
        usersCreatingTrack[chatId][1].append(message.text)
    elif chatId in usersSendingClue:
        Mongo.appendClue(chatId, message.text)
        bot.delete_message(chatId, usersSendingClue[chatId])
        usersSendingClue.pop(chatId)
        bot.send_message(mashaChatId, "Зацепка от пользователя @{0}: {1}".format(message.chat.username, message.text))
        submit_clue(chatId)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chatId = call.message.chat.id
    bot.delete_message(chatId, message_id=call.message.message_id)
    navId = call.data
    if call.data in {'track_save'}:
        navId = 'main_menu'
    elif call.data in {'fullfill_space', 'send_clue', 'show_image_and_quit', 'cocoon_free', 'cocoon_occupied', 'cocoon_about', 'cocoon_start', 'await_start'}:
        navId = None
    if not navId is None:
        Mongo.updateNavigation(chatId, navId)
    if call.data == 'await_start':
        await_start(chatId)
    if call.data == 'question':
        ask_question(chatId)
    elif call.data == 'main_menu':
        main_menu(chatId)
    elif call.data == 'track':
        create_or_follow_track(chatId)
    elif call.data == 'track_create':
        create_track(chatId)
    elif call.data == 'track_save':
        save_track(chatId)
    elif call.data == 'track_follow_random':
        follow_random_track(chatId)
    elif call.data == 'track_follow_main':
        follow_main_track(chatId)
    elif call.data == 'track_next_step':
        follow_track(chatId)
    elif call.data == 'oldness':
        oldness(chatId)
    elif call.data == 'postrave':
        postrave(chatId)
    elif call.data == 'emptiness':
        emptiness(chatId)
    elif call.data == 'fullfill_space':
        fullfill_space(chatId)
    elif call.data == 'between':
        between(chatId)
    elif call.data == 'investigation':
        investigation(chatId)
    elif call.data == 'send_clue':
        send_clue(chatId)
    elif call.data == 'show_image_and_quit':
        show_image_and_quit(chatId)
    elif call.data == 'cocoon':
        cocoon(chatId)
    elif call.data == 'cocoon_free':
        cocoon_free(chatId)
    elif call.data == 'cocoon_occupied':
        cocoon_occupied(chatId)
    elif call.data == 'cocoon_about':
        cocoon_about(chatId)
    elif call.data == 'cocoon_start':
        cocoon_start(chatId)
    elif call.data == 'new_space':
        new_space(chatId)

def new_space(chatId):
    bot.send_message(chatId, Texts.new_space_text, reply_markup=Keyboard.keyboard_new_space)

def cocoon(chatId):
    bot.send_message(chatId, Texts.cocoon_text, reply_markup=Keyboard.keyboard_cocoon)

def cocoon_free(chatId):
    bot.send_message(chatId, Texts.cocoon_free_text, reply_markup=Keyboard.keyboard_cocoon_free)    

def cocoon_occupied(chatId):
    bot.send_message(chatId, Texts.cocoon_occupied_text, reply_markup=Keyboard.keyboard_cocoon_occupied)

def cocoon_about(chatId):
    bot.send_message(chatId, Texts.cocoon_about_text, reply_markup=Keyboard.keyboard_force_main)

def cocoon_start(chatId):
    msg = bot.send_message(chatId, 'https://t.me/joinchat/AUItoA1iE_Y1YThi')
    threading.Timer(600, delete_message_timeout, [chatId, msg.message_id]).start()

def oldness(chatId):
    count = Mongo.countInRoom('oldness')
    bot.send_message(chatId, Texts.oldness_text.format(count), reply_markup=Keyboard.keyboard_force_main)

def postrave(chatId):
    count = Mongo.countInRoom('postrave')
    bot.send_message(chatId, Texts.postrave_text.format(count), reply_markup=Keyboard.keyboard_force_main)

def emptiness(chatId):
    count = Mongo.countInRoom('emptiness')
    bot.send_message(chatId, Texts.emptiness_text.format(count), reply_markup=Keyboard.keyboard_emptiness)

def fullfill_space(chatId):
    files = [f for f in listdir('voices')]
    file = 'voices/{0}'.format(random.choice(files))
    audio = open(file, 'rb')
    bot.send_audio(chatId, audio)
    bot.send_message(chatId, Texts.fullfill_text, reply_markup=Keyboard.keyboard_fullfill)

def investigation(chatId):
    count = Mongo.countInRoom('investigation')
    bot.send_message(chatId, Texts.investigation_text.format(count), reply_markup=Keyboard.keyboard_investigation)

def submit_clue(chatId):
    bot.send_message(chatId, Texts.clue_submit_text, reply_markup=Keyboard.keyboard_investigation)

def send_clue(chatId):
    msg = bot.send_message(chatId, Texts.clue_text, reply_markup=Keyboard.keyboard_clue)
    usersSendingClue[chatId] = msg.message_id

def show_image_and_quit(chatId):
    files = [f for f in listdir('pic')]
    file = 'pic/{0}'.format(random.choice(files))
    img = open(file, 'rb')
    msg = bot.send_photo(chatId, img)
    threading.Timer(15, delete_message_timeout, [chatId, msg.message_id]).start()

def delete_message_timeout(chatId, messageId):
    bot.delete_message(chatId, messageId)
    Mongo.updateNavigation(chatId, 'main_menu')
    main_menu(chatId)

def between(chatId):
    count = Mongo.countInRoom('between')
    bot.send_message(chatId, Texts.between_text.format(count), reply_markup=Keyboard.keyboard_between)    

def ask_question(chatId):
    msg = bot.send_message(chatId, Texts.question_text)
    usersWithQuestions[chatId] = msg.message_id

def main_menu(chatId):
    resetUserStatus(chatId)
    mainImg.seek(0)
    bot.send_photo(chatId, mainImg, reply_markup=Keyboard.keyboard_main)

def create_or_follow_track(chatId):
    bot.send_message(chatId, Texts.track_text, reply_markup=Keyboard.keyboard_track)

def create_track(chatId):
    msg = bot.send_message(chatId, Texts.track_first_step_text, reply_markup=Keyboard.keyboard_force_main)
    usersCreatingTrack[chatId] = [msg.message_id, []]

def save_track(chatId):
    print("saving user track {0}".format(usersCreatingTrack[chatId][1]))
    Mongo.appendTrack(chatId, usersCreatingTrack[chatId][1])
    main_menu(chatId)

def follow_random_track(chatId):
    track_steps = Mongo.getRandomTrack(chatId)
    if track_steps is None:
        bot.send_message(chatId, 'Пока что зрители не создали ни одного трека', reply_markup=Keyboard.keyboard_force_main)
        return
    usersInRandomTrack[chatId] = [track_steps, 1]
    reply_markup = Keyboard.keyboard_follow_track
    if len(track_steps) == 1:
        reply_markup = Keyboard.keyboard_force_main
    bot.send_message(chatId, track_steps[0], reply_markup=reply_markup)

def follow_main_track(chatId):
    bot.send_message(chatId, Texts.track_in_progress_text, reply_markup=Keyboard.keyboard_force_main)
    # трек ещё не готов
    # usersInMainTrack[chatId] = 1
    # bot.send_message(chatId, main_track_steps[0], reply_markup=Keyboard.keyboard_follow_track)

def follow_track(chatId):
    track_steps = main_track_steps
    step = 0
    if chatId in usersInRandomTrack:
        track_steps = usersInRandomTrack[chatId][0]
        step = usersInRandomTrack[chatId][1]
        usersInRandomTrack[chatId][1] = step + 1
    else:
        step = usersInMainTrack[chatId]
        usersInMainTrack[chatId] = step + 1
    reply_markup = Keyboard.keyboard_follow_track
    if step >= len(track_steps) - 1:
        reply_markup = Keyboard.keyboard_force_main
    bot.send_message(chatId, track_steps[step], reply_markup=reply_markup)

# !!! Временно закомментировано чтобы ctrl+c работал
print("Starting bot")
# bot.polling(none_stop=True)
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        print("Bot failed with error {0}. Restarting".format(err))