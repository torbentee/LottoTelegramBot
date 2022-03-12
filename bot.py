import sys
from telegram.ext import Updater
import logging
import shelve
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
import requests
from datetime import datetime, timedelta
import datetime as d
import copy
import os
import math
from enum import Enum

credentials = {}
db_file = 'user'

####################
# Helper functions
####################


def update_db(chatid, newentries):
    idasstring = str(chatid)

    with shelve.open(db_file) as db:
        oldentries = None
        try:
            oldentries = db[idasstring]
        except KeyError:
            oldentries = {}
        oldentries.update(newentries)

        db[idasstring] = oldentries
        logging.info(db[idasstring])


def request_current_jackpot(species=None):
    url = ""
    if (species == Species.EUROJACKPOT):
        url = "https://www.lotto.de/api/stats/entities.eurojackpot/last"
    elif (species == Species.LOTTO):
        url = "https://www.lotto.de/api/stats/entities.lotto/last"
    else:
        result = []
        result.append(request_current_jackpot(Species.EUROJACKPOT))
        result.append(request_current_jackpot(Species.LOTTO))

        return result

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    return (data['jackpotNew'], data['drawDate'])


class Species(Enum):
    EUROJACKPOT = 1
    LOTTO = 2

####################
# Callback functions
####################


def start(update, context):
    logging.info(update.effective_chat.id)
    newentry = {
        'isactive': True
    }
    update_db(update.effective_chat.id, newentry)
    update.message.reply_text(
        "Ok! Let's get a notification for _Eurojackpot_ /help")


def eurojackpot(update, context):
    logging.info(update.effective_chat.id)

    if (len(context.args) == 0):
        jackpot, drawDate = request_current_jackpot(Species.EUROJACKPOT)
        update.message.reply_text(
            "Current eurojackpot: {} mil. €".format(jackpot))
        return

    # TODO verify args
    bound = int(context.args[0])

    user_says = " " + str(bound)
    update.message.reply_text(
        "You will be notified if the eurojackpot is above: " + user_says + " mil. €")

    newentry = {
        'eurojackpot_bottom_bound': bound,
        'euro_lastmessage': datetime(1, 1, 1)
    }
    update_db(update.effective_chat.id, newentry)


def lotto(update, context):
    logging.info(update.effective_chat.id)

    if (len(context.args) == 0):
        jackpot, drawDate = request_current_jackpot(Species.LOTTO)
        update.message.reply_text(
            "Current lotto jackpot: {} mil. €".format(jackpot))
        return

    # TODO verify args
    bound = int(context.args[0])

    user_says = " " + str(bound)
    update.message.reply_text(
        "You will be notified if the lotto jackpot is above: " + user_says + " mil. €")

    newentry = {
        'lottojackpot_bottom_bound': bound,
        'lotto_lastmessage': datetime(1, 1, 1)
    }
    update_db(update.effective_chat.id, newentry)


def poll_eurojackpot(context):
    logging.info("polling")
    import dbm
    try:
        dbm.open(db_file, flag='r')
    except dbm.error:
        logging.warning("database file %s does not exist", db_file)
        return

    database = {}
    with shelve.open(db_file, flag='r', writeback=False) as db:
        database = copy.deepcopy(dict(db))
    jackpots = request_current_jackpot()

    for key in database:
        bound_euro = database[key].get('eurojackpot_bottom_bound') or math.inf
        bound_lotto = database[key].get(
            'lottojackpot_bottom_bound') or math.inf
        euro_lastmessage = database[key].get('euro_lastmessage')
        lotto_lastmessage = database[key].get('lotto_lastmessage')
        jackpot_euro = jackpots[0][0]
        jackpot_lotto = jackpots[1][0]
        drawdate_euro = datetime.fromtimestamp(jackpots[0][1] / 1000.0)
        drawdate_lotto = datetime.fromtimestamp(jackpots[1][1] / 1000.0)

        logging.info(
            {
                "bound_euro": bound_euro,
                "bound_lotto": bound_lotto,
                "eurojackpot": jackpot_euro,
                "lottojackpot": jackpot_lotto,
                "euro_lastmessage": euro_lastmessage,
                "lotto_lastmessage": lotto_lastmessage,
                "drawdate_euro": drawdate_euro,
                "drawdate_lotto": drawdate_lotto
            }
        )
        if (euro_lastmessage == None or euro_lastmessage < drawdate_euro + timedelta(days=1)) and (bound_euro <= jackpot_euro):
            newentry = {
                'euro_lastmessage': datetime.now()
            }
            update_db(key, newentry)
            context.bot.send_message(chat_id=key,
                                     text="The EUROJACKPOT is at {} mil. €".format(jackpot_euro))
            debug = {
                'euro_lastmessage': euro_lastmessage,
                'drawdate_euro': drawdate_euro,
                'bound_euro': bound_euro,
                'jackpot_euro': jackpot_euro
            }
            logging.info(debug)
        if (lotto_lastmessage == None or lotto_lastmessage < drawdate_lotto + timedelta(days=1)) and (bound_lotto <= jackpot_lotto):
            newentry = {
                'lotto_lastmessage': datetime.now()
            }
            update_db(key, newentry)
            context.bot.send_message(chat_id=key,
                                     text="The LOTTOJACKPOT is at {} mil. €".format(jackpot_lotto))


def help(update, context):
    update.message.reply_text("""
    /start - register to use the Lotto News Bot
/help - show this help
/eurojackpot -
/lottojackpot -
/settings -
""")


def settings(update, context):
    reply = ""
    with shelve.open(db_file, flag='c', writeback=False) as db:
        reply = db.get(str(update.effective_chat.id))

    logging.info(str(reply))
    update.message.reply_text(str(reply))

####################
# Main
####################


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    credentials = {
        'telegram_token': os.environ.get('telegram_token')
    }

    logging.info("Startup …")
    updater = Updater(token=credentials['telegram_token'], use_context=True)
    dispatcher = updater.dispatcher
    logging.info("Ready!")

    j = dispatcher.job_queue

    j.run_repeating(poll_eurojackpot, interval=1800, first=0)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    eurojackpot_handler = CommandHandler('eurojackpot', eurojackpot)
    dispatcher.add_handler(eurojackpot_handler)
    lotto_handler = CommandHandler('lottojackpot', lotto)
    dispatcher.add_handler(lotto_handler)
    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)
    settings_hanlder = CommandHandler('settings', settings)
    dispatcher.add_handler(settings_hanlder)

    logging.info("Start polling")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
