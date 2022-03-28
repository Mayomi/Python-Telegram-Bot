#!/usr/bin/env python

import logging

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

import ButtonChecker
# Telegram Bot Token
bot_token = ''
# TMDB APIKey
tmdb_apikey = ''
tmdb_timeout = 5

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    text = '回复 /s <搜索内容> 即可搜索指定的剧集/电影\n*更多功能还在开发/优化中..\n使用问题联系：@dyaxy*'
    update.message.reply_markdown(text)


def search(update: Update, context: CallbackContext) -> None:
    try:
        content = context.args
        query = str(context.args[0])
        for i in range(1, len(content)):
            query = query + ' '+context.args[i]
        text, reply_markup = ButtonChecker.onSearch(query)
        update.message.reply_markdown(
            text, reply_markup=reply_markup)

    except (IndexError, ValueError):
        update.message.reply_markdown('🚫*解析错误*🚫 用法: /s <搜索内容>')


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    bot = update.callback_query.bot
    calldata = query.data.split('_')
    calltype = calldata[0]
    print(query.data)
    match calltype:
        case 'again':
            text, reply_markup = ButtonChecker.onSearch(
                calldata[1])
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        case 'search':
            text, reply_markup = ButtonChecker.onSearchResult(
                calldata[1], calldata[2])
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        case 'info':
            text, reply_markup = ButtonChecker.onInfomation(
                calldata[1], calldata[2], calldata[3])
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        case 'watch':
            text, reply_markup = ButtonChecker.onSelectCountry(
                calldata[1], calldata[2])
            bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        case 'country':
            for i in range(2):
                text, reply_markup = ButtonChecker.onOffer(
                calldata[1], calldata[2], calldata[3],i)
                bot.send_message(
                    chat_id=update.effective_message.chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
            )


def main() -> None:
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("s", search))
    dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()