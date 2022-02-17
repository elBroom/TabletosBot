from telegram.ext import (
    CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, InlineQueryHandler,
)

from commands import (
    start_command, help_command, list_command,
    setting_command, new_command, alert_command,
    clean_command, stop_command,
)


handlers = [
    CommandHandler('start', start_command.start_command),
    CommandHandler('setting', setting_command.setting_command),
    CommandHandler('help', help_command.help_command),
    CommandHandler('clean', clean_command.clean_command),
    CommandHandler('stop', stop_command.stop_command),
    ConversationHandler(
        entry_points=[CommandHandler('new', new_command.new_command)],
        states={
            new_command.PILLNAME: [MessageHandler(Filters.regex('^[\w]+$'), new_command.set_pill_name)],
            new_command.PILLDOSAGE: [MessageHandler(Filters.regex('^[0-9.,]+(мг|г|mg|g)$'), new_command.set_pill_dosage)],
            new_command.PILLTIME: [MessageHandler(Filters.regex('^[0-2][0-9]:[0-6][0-9]$'), new_command.set_pill_time)],
        },
        fallbacks=[CommandHandler('cancel', new_command.cancel)],
    ),

    CommandHandler('list', list_command.list_command),
    CallbackQueryHandler(list_command.mod_on_query, pattern='^on [0-9]+$'),
    CallbackQueryHandler(list_command.mod_off_query, pattern='^off [0-9]+$'),
    CallbackQueryHandler(list_command.delete_query, pattern='^delete [0-9]+$'),
]
