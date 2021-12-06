import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from sys import executable

from telegram import ParseMode
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.utils.helpers import escape_markdown
from telegraph import Telegraph
from wserver import start_server_async
from Atrocious_Mirror_Bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, PORT, alive, web, OWNER_ID, AUTHORIZED_CHATS, telegraph_token
from Atrocious_Mirror_Bot.helper.ext_utils import fs_utils
from Atrocious_Mirror_Bot.helper.telegram_helper.bot_commands import BotCommands
from Atrocious_Mirror_Bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from Atrocious_Mirror_Bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, torrent_search, delete, speedtest, count, leech_settings


PM_START_TEXT = """
Hello {}, I'm {}
I can mirror all your links to Google drive. But in pm or unauthorized group you can use all telegram upload tools. If you want to upload in Google Drive you need to join Atrocious Cloud Drive.
For commands and help press /help .
"""


def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - botStartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="help_back")]],
                    ),
                )
            elif args[0].lower() == "markdownhelp":
                IMPORTED["extras"].markdown_help_sender(update)
            elif args[0].lower() == "disasters":
                IMPORTED["disasters"].send_disasters(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            last_name = update.effective_user.last_name
            update.effective_message.reply_photo(
                Stats_Photo,
                PM_START_TEXT.format(
                    escape_markdown(first_name), escape_markdown(context.bot.first_name),
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="✅ Add me in your group",
                                url="t.me/{}?startgroup=true".format(
                                    context.bot.username,
                                ),
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="☯️ Cloud Group",
                                url="https://t.me/+WKZqyWNHpLViMmI1",
                            ),
                            InlineKeyboardButton(
                                text="✳ Find More",
                                url="https://github.com/AL-Noman21",
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="🕎 Atrocious Bot Owner",
                                url="https://t.me/smexynos7870",
                            ),
                        ],
                    ],
                ),
            )
    else:
        update.effective_message.reply_text(
            "I'm awake already!\n<b>Haven't slept since:</b> <code>{}</code>".format(
                uptime,
            ),
            parse_mode=ParseMode.HTML,
        )

def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b> 「⭕️ BOT STATISTICS ⭕️」</b>\n' \
            f'<b> </b>\n' \
            f'<b> Bot Uptime :</b> <code>{currentTime}</code>\n\n' \
            f'<b> Total Disk Space :</b> <code>{total}</code>\n' \
            f'<b> Used :</b> <code>{used}</code>\n ' \
            f'<b> Free :</b> <code>{free}</code>\n\n' \
            f'<b> Upload :</b> <code>{sent}</code>\n' \
            f'<b> Download :</b> <code>{recv}</code>\n\n' \
            f'<b> CPU :</b> <code>{cpuUsage}%</code>\n ' \
            f'<b> RAM :</b> <code>{memory}%</code>!\n ' \
            f'<b> DISK :</b> <code>{disk}%</code>!\n ' \
            f'<b> </b>\n' \
            f'<b> 「⭕️ @FlameOSGroup  ⭕️」</b>'
    update.effective_message.reply_photo(Stats_Photo, stats, parse_mode=ParseMode.HTML)

Stats_Photo = "https://telegra.ph/file/c06d92681208824918821.jpg"

def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.terminate()
    web.terminate()
    os.execl(executable, executable, "-m", "Atrocious_Mirror_Bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b>: To get this message
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [download_url][magnet_link]: Start mirroring the link to Google Drive.
<br><br>
<b>/{BotCommands.TarMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [magnet_link]: Start Mirroring using qBittorrent, Use <b>/{BotCommands.QbMirrorCommand} s</b> to select files before downloading
<br><br>
<b>/{BotCommands.QbTarMirrorCommand}</b> [magnet_link]: Start mirroring using qBittorrent and upload the archived (.tar) version of the download
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [magnet_link]: Start mirroring using qBittorrent and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [magnet_link]: Starts mirroring using qBittorrent and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.LeechCommand}</b> This command should be used as reply to Magnet link, Torrent link, or Direct link. [this command will SPAM the chat and send the downloads a seperate files, if there is more than one file, in the specified Torrent]
<br><br>
<b>/{BotCommands.TarLeechCommand}</b> This command should be used as reply to Magnet link, Torrent link, or Direct link and upload it as (.tar). [this command will SPAM the chat and send the downloads a seperate files, if there is more than one file, in the specified Torrent]
<br><br>
<b>/{BotCommands.ZipLeechCommand}</b> This command should be used as reply to Magnet link, Torrent link, or Direct link and upload it as (.zip). [this command will SPAM the chat and send the downloads a seperate files, if there is more than one file, in the specified Torrent]
<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b> This command should be used as reply to Magnet link, Torrent link, or Direct link and if file is any archive, extracts it. [this command will SPAM the chat and send the downloads a seperate files, if there is more than one file, in the specified Torrent]
<br><br>
<b>/{BotCommands.QbLeechCommand}</b> This command should be used as reply to Magnet link, Torrent link, or Direct link using qBittorrent. [this command will SPAM the chat and send the downloads a seperate files, if there is more than one file, in the specified Torrent]
<br><br>
<b>/{BotCommands.QbTarLeechCommand}</b> This command should be used as reply to Magnet link, Torrent link, or Direct link and upload it as (.tar) using qBittorrent. [this command will SPAM the chat and send the downloads a seperate files, if there is more than one file, in the specified Torrent]
<br><br>
<b>/{BotCommands.QbZipLeechCommand}</b> This command should be used as reply to Magnet link, Torrent link, or Direct link and upload it as (.zip) using qBittorrent. [this command will SPAM the chat and send the downloads a seperate files, if there is more than one file, in the specified Torrent]
<br><br>
<b>/{BotCommands.QbUnzipLeechCommand}</b> This command should be used as reply to Magnet link, Torrent link, or Direct link and if file is any archive, extracts it using qBittorrent. [this command will SPAM the chat and send the downloads a seperate files, if there is more than one file, in the specified Torrent]
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url]: Copy file/folder to Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url]: Count file/folder of Google Drive Links
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file from Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl. Click <b>/{BotCommands.WatchCommand}</b> for more help
<br><br>
<b>/{BotCommands.TarWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and zip before uploading
<br><br>
<b>/{BotCommands.LeechWatchCommand}</b> Leech through youtube-dl 
<br><br>
<b>/{BotCommands.LeechTarWatchCommand}</b> Leech through youtube-dl and tar before uploading 
<br><br>
<b>/{BotCommands.LeechZipWatchCommand}</b> Leech through youtube-dl and zip before uploading 
<br><br>
<b>/{BotCommands.LeechSetCommand}</b> Leech Settings 
<br><br>
<b>/{BotCommands.SetThumbCommand}</b> Reply to photo to set it as thumbnail for next uploads 
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Reply to the message by which the download was initiated and that download will be cancelled
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: Cancel all running tasks
<br><br>
<b>/{BotCommands.ListCommand}</b> [search term]: Searches the search term in the Google Drive, If found replies with the link
<br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Show Stats of the machine the bot is hosted on
'''
help = Telegraph(access_token=telegraph_token).create_page(
        title='Atrocious Mirror Help',
        author_name='AL-Noman',
        author_url='https://t.me/smexynos7870',
        html_content=help_string_telegraph,
    )["path"]

help_string = f'''
/{BotCommands.PingCommand}: Check how long it takes to Ping the Bot . (Only sudo and owner)
/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot) .
/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot) .
/{BotCommands.AuthorizedUsersCommand}: Show authorized users (Only Owner & Sudo) .
/{BotCommands.AddSudoCommand}: Add sudo user (Only Owner) .
/{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner) .
/{BotCommands.RestartCommand}: Restart the bot (Only Owner) .
/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports (Only Owner).
/{BotCommands.SpeedCommand}: Check Internet Speed of the Host
/{BotCommands.ShellCommand}: Run commands in Shell (Only Owner)
/{BotCommands.ExecHelpCommand}: Get help for Executor module (Only Owner) .
/{BotCommands.TsHelpCommand}: Get help for Torrent search module .
'''

def bot_help(update, context):
    button = button_build.ButtonMaker()
    button.buildbutton("Other + Public Commands", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

'''
botcmds = [
        (f'{BotCommands.HelpCommand}','Get Detailed Help'),
        (f'{BotCommands.MirrorCommand}', 'Start Mirroring'),
        (f'{BotCommands.TarMirrorCommand}','Start mirroring and upload as .tar'),
        (f'{BotCommands.ZipMirrorCommand}','Start mirroring and upload as .zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Extract files'),
        (f'{BotCommands.TorrentMirrorCommand}','Start Torrent Mirroring'),
        (f'{BotCommands.TorrentTarMirrorCommand}','Start Toreent mirroring and upload as .tar'),
        (f'{BotCommands.Torrent.ZipMirrorCommand}','Start Torrent mirroring and upload as .zip'),
        (f'{BotCommands.TorrentUnzipMirrorCommand}','Unzip Toreent Files'),
        (f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.CountCommand}','Count file/folder of Drive link'),
        (f'{BotCommands.DeleteCommand}','Delete file from Drive'),
        (f'{BotCommands.WatchCommand}','Mirror Youtube-dl support link'),
        (f'{BotCommands.TarWatchCommand}','Mirror Youtube playlist link as .tar'),
        (f'{BotCommands.ZipWatchCommand}','Mirror Youtube playlist link as .zip'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.CancelAllCommand}','Cancel all tasks'),
        (f'{BotCommands.ListCommand}','Searches files in Drive'),
        (f'{BotCommands.StatusCommand}','Get Mirror Status message'),
        (f'{BotCommands.StatsCommand}','Bot Usage Stats'),
        (f'{BotCommands.PingCommand}','Ping the Bot'),
        (f'{BotCommands.RestartCommand}','Restart the bot [owner/sudo only]'),
        (f'{BotCommands.LogCommand}','Get the Bot Log [owner/sudo only]'),
        (f'{BotCommands.TsHelpCommand}','Get help for Torrent search module')
    ]
'''

def main():
    fs_utils.start_cleanup()
    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(PORT))
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Atrocious Mirror Bot Restarted!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)
    # bot.set_my_commands(botcmds)
    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand, bot_help, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand, stats, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Atrocious Mirror Bot Started")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
