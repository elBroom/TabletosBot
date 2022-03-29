from telegram import ReplyKeyboardMarkup

YES = ('да', 'д', 'yes', 'y')
NO = ('нет', 'н', 'not', 'n')
NOW = ('сейчас', 'now')
TODAY = ('сегодня', 'today')
SKIP = ('пропустить', 'skip')
MEASURING_RUS = ('мг', 'г', 'ME', 'мл', 'амп', 'таб')
MEASURING_EN = ('mg', 'g', 'ME', 'ml', 'аmp', 'tab')

markup_bool = ReplyKeyboardMarkup([[YES[0], NO[0]]], one_time_keyboard=True)
markup_skip = ReplyKeyboardMarkup([[SKIP[0]]], one_time_keyboard=True)
markup_now = ReplyKeyboardMarkup([[NOW[0]]], one_time_keyboard=True)
markup_today = ReplyKeyboardMarkup([[TODAY[0]]], one_time_keyboard=True)
