import re

from telegram.ext import (
    CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler,
)

from answers import YES, NO, NOW, TODAY, SKIP
from commands import (
    start_command, help_command, list_command, history_command,
    setting_command, new_command, alert_command, report_command,
    clean_command, stop_command, add_command,
)

regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
regex_dosage = re.compile(r'^[0-9]{1,10}((,|\.)[0-9]{1,4})? ?(мг|г|МЕ|mg|g|ME)$')
regex_date_time = re.compile(f'^((202[0-9]-[0-1][0-9]-[0-3][0-9] )?[0-2][0-9]:[0-5][0-9])|{"|".join(NOW)}|$')
regex_date = re.compile(f'^(202[0-9]-[0-1][0-9]-[0-3][0-9])|{"|".join(TODAY)}$')
regex_time = re.compile(r'^[0-2][0-9]:[0-5][0-9]$')
regex_bool = re.compile(f"^{'|'.join(YES)}|{'|'.join(NO)}$")
regex_skip = re.compile(f"^{'|'.join(SKIP)}$")


handlers = [
    CommandHandler('start', start_command.start_command),
    CommandHandler('help', help_command.help_command),
    CommandHandler('list', list_command.list_command),
    CommandHandler('history', history_command.history_command),
    CommandHandler('report', report_command.report_command),
    CommandHandler('clean', clean_command.clean_command),
    CommandHandler('stop', stop_command.stop_command),
    ConversationHandler(
        entry_points=[CommandHandler('setting', setting_command.setting_command)],
        states={
            setting_command.TIMEZONE: [
                MessageHandler(Filters.regex('^\w+/\w+$'), setting_command.set_timezone),
                MessageHandler(Filters.location, setting_command.set_timezone_from_location),
                MessageHandler(Filters.regex(regex_skip), setting_command.skip_timezone),
            ],
            setting_command.INTERVAL: [
                MessageHandler(Filters.regex('^[0-9]+$'), setting_command.set_interval),
            ],
            setting_command.PHOTO: [
                MessageHandler(Filters.regex(regex_bool), setting_command.set_photo),
            ],
            setting_command.URGENCY: [
                MessageHandler(Filters.regex(regex_bool), setting_command.set_urgency),
            ],
        },
        fallbacks=[CommandHandler('cancel', setting_command.cancel)],
    ),
    ConversationHandler(
        entry_points=[CommandHandler('new', new_command.new_command)],
        states={
            new_command.NAME: [MessageHandler(Filters.regex('^\w+$'), new_command.set_pill_name)],
            new_command.DOSAGE: [MessageHandler(Filters.regex(regex_dosage), new_command.set_pill_dosage)],
            new_command.TIME: [MessageHandler(Filters.regex(regex_time), new_command.set_pill_time)],
            new_command.DATE_SET: [MessageHandler(Filters.regex(regex_bool), new_command.data_setting)],
            new_command.DATE_START: [MessageHandler(Filters.regex(regex_date), new_command.set_date_start)],
            new_command.DATE_END: [MessageHandler(Filters.regex(regex_date), new_command.set_date_end)],
        },
        fallbacks=[CommandHandler('cancel', new_command.cancel)],
    ),

    CallbackQueryHandler(list_command.mod_on_query, pattern=f'^{list_command.ON} [0-9]+$'),
    CallbackQueryHandler(list_command.mod_off_query, pattern=f'^{list_command.OFF} [0-9]+$'),
    CallbackQueryHandler(list_command.delete_query, pattern=f'^{list_command.DELETE} [0-9]+$'),

    ConversationHandler(
        entry_points=[
            CallbackQueryHandler(alert_command.take_photo_query, pattern=f'^{alert_command.TAKEPHOTO} [0-9]+$'),
        ],
        states={
            alert_command.CHECK: [
                MessageHandler(Filters.photo, alert_command.check_photo),
                MessageHandler(Filters.regex(regex_skip), alert_command.skip_photo),
            ],
        },
        fallbacks=[],
    ),
    CallbackQueryHandler(alert_command.take_query, pattern=f'^{alert_command.TAKE} [0-9]+$'),
    CallbackQueryHandler(alert_command.forgot_query, pattern=f'^{alert_command.FORGOT} [0-9]+$'),
    CallbackQueryHandler(alert_command.later_query, pattern=f'^{alert_command.LATER} [0-9]+$'),

    CallbackQueryHandler(history_command.delete_log_query, pattern=f'^{history_command.DELETE} [0-9]+$'),
    ConversationHandler(
        entry_points=[CommandHandler('add', add_command.add_command)],
        states={
            add_command.NAME: [MessageHandler(Filters.regex('^\w+$'), add_command.set_pill_name)],
            add_command.DOSAGE: [MessageHandler(Filters.regex(regex_dosage), add_command.set_pill_dosage)],
            add_command.TIME: [MessageHandler(Filters.regex(regex_date_time), add_command.set_pill_time)],
        },
        fallbacks=[CommandHandler('cancel', add_command.cancel)],
    )
]
