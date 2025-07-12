import re

from telegram.ext import (
    CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler,
)

from answers import YES, NO, NOW, TODAY, SKIP, MEASURING_RUS, MEASURING_EN
from commands import (
    start_command, help_command, list_command, history_command,
    setting_command, new_command, alert_command, report_command,
    clean_command, stop_command, add_command,
)

regex_name = re.compile(r'^[\w\- ]{1,40}$')
regex_dosage = re.compile(f"^[0-9]{{1,10}}((,|\.)[0-9]{{1,4}})? ?({'|'.join(MEASURING_RUS+MEASURING_EN)})$")
regex_date_time = re.compile(f'^((202[0-9]-[0-1][0-9]-[0-3][0-9] )?[0-2][0-9]:[0-5][0-9])|{"|".join(NOW)}|$')
regex_date = re.compile(f'^(202[0-9]-[0-1][0-9]-[0-3][0-9])|{"|".join(TODAY+SKIP)}$')
regex_time = re.compile(r'^[0-2][0-9]:[0-5][0-9]$')
regex_bool = re.compile(f"^{'|'.join(YES+NO)}$")
regex_skip = re.compile(f"^{'|'.join(SKIP)}$")


handlers = [
    CommandHandler('start', start_command.start_command),
    CommandHandler('help', help_command.help_command),
    CommandHandler('report', report_command.report_command),
    CommandHandler('report_quarter', report_command.report_last_quarter_command),
    CommandHandler('clean', clean_command.clean_command),
    CommandHandler('stop', stop_command.stop_command),

    ConversationHandler(
        entry_points=[CommandHandler('setting', setting_command.setting_command)],
        states={
            setting_command.TIMEZONE: [
                MessageHandler(filters.Regex('^\w+/\w+$'), setting_command.set_timezone),
                MessageHandler(filters.Regex(regex_skip), setting_command.skip_timezone),
            ],
            setting_command.INTERVAL: [
                MessageHandler(filters.Regex('^[0-9]+$'), setting_command.set_interval),
            ],
            setting_command.URGENCY: [
                MessageHandler(filters.Regex(regex_bool), setting_command.set_urgency),
            ],
        },
        fallbacks=[CommandHandler('cancel', setting_command.cancel)],
    ),

    ConversationHandler(
        entry_points=[CommandHandler('new', new_command.new_command)],
        states={
            new_command.NAME: [MessageHandler(filters.Regex(regex_name), new_command.set_pill_name)],
            new_command.DOSAGE: [MessageHandler(filters.Regex(regex_dosage), new_command.set_pill_dosage)],
            new_command.TIME: [MessageHandler(filters.Regex(regex_time), new_command.set_pill_time)],
            new_command.DATE_SET: [MessageHandler(filters.Regex(regex_bool), new_command.data_setting)],
            new_command.DATE_START: [MessageHandler(filters.Regex(regex_date), new_command.set_date_start)],
            new_command.DATE_END: [MessageHandler(filters.Regex(regex_date), new_command.set_date_end)],
        },
        fallbacks=[CommandHandler('cancel', new_command.cancel)],
    ),

    CommandHandler('list', list_command.list_command),
    CommandHandler('list_active', list_command.active_list_command),
    CommandHandler('list_waiting', list_command.waiting_list_command),
    CallbackQueryHandler(list_command.mod_on_query, pattern=f'^{list_command.ON} [0-9]+$'),
    CallbackQueryHandler(list_command.mod_off_query, pattern=f'^{list_command.OFF} [0-9]+$'),
    CallbackQueryHandler(list_command.delete_query, pattern=f'^{list_command.DELETE} [0-9]+$'),

    CommandHandler('history', history_command.history_command),
    CallbackQueryHandler(history_command.delete_log_query, pattern=f'^{history_command.DELETE} [0-9]+$'),

    ConversationHandler(
        entry_points=[CommandHandler('add', add_command.add_command)],
        states={
            add_command.NAME: [MessageHandler(filters.Regex(regex_name), add_command.set_pill_name)],
            add_command.DOSAGE: [MessageHandler(filters.Regex(regex_dosage), add_command.set_pill_dosage)],
            add_command.TIME: [MessageHandler(filters.Regex(regex_date_time), add_command.set_pill_time)],
        },
        fallbacks=[CommandHandler('cancel', add_command.cancel)],
    ),

    CallbackQueryHandler(alert_command.take_query, pattern=f'^{alert_command.TAKE} [0-9]+$'),
    CallbackQueryHandler(alert_command.forgot_query, pattern=f'^{alert_command.FORGOT} [0-9]+$'),
    CallbackQueryHandler(alert_command.later_query, pattern=f'^{alert_command.LATER} [0-9]+$'),
]
