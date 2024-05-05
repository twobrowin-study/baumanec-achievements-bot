import asyncio
from telegram import Bot
from telegram.ext import Application
from telegram.constants import ParseMode

from spreadsheetbot.sheets.settings import Settings
from spreadsheetbot.sheets.users import Users
from achievements import Achievements

from spreadsheetbot.basic.log import Log

def PerformAndScheldueAchievementsNotifications(app: Application):
    app.create_task(
        _perform_achievements_notifications(app, False),
        {
            'action': 'Perform first achievements notifications'
        }
    )
    ScheldueAchievementsNotifications(app)

def ScheldueAchievementsNotifications(app: Application) -> None:
    app.create_task(
        _scheldue_and_perform_achievements_notification(app),
        {
            'action': 'Perform scheldued achievements notifications'
        }
    )

async def _scheldue_and_perform_achievements_notification(app: Application) -> None:
    await asyncio.sleep(Settings.achievements_update_time)
    ScheldueAchievementsNotifications(app)
    await _perform_achievements_notifications(app, True)

async def _perform_achievements_notifications(app: Application, update_df: bool) -> None:
    bot: Bot = app.bot

    Log.info("Start performing achievements notifications")
    if update_df:
        await Achievements._update_df()
        Log.info("Updated achievements whole df")

    for chat_id, achivements_message in Achievements.get_user_achievements_to_notify(Users.get_users_without_state()):
        Log.info(f"Preforming achivievement notification to user {chat_id=}")
        Log.debug(f"{achivements_message=}")
        await bot.send_message(
            chat_id, achivements_message,
            parse_mode = ParseMode.MARKDOWN,
            reply_markup = Achievements.get_user_achievement_notify_inline_keyboard(chat_id)
        )
        await Achievements.notifications_set_done(app, chat_id)
    Log.info("Done performing achievements notification")