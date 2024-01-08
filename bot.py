import logging
import os
import sys
from datetime import datetime

from telegram.ext import CommandHandler, Updater

from helper import update_db,request_current_jackpot,poll_eurojackpot,Species,getFullConfig

credentials = {}

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


def help(update, context):
    update.message.reply_text("""
    /start - register to use the Lotto News Bot
/help - show this help
/eurojackpot -
/lottojackpot -
/settings -
""")


def settings(update, context):
    reply = getFullConfig(update.effective_chat.id)

    logging.info(reply)
    update.message.reply_text(reply)


def error_callback(update, context):
    logging.warning('Update "%s" caused error "%s"', update, context.error)

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

    dispatcher.add_error_handler(error_callback)

    logging.info("Start polling")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
