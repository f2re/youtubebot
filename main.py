#!/usr/bin/env python
import os
from dotenv import load_dotenv
from pytube.cli import on_progress
import telebot
from pytube import YouTube
from paramiko import SSHClient
from scp import SCPClient
import glob

load_dotenv()
bot = telebot.TeleBot( os.getenv('TGBOT') )

def uploadVideoDir():
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect( os.getenv('DST_HOST') , username=os.getenv('DST_USER') )
    scp = SCPClient(ssh.get_transport())
    # scp.put('test.txt', 'test2.txt')
    # scp.get('test2.txt')
    scp.put(os.getenv('DOWNLOADPATH'), recursive=True, remote_path=os.getenv('REMOTE_PATH'))
    scp.close()

    files = glob.glob( os.getenv('DOWNLOADPATH')+'/*')
    for f in files:
        os.remove(f)
        print(f)

# Handles all messages which text matches the regex regexp.
# See https://en.wikipedia.org/wiki/Regular_expression
# This regex matches all sent url's.
@bot.message_handler(regexp='((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)')
def command_url(message):
    txt_ = message.text
    if txt_.find('youtube.com')!= -1 or txt_.find('youtu.be') != -1:
        yt = YouTube( txt_, on_progress_callback=on_progress )
        video = yt.streams.get_highest_resolution()
        if video:
            bot.send_message(message.from_user.id, "Начинаю скачивание " + video.default_filename + " ({0:0.2f} MB)".format(video.filesize/(1024*1024)))
            video.download(os.getenv('DOWNLOADPATH'))
            bot.reply_to(message, video.title + ": скачано успешно.")
            # video.default_filename
            uploadVideoDir()
        else:
            bot.reply_to(message, "Не получилось скачать почему-то")
    else:
        bot.reply_to("Похоже это не ссылка на youtube. Я умею загружать только с youtube.")

bot.polling(none_stop=True, interval=0)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Бот для отправки видео с youtube на определенное устройство")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

