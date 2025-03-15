import os
import logging
import redis
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from ChatGPT_HKBU import HKBU_ChatGPT

# 添加的全局常量
BASICURL = "https://genai.hkbu.edu.hk/general/rest"
MODELNAME = "gpt-4-o-mini"
APIVERSION = "2024-05-01-preview"

# 全局变量
global redis1

def main():
    """
    主函数：初始化 Telegram 机器人，Redis 连接，以及 ChatGPT。
    """
    # ----------------------- 加载环境变量 -----------------------
    telegram_token = os.getenv("TELEGRAM_ACCESS_TOKEN")
    if not telegram_token:
        raise RuntimeError("未设置 TELEGRAM_ACCESS_TOKEN 环境变量")

    redis_host = os.getenv("REDIS_HOST")
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_port = int(os.getenv("REDIS_PORT", "16678"))
    decode_responses = os.getenv("REDIS_DECODE_RESPONSE", "true").lower() == "true"
    redis_username = os.getenv("REDIS_USERNAME", "")

    chatgpt_token = os.getenv("CHATGPT_ACCESS_TOKEN")
    if not chatgpt_token:
        raise RuntimeError("未设置 CHATGPT_ACCESS_TOKEN 环境变量")
    
    # ----------------------- 初始化 Telegram 机器人 -----------------------
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher

    # ----------------------- 初始化 Redis 客户端 -----------------------
    global redis1
    redis1 = redis.Redis(
        host=redis_host,
        password=redis_password,
        port=redis_port,
        decode_responses=decode_responses,
        username=redis_username
    )

    # ----------------------- 初始化 ChatGPT -----------------------
    global chatgpt
    import configparser

    config = configparser.ConfigParser()
    config['CHATGPT'] = {
        'BASICURL': BASICURL,
        'MODELNAME': MODELNAME,
        'APIVERSION': APIVERSION,
        'ACCESS_TOKEN': chatgpt_token
    }
    chatgpt = HKBU_ChatGPT(config)

    
    # ----------------------- 配置日志 -----------------------
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # ----------------------- 注册命令处理器 -----------------------
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))

    # ----------------------- 注册 ChatGPT 处理器 -----------------------
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # ----------------------- 启动机器人 -----------------------
    updater.start_polling()
    updater.idle()

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Helping you helping you.')

def hello_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Good day, Kevin!')

def add(update: Update, context: CallbackContext) -> None:
    """
    /add 命令：增加关键字计数。
    """
    try:
        global redis1
        msg = context.args[0]
        logging.info("Received keyword: %s", msg)

        redis1.incr(msg)
        count = redis1.get(msg)

        update.message.reply_text(f'You have said {msg} for {count} times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def equiped_chatgpt(update, context):
    """
    非命令文本消息处理函数。
    """
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

if __name__ == '__main__':
    main()
