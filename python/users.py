from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import requests

from spreadsheetbot.basic.log import Log

from spreadsheetbot.sheets.users import UsersAdapterClass
from spreadsheetbot.sheets.keyboard import Keyboard
from spreadsheetbot.sheets.i18n import I18n
from spreadsheetbot.sheets.settings import Settings

from achievements import Achievements

def get_users_without_state(self: UsersAdapterClass) -> list[str]:
    return self.as_df.loc[self.as_df.state.isin(['', None])].chat_id.values.tolist()
UsersAdapterClass.get_users_without_state = get_users_without_state

async def keyboard_key_handler(self: UsersAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard_row = Keyboard.get(update.message.text)
    chat_id = update.effective_chat.id
    if keyboard_row.function == Keyboard.REGISTER_FUNCTION:
        user = self._get(self.selector(chat_id))
        await update.message.reply_markdown(
            keyboard_row.text_markdown.format(user=self.user_data_markdown(user)),
            reply_markup=self.user_data_inline_keyboard(user)
        )
        return

    condition_column = 'is_active' if keyboard_row.condition in [None, ''] else keyboard_row.condition
    show_button = not self.as_df.loc[
        self.selector(update.message.chat_id) &
        self.selector_condition(condition_column)
    ].empty

    reply_keyboard = Keyboard.reply_keyboard
    if keyboard_row.function == I18n.my_achievements:
        achievements = Achievements.get_user_achievements_to_show(chat_id)
        if len(achievements) == 0:
            message = keyboard_row.text_markdown.format(achievements = I18n.no_achievements)
        else:
            message = keyboard_row.text_markdown.format(achievements = '\n'.join(achievements))
            reply_keyboard = Achievements.get_user_achievements_manufacture_inline_keyboard(chat_id)
        await update.message.reply_markdown(message, reply_markup=reply_keyboard)
        return

    if keyboard_row.state not in [None, ''] and show_button == True:
        reply_keyboard = Keyboard.get_inline_keyboard_by_state(keyboard_row.state)
    
    if keyboard_row.send_picture == '' and keyboard_row.send_document == '' and keyboard_row.send_document_file_id == '':
        await update.message.reply_markdown(
            keyboard_row.text_markdown,
            reply_markup=reply_keyboard
        )
        return

    if keyboard_row.send_document_file_id != '':
        await update.message.reply_document(
            keyboard_row.send_document_file_id,
            caption=keyboard_row.text_markdown,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_keyboard
        )
        return

    if keyboard_row.send_document != '':
        Log.info(f"Downloading document {keyboard_row.send_document} by key {keyboard_row.key}")
        responce = requests.get(keyboard_row.send_document)
        responce.raise_for_status()
        filename = '__.pdf'
        if 'content-disposition' in responce.headers:
            filename = responce.headers['content-disposition'].removeprefix('attachment; filename=').replace('"', '')
        
        message = await update.message.reply_document(
            responce.content,
            caption=keyboard_row.text_markdown,
            filename=filename,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_keyboard
        )

        file_id = message.document.file_id
        Log.info(f"Updating keyboard document - setting file id {file_id} by key {keyboard_row.key}")
        Keyboard.wks_row_pad = 2
        Keyboard.wks_col_pad = 1
        Keyboard.uid_col     = 'key'
        await Keyboard._update_record(keyboard_row.key, 'send_document_file_id', file_id)

        return

    if keyboard_row.send_picture != '' and len(keyboard_row.text_markdown) <= 1024:
        await update.message.reply_photo(
            keyboard_row.send_picture,
            caption=keyboard_row.text_markdown,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_keyboard
        )
        return

    if keyboard_row.send_picture != '' and len(keyboard_row.text_markdown) > 1024:
        await update.message.reply_markdown(
            keyboard_row.text_markdown
        )
        await update.message.reply_photo(
            keyboard_row.send_picture,
            reply_markup=reply_keyboard
        )
        return
UsersAdapterClass.keyboard_key_handler = keyboard_key_handler

async def achivment_manufacture_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    achivment_id = update.callback_query.data.removeprefix(Achievements.CALLBACK_ACHIEVMENT_MANUFACTURE_PREFIX)
    chat_id = update.effective_chat.id
    
    achivment, achivment_status = Achievements.get_with_status(chat_id, achivment_id)
    
    Log.info(f"Got achivment manufacture update for {achivment=} and {chat_id=} and {achivment_status=}")
    
    if achivment_status in [I18n.issued_to_notify, I18n.issued_notified]:
        await Achievements._update_record(chat_id, achivment, I18n.issued_notified_to_manufacture)
    
    elif achivment_status in [I18n.issued_notified_to_manufacture]:
        await Achievements._update_record(chat_id, achivment, I18n.issued_notified)
    
    old_reply_markup = update.effective_message.reply_markup

    if old_reply_markup:
        reply_markup = InlineKeyboardMarkup([
            [
                butt if butt.callback_data != update.callback_query.data
                     else InlineKeyboardButton(
                        text =
                            Settings.remove_from_manufacture_template.format(achievement = achivment.replace('*',''))
                                if achivment_status != I18n.issued_notified_to_manufacture 
                            else Settings.send_to_manufacture_template.format(achievement = achivment.replace('*','')),
                        callback_data = update.callback_query.data
                     )
            ]
            for row in old_reply_markup.inline_keyboard
            for butt in row
        ])
    else:
        reply_markup = Achievements.get_user_achievements_manufacture_inline_keyboard(chat_id)

    await update.effective_message.edit_reply_markup(reply_markup)
UsersAdapterClass.achivment_manufacture_list_callback = achivment_manufacture_list_callback