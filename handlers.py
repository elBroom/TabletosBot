import re

from telegram.ext import (
    CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler,
)

from commands import (
    start_command, help_command, list_command, history_command,
    setting_command, new_command, alert_command, report_command,
    clean_command, stop_command,
)

regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


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
                MessageHandler(Filters.regex('^skip|пропустить$'), setting_command.skip_timezone),
                MessageHandler(Filters.regex('^\w+/\w+$'), setting_command.set_timezone),
                MessageHandler(Filters.location, setting_command.set_timezone_from_location),
            ],
            setting_command.INTERVAL: [
                MessageHandler(Filters.regex('^[0-9]+$'), setting_command.set_interval),
            ],
            setting_command.PHOTO: [
                MessageHandler(Filters.regex('^да|нет|yes|no|y|n$'), setting_command.set_photo),
            ],
            setting_command.URGENCY: [
                MessageHandler(Filters.regex('^да|нет|yes|no|y|n$'), setting_command.set_urgency),
            ],
        },
        fallbacks=[CommandHandler('cancel', setting_command.cancel)],
    ),
    ConversationHandler(
        entry_points=[CommandHandler('new', new_command.new_command)],
        states={
            new_command.NAME: [MessageHandler(Filters.regex('^\w+$'), new_command.set_pill_name)],
            new_command.DOSAGE: [MessageHandler(
                Filters.regex('^[0-9]{1,10}((,|\.)[0-9]{1,4})? ?(мг|г|mg|g)$'), new_command.set_pill_dosage,
            )],
            new_command.TIME: [MessageHandler(Filters.regex('^[0-2][0-9]:[0-6][0-9]$'), new_command.set_pill_time)],
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
                MessageHandler(Filters.regex('^skip|пропустить$'), alert_command.skip_photo),
            ],
        },
        fallbacks=[],
    ),
    CallbackQueryHandler(alert_command.take_query, pattern=f'^{alert_command.TAKE} [0-9]+$'),
    CallbackQueryHandler(alert_command.forgot_query, pattern=f'^{alert_command.FORGOT} [0-9]+$'),
    CallbackQueryHandler(alert_command.later_query, pattern=f'^{alert_command.LATER} [0-9]+$'),

    CallbackQueryHandler(history_command.delete_log_query, pattern=f'^{history_command.DELETE} [0-9]+$'),
]
