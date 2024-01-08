import shelve
import logging
from enum import Enum
import requests
import copy
import math
import json
from datetime import datetime, timedelta

db_file = 'data/user.db'

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
        if (euro_lastmessage == None or euro_lastmessage < drawdate_euro + timedelta(days=1)) and jackpot_euro != None and (bound_euro <= jackpot_euro):
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

        if (lotto_lastmessage == None or lotto_lastmessage < drawdate_lotto + timedelta(days=1)) and jackpot_lotto != None and (bound_lotto <= jackpot_lotto):
            newentry = {
                'lotto_lastmessage': datetime.now()
            }
            update_db(key, newentry)
            context.bot.send_message(chat_id=key,
                                     text="The LOTTOJACKPOT is at {} mil. €".format(jackpot_lotto))


def getFullConfig(chat_id):
    result = ""
    with shelve.open(db_file, flag='c', writeback=False) as db:
        result = db.get(str(chat_id))

    logging.info(result)
    return json.dumps(str(result))
