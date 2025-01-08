# Бот ачивок ДОЛ Бауманец

## Функциональное наполнение доступно в описании основной библиотеки [Spread Sheet Bot](https://github.com/twobrowin-study/spreadsheetbot-lib)

Также добавлено управление ачивками на основе статусной модели:

* Не выдано
* Выдано, отправить уведомление
* Выдано, уведомление отправлено
* Выдано, заказано изготовление, уведомление отправлено
* Отозвано, отправить уведомление
* Отозвано, уведомление отправлено
* Требуется определить статус

## Запуск приложения

`python main.py` в директории `python`

Для запуска в режиме отладки могут использоваться флаги `debug`, `--debug`, `-D`.

## Сборка и запуск Docker контейнера

`docker build -t twobrowin/baumanec-achievments-bot:latest .`

`docker push twobrowin/baumanec-achievments-bot:latest`

`helm upgrade --install --debug -n baumanec baumanec-achievements-bot ./charts`

## Зависимости k8s

Следует создать неймспейс `baumanec` и секрет `baumanec-achievements-bot` в нём, поля секрета:

* `bot_token` - токен подключения к Telegram боту

* `sheets_acc_json` - JWT токен подключения к Google Spreadsheet API

* `sheets_link` - Ссылка на подключение к требуемой таблице - боту требуется доступ на запись, может быть передан как в ссылке, так и назначен инстрементами Google Spreadsheet

## Переменные окружения для запуска приложения

* `BOT_TOKEN` - токен подключения к Telegram боту

* `SHEETS_ACC_JSON` - JWT токен подключения к Google Spreadsheet API

* `SHEETS_LINK` - Ссылка на подключение к требуемой таблице - боту требуется доступ на запись, может быть передан как в ссылке, так и назначен инстрементами Google Spreadsheet

* `SWITCH_UPDATE_TIME` - Время обновления стандартной таблицы 

* `SETTINGS_UPDATE_TIME` - Время обновления стандартной таблицы 