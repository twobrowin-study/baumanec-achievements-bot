import os, sys, json, dotenv
from telegram.ext import CallbackQueryHandler
from spreadsheetbot import Log, DEBUG

from users import UsersAdapterClass
from spreadsheetbot_ext import SpreadSheetBot
from log_ext import LogSheetAdapterClass
from achievements import Achievements

if "DOCKER_RUN" in os.environ:
    Log.info("Running in docker environment")
else:
    dotenv.load_dotenv()
    Log.info("Running in dotenv environment")

if len(sys.argv) > 1 and sys.argv[1] in ['debug', '--debug', '-D']:
    Log.setLevel(DEBUG)
    Log.debug("Starting in debug mode")

BOT_TOKEN            = os.environ.get('BOT_TOKEN')
SHEETS_ACC_JSON      = json.loads(os.environ.get('SHEETS_ACC_JSON'))
SHEETS_LINK          = os.environ.get('SHEETS_LINK')
SWITCH_UPDATE_TIME   = int(os.environ.get('SWITCH_UPDATE_TIME'))
SETTINGS_UPDATE_TIME = int(os.environ.get('SETTINGS_UPDATE_TIME'))

if __name__ == "__main__":
    bot = SpreadSheetBot(
        BOT_TOKEN,
        SHEETS_ACC_JSON,
        SHEETS_LINK,
        SWITCH_UPDATE_TIME,
        SETTINGS_UPDATE_TIME
    )
    bot.run_polling(
        extra_user_handlers = [
            CallbackQueryHandler(
                callback = UsersAdapterClass.achivment_manufacture_list_callback,
                pattern  = Achievements.CALLBACK_ACHIEVMENT_MANUFACTURE_PATTERN,
                block    = False
            )
        ]
    )