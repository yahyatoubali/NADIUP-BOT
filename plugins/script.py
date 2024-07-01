from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Translation(object):

    START_TEXT = """
👋 Hey {}

I am NadiuP Bot, a Telegram URL Uploader Bot.

**Send me a direct link, and I will upload it to Telegram as a file/video.**

Use the help button to know how to use me.
"""

    HELP_TEXT = """
**Link to Media or File:**

- Send a link to upload to Telegram as a file or media.

**Set Thumbnail:**

- Send a photo to make it as a permanent thumbnail.

**Deleting Thumbnail:**

- Send `/delthumb` to delete the thumbnail.

**Settings:**

- Configure my settings to change the upload mode.

**Show Thumbnail:**

- Send `/showthumb` to view your custom thumbnail.

**Extract Audio:**

- Reply to a video with `/extractaudio` to extract the audio.

**Unzip Archives:**

- Reply to a supported archive file (zip, rar) with `/unzip` to extract its contents.
"""

    ABOUT_TEXT = """
**My Name:** [NadiuP Bot](https://t.me/nadiupbot)

**Channel:** [NT Bots](https://t.me/NT_BOT_CHANNEL)

**Source:** [Click Here](https://github.com/yahyatoubali/NADIUP-BOT)

**Support Group:** [NT Bots Support](https://t.me/NT_BOTS_SUPPORT)

**Database:** [MongoDB](https://cloud.mongodb.com)

**Language:** [Python 3.12.3](https://www.python.org/)

**Framework:** [Pyrogram 2.0.106](https://docs.pyrogram.org/)

**Developer:** @yahyatoubali 
"""

    PROGRESS = """
**Progress:** {0}%

**Done:** {1}
**Total Size:** {2}
**Speed:** {3}/s
**ETA:** {4}
"""

    START_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('⚙️ Settings', callback_data='OpenSettings')
        ],[
        InlineKeyboardButton('❔ Help', callback_data='help'),
        InlineKeyboardButton('👨‍🚒 About', callback_data='about')
        ],[
        InlineKeyboardButton('⛔️ Close', callback_data='close')
        ]]
    )
    HELP_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('🏡 Home', callback_data='home'),
        InlineKeyboardButton('👨‍🚒 About', callback_data='about')
        ],[
        InlineKeyboardButton('⛔️ Close', callback_data='close')
        ]]
    )
    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('🏡 Home', callback_data='home'),
        InlineKeyboardButton('❔ Help', callback_data='help')
        ],[
        InlineKeyboardButton('⛔️ Close', callback_data='close')
        ]]
    )
    BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('⛔️ Close', callback_data='close')
        ]]
    )
    EXTRACT_ZIP_INTRO_ONE = "Send a compressed file first, then reply to the file with `/unzip`."
    EXTRACT_ZIP_INTRO_THREE = "Analyzing received file. ⚠️ This might take some time. Please be patient."
    UNZIP_SUPPORTED_EXTENSIONS = ("zip", "rar")
    EXTRACT_ZIP_ERRS_OCCURED = "Sorry. Errors occurred while processing the compressed file. Please check everything again, and if the issue persists, report this to <a href='https://t.me/yahyatoubali'>@yahyatoubali</a>"
    CANCEL_STR = "Process Cancelled"
    ZIP_UPLOADED_STR = "Uploaded {} files in {} seconds"
    TEXT = "Send me any custom thumbnail to set it."
    IFLONG_FILE_NAME = "Only 64 characters can be named."
    RENAME_403_ERR = "Sorry. You are not permitted to rename this file."
    ABS_TEXT = "Please don't be selfish."
    FORMAT_SELECTION = "Now Select the Desired Format or File 🗄️ Size to Upload\n{}"  # Added {} for thumbnail
    SET_CUSTOM_USERNAME_PASSWORD = """"""
    NOYES_URL = "🤖 Robot URL detected. Please shorten the URL using a service like [shrtz.me](https://shrtz.me/) and send me the shortened URL." 
    DOWNLOAD_START = "Downloading to my server, please wait ⏳"
    UPLOAD_START = "📤 Uploading, please wait..."
    RCHD_BOT_API_LIMIT = "Downloaded in {} seconds.\nDetected File Size: {}\nSorry. But, I cannot upload files greater than 2GB. Use this bot: @UPLOADER_4GB_BOT"
    #AFTER_SUCCESSFUL_UPLOAD_MSG = "OWNER : Lisa 💕\nFor the List of Telegram Bots"
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "Downloaded in {} seconds.\n\nUploaded in {} seconds.\n\nThanks for using NadiuP Bot!"
    NOT_AUTH_USER_TEXT_FILE_SIZE = "Detected File Size: {}. Free Users can only upload: {}.\nPlease /upgrade your subscription.\nIf you think this is a bug, please contact <a href='https://t.me/yahyatoubali'>@yahyatoubali</a>"
    SAVED_CUSTOM_THUMB_NAIL = "Custom video / file thumbnail saved. This image will be used in the video / file."
    DEL_ETED_CUSTOM_THUMB_NAIL = "✅ Custom thumbnail cleared successfully."
    FF_MPEG_DEL_ETED_CUSTOM_MEDIA = "✅ Media cleared successfully."
    SAVED_RECVD_DOC_FILE = "Document Downloaded Successfully."
    CUSTOM_CAPTION_UL_FILE = " "
    DOWNLOAD_FAILED = "🔴 Error: Download Failed 🔴"
    NO_CUSTOM_THUMB_NAIL_FOUND = "No custom thumbnail found."
    NO_VOID_FORMAT_FOUND = "⛔️ Error: {}"  # {} for dynamic error message
    FILE_NOT_FOUND = "Error, File not Found!!"
    USER_ADDED_TO_DB = "User <a href='tg://user?id={}'>{}</a> added to {} till {}."
    SOMETHING_WRONG = "<code>Something Wrong. Try again.</code>"
    FF_MPEG_RO_BOT_RE_SURRECT_ED = """Syntax: /trim HH:MM:SS for screenshot of that specific time."""
    FF_MPEG_RO_BOT_STEP_TWO_TO_ONE = "First send /downloadmedia to any media so that it can be downloaded to my local. \nSend /storageinfo to know the media, that is currently downloaded."
    FF_MPEG_RO_BOT_STOR_AGE_INFO = "Video Duration: {}\nSend /clearffmpegmedia to delete this media, from my storage.\nSend /trim HH:MM:SS [HH:MM:SS] to cu[l]t a small photo / video, from the above media."
    FF_MPEG_RO_BOT_STOR_AGE_ALREADY_EXISTS = "A saved media already exists. Please send /storageinfo to know the current media details."
    USER_DELETED_FROM_DB = "User <a href='tg://user?id={}'>{}</a> deleted from DataBase."
    REPLY_TO_DOC_OR_LINK_FOR_RARX_SRT = "Reply to a Telegram media (MKV), to extract embedded streams"
    REPLY_TO_MEDIA_ALBUM_TO_GEN_THUMB = "Reply /generatecustomthumbnail to a media album, to generate custom thumbail"
    ERR_ONLY_TWO_MEDIA_IN_ALBUM = "Media Album should contain only two photos. Please re-send the media album, and then try again, or send only two photos in an album."
    INVALID_UPLOAD_BOT_URL_FORMAT = "URL format is incorrect. Make sure your URL starts with either http:// or https://.\nYou can set a custom file name using the format: `link | file_name.extension`"
    ABUSIVE_USERS = "You are not allowed to use this bot. If you think this is a mistake, please check /me to remove this restriction."
    FF_MPEG_RO_BOT_AD_VER_TISE_MENT = "Join: @TGBotsCollectionbot \nFor the list of Telegram bots."
    EXTRACT_ZIP_INTRO_ONE = "Send a compressed file first, then reply to the file with `/unzip`."
    EXTRACT_ZIP_INTRO_THREE = "Analyzing received file. ⚠️ This might take some time. Please be patient."
    UNZIP_SUPPORTED_EXTENSIONS = ("zip", "rar")
    EXTRACT_ZIP_ERRS_OCCURED = "Sorry. Errors occurred while processing the compressed file. Please check everything again, and if the issue persists, report this to <a href='https://t.me/yahyatoubali'>@yahyatoubali</a>"
    CANCEL_STR = "Process Cancelled"
    ZIP_UPLOADED_STR = "Uploaded {} files in {} seconds"
    SLOW_URL_DECED = "Gosh that seems to be a very slow URL. Since you were screwing my home, I am in no mood to download this file. Meanwhile, why don't you try this: ==> https://shrtz.me/PtsVnf6 and get me a fast URL?" 
    FORCE_SUBSCRIBE_TEXT = "<code>Sorry Dear You Must Join My Updates Channel for using me 😌😉....</code>"
    BANNED_USER_TEXT = "<code>You are Banned!</code>"
    CHECK_LINK = "Processing your link ⌛"
