from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application
import pandas as pd

from spreadsheetbot.sheets.abstract import AbstractSheetAdapter
from spreadsheetbot.sheets.i18n import I18n
from spreadsheetbot.sheets.settings import Settings
from spreadsheetbot.sheets.users import Users

class AchievementsAdapterClass(AbstractSheetAdapter):
    CALLBACK_ACHIEVMENT_MANUFACTURE_PREFIX   = 'achievment_manufacture_'
    CALLBACK_ACHIEVMENT_MANUFACTURE_TEMPLATE = 'achievment_manufacture_{achievment_id}'
    CALLBACK_ACHIEVMENT_MANUFACTURE_PATTERN  = 'achievment_manufacture_[0-9]+'

    def __init__(self) -> None:
        super().__init__('achievements', 'achievements', initialize_as_df=True)
        self.uid = 'chat_id'
        self.wks_row_pad = 2
        self.selector = lambda chat_id: self.as_df.chat_id == str(chat_id)
    
    async def _pre_async_init(self):
        self.sheet_name = I18n.achievements
        self.update_sleep_time = Settings.achievements_update_time
        self.retry_sleep_time  = self.update_sleep_time // 2
    
    async def _get_df(self) -> pd.DataFrame:
        df = pd.DataFrame(await self.wks.get_all_records())
        df.chat_id = df.chat_id.apply(str)
        return df

    def get(self, chat_id: int|str) -> pd.Series:
        return self._get(self.selector(chat_id))
    
    def get_with_status(self, chat_id: int|str, achivment_id: str|int) -> tuple[str,str]:
        achivment = self.as_df.columns[int(achivment_id)]
        return achivment, self.get(chat_id)[achivment]
    
    def get_user_achievements_to_show(self, chat_id: int|str) -> list[str]:
        return [
            f"- {achivment}" if status != I18n.issued_notified_to_manufacture else f"- {achivment}, {I18n.sent_to_manufacture}"
            for achivment,status in self.get(chat_id).to_dict().items()
            if status in [I18n.issued_to_notify, I18n.issued_notified, I18n.issued_notified_to_manufacture] and achivment not in ['chat_id', 'name']
        ]
    
    def get_user_achievements_manufacture_inline_keyboard(self, chat_id: int|str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text = 
                    f"{achivment.replace('*','')} {I18n.send_to_manufacture}"
                    if status != I18n.issued_notified_to_manufacture 
                    else f"{achivment.replace('*','')} {I18n.remove_from_manufacture}",
                callback_data = 
                    self.CALLBACK_ACHIEVMENT_MANUFACTURE_TEMPLATE.format(achievment_id = self.as_df.columns.get_loc(achivment))
            )]
            for achivment,status in self.get(chat_id).to_dict().items()
            if status in [I18n.issued_to_notify, I18n.issued_notified, I18n.issued_notified_to_manufacture] and achivment not in ['chat_id', 'name']
        ])
    
    def get_user_achievements_to_notify(self, chat_ids: list[str]) -> list[tuple[str, str]]:
        return [
            (
                user_achvements.chat_id,
                Settings.achievements_issued_message_template.format(
                    template = '\n'.join([
                        f"- {achivment}"
                        for achivment, status in user_achvements.to_dict().items()
                        if status == I18n.issued_to_notify and achivment not in ['chat_id', 'name']
                    ])
                )
            )
            for _,user_achvements in self.as_df.iloc[1:].iterrows()
            if I18n.issued_to_notify in user_achvements.unique() and user_achvements.chat_id in chat_ids
        ] + [
            (
                user_achvements.chat_id,
                Settings.achievements_withdrawn_message_template.format(
                    template = '\n'.join([
                        f"- {achivment}"
                        for achivment, status in user_achvements.to_dict().items()
                        if status == I18n.withdrawn_to_notify and achivment not in ['chat_id', 'name']
                    ])
                )
            )
            for _,user_achvements in self.as_df.iloc[1:].iterrows()
            if I18n.withdrawn_to_notify in user_achvements.unique() and user_achvements.chat_id in chat_ids
        ]
    
    def get_user_achievement_notify_inline_keyboard(self, chat_id: int|str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=f"{achivment.replace('*','')} {I18n.send_to_manufacture}",
                    callback_data = 
                        self.CALLBACK_ACHIEVMENT_MANUFACTURE_TEMPLATE.format(achievment_id = self.as_df.columns.get_loc(achivment))
                )
            ]
            for achivment,status in self.get(chat_id).to_dict().items()
            if status == I18n.issued_to_notify and achivment not in ['chat_id', 'name']
        ])

    async def notifications_set_done(self, app: Application, chat_id: int|str) -> None:
        await self._batch_update_or_create_record(
            chat_id, None, None, app,
            **({
                achivment: I18n.issued_notified
                for achivment,status in self.get(chat_id).to_dict().items()
                if status == I18n.issued_to_notify and achivment not in ['chat_id', 'name']
            } | {
                achivment: I18n.withdrawn_notified
                for achivment,status in self.get(chat_id).to_dict().items()
                if status == I18n.withdrawn_to_notify and achivment not in ['chat_id', 'name']
            })
        )

Achievements = AchievementsAdapterClass()