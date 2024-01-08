import logging
import os
import sys
from datetime import datetime

from telegram.ext import Application, CommandHandler

from helper import update_db,request_current_jackpot,poll_eurojackpot,Species,getFullConfig

credentials = {}

async def start(update, context):
    logging.info(update.effective_chat.id)
    newentry = {
        'isactive': True
    }
    update_db(update.effective_chat.id, newentry)
    await update.message.reply_text(
        "Ok! Let's get a notification for _Eurojackpot_ /help")


async def eurojackpot(update, context):
    logging.info(update.effective_chat.id)

    if (len(context.args) == 0):
        jackpot, drawDate = request_current_jackpot(Species.EUROJACKPOT)
        await update.message.reply_text(
            "Current eurojackpot: {} mil. €".format(jackpot))
        return

    # TODO verify args
    bound = int(context.args[0])

    user_says = " " + str(bound)
    await update.message.reply_text(
        "You will be notified if the eurojackpot is above: " + user_says + " mil. €")

    newentry = {
        'eurojackpot_bottom_bound': bound,
        'euro_lastmessage': datetime(1, 1, 1)
    }
    update_db(update.effective_chat.id, newentry)


async def lotto(update, context):
    logging.info(update.effective_chat.id)

    if (len(context.args) == 0):
        jackpot, drawDate = request_current_jackpot(Species.LOTTO)
        await update.message.reply_text(
            "Current lotto jackpot: {} mil. €".format(jackpot))
        return

    # TODO verify args
    bound = int(context.args[0])

    user_says = " " + str(bound)
    await update.message.reply_text(
        "You will be notified if the lotto jackpot is above: " + user_says + " mil. €")

    newentry = {
        'lottojackpot_bottom_bound': bound,
        'lotto_lastmessage': datetime(1, 1, 1)
    }
    update_db(update.effective_chat.id, newentry)


async def helpHandler(update, context):
    await update.message.reply_text("""
    /start - register to use the Lotto News Bot
/help - show this help
/eurojackpot -
/lottojackpot -
/settings -
""")


async def settings(update, context):
    reply = getFullConfig(update.effective_chat.id)

    logging.info(reply)
    await update.message.reply_text(reply)


async def error_callback(update, context):
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
    application = Application.builder().token(credentials['telegram_token']).build()
    logging.info("Ready!")

    job_queue = application.job_queue
    job_queue.run_repeating(poll_eurojackpot, interval=1800, first=0)

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('eurojackpot', eurojackpot))
    application.add_handler(CommandHandler('lottojackpot', lotto))
    application.add_handler(CommandHandler('help',helpHandler))
    application.add_handler(CommandHandler('settings', settings))

    application.add_error_handler(error_callback)

    logging.info("Start polling")
    application.run_polling()
    application.idle()


if __name__ == "__main__":
    main()
