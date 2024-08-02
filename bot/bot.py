#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import ForceReply, Update
import os
import logging
import requests
from datetime import datetime
from requests import Request, Session
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_token():
    dict_raw_data = {}
    cokie = ""
    mydb = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_DATABASE'),
    )

    mycursor = mydb.cursor()
    mycursor.execute("SELECT token FROM tokens")
    myresult = mycursor.fetchone()
    lines = myresult[0].split('\\')
    for line in lines:
        if line.find('--data-raw') > -1:
            raw_data = line.split('--data-raw')[1].strip().strip("'")
            params = raw_data.split('&')
            for param in params:
                dict_raw_data[param.split('=')[0]] = param.split('=')[1]
        if line.find('cookie:') > -1:
            cokie = line.split('cookie:')[1].strip().strip("'")

    mycursor.close()
    mydb.close()
    return (dict_raw_data, cokie)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

last_call = datetime.now()

# Define a few command handlers. These usually take the two arguments update and
# context.


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    global last_call

    cc = update.message.text.lstrip("/pp").strip()
    cc_infos = cc.split("|")

    if len(cc_infos) == 4 and len(cc_infos[0]) == 16 and len(cc_infos[1]) == 2 and len(cc_infos[2]) == 2 and len(cc_infos[3]) == 3:

        time_delta_obj = datetime.now() - last_call
        diff_in_mins = int(time_delta_obj.total_seconds()/60)
        waiting_mins = 3

        if diff_in_mins < waiting_mins:
            await update.message.reply_text("Try again after " + str(waiting_mins - diff_in_mins) + " minutes")
        else:
            params = get_token()
            token = params[1]
            raw_data = params[0]
            last_call = datetime.now()
            url = 'https://checkout.steampowered.com/checkout/inittransaction/'

            raw_data['PaymentMethod'] = 'visa' if cc_infos[0][0] == "4" else "mastercard"
            raw_data['CardNumber'] = cc_infos[0]
            raw_data['CardExpirationYear'] = '20' + cc_infos[2]
            raw_data['CardExpirationMonth'] = cc_infos[1]

            headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                       "cookie": token}
            response = requests.post(url, headers=headers, data=raw_data)
            declined_result = """⚜️Card ➔  """ + cc + """
⚜️Status ➔  𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌ 
⚜️Gateway ➔   Paypal 0.1 $ 
⚜️Response ➔  
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
⚜️Bank Info ➔   Pnc Bank, National Association 
⚜️Country ➔  United States of America (the) 🇺🇸
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
⚜️Free Bins ➔ @BinPost
⚜️Free CCs ➔ @RandomCreditCards
⚜️Buy ➔  @PremiumChecker"""
            approved_result = """
✨Card ➔ """ + cc + """
✨Status ➔  APPROVED ⚡️ 
✨Gateway ➔   Paypal 0.1 $ 
✨Response ➔ VALID_BILLING_ADDRESS ✅
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
✨Bin ➔ VISA;CREDIT;PLATIUM
✨Bank Info ➔   AU  Bank 
✨Country ➔  Australia
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""
            await update.message.reply_text(approved_result if response.json()["success"] == 1 else declined_result)
    else:
        await update.message.reply_text("Credit card is not correct " + cc)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(
        "7437575787:AAGTMpWsOP1lo1gEEhEBPUvMzHbdJ0_qFJw").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("pp", check_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
