from telegram.ext import Application

from spreadsheetbot import SpreadSheetBot

from achievements import Achievements
from achievements_notify import PerformAndScheldueAchievementsNotifications

SpreadSheetBot.default_post_init = SpreadSheetBot.post_init
async def post_init(self: SpreadSheetBot, app: Application) -> None:
    await self.default_post_init(app)
    await Achievements.async_init(self.sheets_secret, self.sheets_link)
    PerformAndScheldueAchievementsNotifications(app)
SpreadSheetBot.post_init = post_init
