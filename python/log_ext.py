from datetime import datetime

from spreadsheetbot.basic.log import Log
from spreadsheetbot.sheets.log import LogSheetAdapterClass

async def write(self, chat_id: int|str, message: str):
    row = int(await self._next_available_row())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update = self._prepare_batch_update([
        (row, self.timestamp_col, timestamp),
        (row, self.chat_id_col, chat_id),
        (row, self.message_col, message),
    ])
    await self.wks.batch_update(update)
    Log.info(f"Wrote to {self.name} log {row=} database chat_id: {chat_id} message: {message}")
LogSheetAdapterClass.write = write
