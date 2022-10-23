import csv
import time
from io import BytesIO
import pyrogram.types
import requests
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator
from pyrogram import Client, filters, enums
# from telegram import update
from pyrogram.enums import ParseMode
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler


app = Client("my_account")
chat_id= ""
lang = "en"
messages = []
batchpos = "BOT RIGHT"

async def reminder():
    currentyear = date.today().year
    today = date.today().strftime("%d")
    month = date.today().strftime("%B")
    month = month[0:3]
    if today[0] == "0":
        today = today[1:]
    fullday = f"{month} {today}"
    with open(f"festivals{currentyear}.csv", "r", encoding="UTF-8") as f:
        file = f.readlines()
        for festline in file:
            if fullday in festline:
                festival = festline.split(",")[1]
                f.close()
                with open("chat_ids.csv", "r", encoding="UTF-8") as f:
                    file = f.readlines()
                    for chatlines in file:
                        inline_keyboard = []
                        insidelist = []
                        global chat_id
                        text1= f"Happy {festival}"
                        if lang == "hi" or lang == "gu":
                            translator = Translator()
                            text1 = translator.translate(text1, dest=lang).text

                        insidelist.append(InlineKeyboardButton(text=text1, callback_data=f"TOP LEFT"))
                        inline_keyboard.append(insidelist)

                        inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard)
                        text = f"Hi, Today is {festival} Wish Your Customer's `Happy {festival}`"
                        if lang == "hi" or lang == "gu":
                            translator = Translator()
                            translated = translator.translate(text, dest=lang)
                            text = translated.text
                        await app.send_message(chat_id=chatlines,
                                                  text=text)
                f.close()

scheduler = AsyncIOScheduler()
scheduler.add_job(reminder, "interval", seconds=3600*24)

scheduler.start()


@app.on_message(filters.command("defaultpos"))
async def defaultpos(client, message):
    inline_keyboard = []
    insidelist = []
    global chat_id
    chat_id = message.chat.id
    text1 = "TOP-LEFT"
    text2 = "TOP-RIGHT"
    text3 = "BOTTOM-LEFT"
    text4 = "BOTTOM-RIGHT"
    if lang == "hi" or lang == "gu":
        translator = Translator()
        text1 = translator.translate(text1, dest=lang).text
        text2 = translator.translate(text2, dest=lang).text
        text3 = translator.translate(text3, dest=lang).text
        text4 = translator.translate(text4, dest=lang).text

    insidelist.append(InlineKeyboardButton(text=text1, callback_data=f"TOP LEFT"))
    insidelist.append(InlineKeyboardButton(text=text2, callback_data=f"TOP RIGHT"))
    inline_keyboard.append(insidelist)
    insidelist = []
    insidelist.append(InlineKeyboardButton(text=text3, callback_data=f"BOT LEFT"))
    insidelist.append(InlineKeyboardButton(text=text4, callback_data=f"BOT RIGHT"))
    inline_keyboard.append(insidelist)
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard)
    text = "Kindly Select Default Position for Watermark."
    if lang == "hi" or lang == "gu":
        translator = Translator()
        translated = translator.translate(text, dest=lang)
        text = translated.text
    await client.send_message(chat_id=message.chat.id,
                              text=text,
                          reply_markup=inline_keyboard_markup)
    global message_id
    message_id = message.id

@app.on_callback_query(filters.regex("BOT RIGHT") | filters.regex("BOT LEFT") | filters.regex("TOP RIGHT")| filters.regex("TOP LEFT"))
async def batch(client, callback_query):
    global batchpos
    batchpos = callback_query.data
    await client.send_message(int(chat_id), f"Now, and onward your default position is {batchpos}")



@app.on_message(filters.media_group)
@app.on_message(filters.photo)
async def my_handler(client, message):

    async def progress(current, total):
        print(f"{current * 100 / total:.1f}%")


    await app.download_media(message, progress=progress, file_name=f"{message.chat.id}/{message.id}.jpg")
    messages.append(message.id)
    print(message)

    async def watermark_with_transparency(input_image_path,
                                    output_image_path,
                                    watermark_image_path,
                                    position):

        print(input_image_path)
        base_image = Image.open(input_image_path).convert("RGBA")
        watermark = Image.open(watermark_image_path).convert("RGBA")
        # kadmark = Image.open("kad.png").convert("RGBA")
        watermarkbox = watermark.crop(watermark.getbbox())
        # kadmarkbox = kadmark.crop(kadmark.getbbox())
        w, h = base_image.size
        print(w, h)
        # beforew, beforeh = kadmarkbox.size
        ww, wh = watermarkbox.size
        # print(beforew, beforeh)
        with open("userlogo.csv", "r", encoding="UTF-8") as f:
            lines = f.readlines()
            captions = [line.split(",")[-1] for line in lines if str(chat_id) in line]
            caption = captions[0]
            print(f"caption {caption}")

        if w >= h:
            I1 = ImageDraw.Draw(base_image)
            myFont = ImageFont.truetype("arial.ttf", round(w * 2.3 / 100), encoding="unic")
            watermarkbox = watermarkbox.resize((int(w * 20 / 100), int(wh / ww * (w * 20 / 100))))
            # kadmark = kadmarkbox.resize((int(w * 20 / 100), int(beforeh / beforew * (w * 20 / 100))))

            width, height = base_image.size
            if position == "TOP-LEFT":
                I1.text((int(w * .0321), int(h * .0321) + int(wh / ww * (w * 20 / 100) + 6)), caption, font=myFont,
                        fill=(0, 0, 0))
                position = (int(w * .0321), int(h * .0321))
            if position == "TOP-RIGHT":
                I1.text((int(w - int(w * 20 / 100) - int(w * .0321)),
                         int(h * .0321) + int(wh / ww * (w * 20 / 100) + 8)), caption, font=myFont,
                        fill=(0, 0, 0))
                position = (int(w - int(w * 20 / 100) - int(w * .0321)), int(h * .0321))

            if position == "BOT-LEFT":
                I1.text((int(w * .0321), h - int(h * .0321 * 2)), caption, font=myFont,
                        fill=(0, 0, 0))
                position = (int(w * .0321), h - int(wh / ww * (w * 20 / 100) + int(h * .0321 * 2)) - 5)
            # if position == "BOT-MID":
            #     position = (int(w / 120), int(h - (h / 100) - wh))
            if position == "BOT-RIGHT":
                I1.text((int(w - int(w * 20 / 100) - int(w * .0321)), h - int(h * .0321 * 2)), caption, font=myFont,
                        fill=(0, 0, 0))
                position = (int(w - int(w * 20 / 100) - int(w * .0321)),
                            h - int(wh / ww * (w * 20 / 100) + int(h * .0321 * 2)) - 5)
        else:
            I1 = ImageDraw.Draw(base_image)
            myFont = ImageFont.truetype("arial.ttf", round(h * 2.3 / 100), encoding="unic")
            watermarkbox = watermarkbox.resize((int(ww / wh * (h * 5 / 100)), int(h * 5 / 100)))
            # kadmark = kadmarkbox.resize((int(beforew / beforeh * (h * 15 / 100)), int(h * 15 / 100)))

            width, height = base_image.size
            if position == "TOP-LEFT":
                I1.text((int(w * .0321), int(h * .0321) + int(h * 5 / 100) + 6), caption, font=myFont,
                        fill=(0, 0, 0))
                position = (int(w * .0321), int(h * .0321))
            if position == "TOP-RIGHT":
                I1.text((int(w - int(ww / wh * (h * 5 / 100)) - int(w * .0321)),
                         int(h * .0321) + int(h * 5 / 100) + 6), caption, font=myFont,
                        fill=(0, 0, 0))
                position = (int(w - int(ww / wh * (h * 5 / 100)) - int(w * .0321)), int(h * .0321))

            if position == "BOT-LEFT":
                I1.text((int(w * .0321),
                         h - int(h * .0321)),
                        caption, font=myFont,
                        fill=(0, 0, 0))
                position = (int(w * .0321), h - int(h * 5 / 100) - int(h * .0321))
            # if position == "BOT-MID":
            #     position = (int(w / 120), int(h - (h / 100) - wh))
            if position == "BOT-RIGHT":
                I1.text((int(w - int(ww / wh * (h * 5 / 100)) - int(w * .0321)), h - int(h * .0321)),
                        caption, font=myFont,
                        fill=(0, 0, 0))
                position = (
                int(w - int(ww / wh * (h * 5 / 100)) - int(w * .0321)), h - int(h * 5 / 100) - int(h * .0321))

        transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        transparent.paste(base_image, (0, 0))
        # transparent.paste(kadmark, (int(width / 2), int(height / 2)), mask=kadmark)
        transparent.paste(watermarkbox, position, mask=watermarkbox)
        # transparent.convert("RGB")
        # transparent.paste(kadmark, (int(width/2), int(height/2)), mask=kadmark)
        transparent.convert("RGB").save(output_image_path)

    print(batchpos)
    identifier = message.chat.id
    if batchpos == f"TOP LEFT":
        await watermark_with_transparency(f"{message.chat.id}/{message.id}.jpg", f"{message.chat.id}/{message.id}.jpg",
                                          f'userlogos/{identifier}.png', position="TOP-LEFT")
    if batchpos == f"TOP RIGHT":
        await watermark_with_transparency(f"{message.chat.id}/{message.id}.jpg", f"{message.chat.id}/{message.id}.jpg",
                                          f'userlogos\\{identifier}.png', position="TOP-RIGHT")
    if batchpos == f"BOT LEFT":
        await watermark_with_transparency(f"{message.chat.id}/{message.id}.jpg", f"{message.chat.id}/{message.id}.jpg",
                                          f'userlogos\\{identifier}.png', position="BOT-LEFT")

    if batchpos == f"BOT RIGHT":
        await watermark_with_transparency(f"{message.chat.id}/{message.id}.jpg", f"{message.chat.id}/{message.id}.jpg",
                                          f'userlogos\\{identifier}.png', position="BOT-RIGHT")

    await client.send_photo(int(message.chat.id), open(f"{message.chat.id}/{message.id}.jpg", "rb"))



@app.on_message(filters.command("start") | filters.command("help"))
async def start_handler(client, message):
    global chat_id
    inline_keyboard = []
    insidelist = []
    try:
        chat_id = message.chat.id
        print(chat_id)
    except:
        chat_id = message.chat.id
        print("else" +chat_id)
    is_in = True
    with open("chat_ids.csv", "a+", encoding="UTF-8") as f:
        f.seek(0)

        file = f.readlines()

        print("file opened and stored in file")
        print(file)
        for chatlines in file:
            if chatlines.strip() == str(chat_id).strip():
                is_in = False

        if is_in:

            f.write("%s\n" % (chat_id))
            print("file written")
        else:
            print("Already available")

    insidelist.append(InlineKeyboardButton(text="English", callback_data="eng"))
    insidelist.append(InlineKeyboardButton(text="हिन्दी", callback_data="hi"))
    insidelist.append(InlineKeyboardButton(text="ગુજરાતી", callback_data="gu"))
    inline_keyboard.append(insidelist)
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard)
    await message.reply(text="k", reply_markup=inline_keyboard_markup)

    @app.on_callback_query(filters=filters.regex("[a-zA-Z]"))
    async def welcome(client, callback_query):
        global lang
        lang = callback_query.data
        print(lang)
        insidelist = []
        inline_keyboard = []
        if check_user_in_the_group(client, callback_query):
            user = callback_query.from_user.first_name
            parse_mode = ParseMode.HTML
            text = f"Hello, {user}\nWelcome To WaterMarker. \nWhat I can do?\n1. /setlogo : to set your logo (it's onetime process). You can also add a caption (like 'Mobile No. for easy contact') which shown as tagline of your logo.\n2. Now send any thing you want to make your status (e.g. 'Happy Diwali')\n3. You can send me your any image or images to make your logo float on it.\n4. /defaultpos : used for position of your logo on what you send me.\n Final output would be like this..."

            with open("userlogo.csv", "r", encoding="UTF-8") as f:
                file = f.readlines()
                for logosline in file:
                    if str(chat_id) in logosline:
                        text = f"Hello, {user}\nWelcome To WaterMarker. \nWhat I can do?\n1. /setlogo : to set your logo (it's onetime process). You can also add a caption (like 'Mobile No. for easy contact') which shown as tagline of your logo.\n2. Now send any thing you want to make your status (e.g. 'Happy Diwali')\n3. You can send me your any image or images to make your logo float on it.\n4. /defaultpos : used for position of your logo on what you send me.\n Final output would be like this..."
                f.close()
            if lang == "hi" or lang == "gu":
                translator = Translator()
                translated = translator.translate(text, dest=lang)
                text = translated.text

            await client.send_message(text=text, chat_id=int(chat_id))
            await client.send_photo(int(message.chat.id),
                                    "AgACAgUAAxkBAAImJ2NL1En2021yjPma4flc-RT2UXbTAALesTEbcJxhVhyBcQ08SWHYAAgBAAMCAAN5AAceBA", caption="Sample Image")
        else:
            text = "Join Now 🤗"
            if lang == "hi" or lang == "gu":
                translator = Translator()
                translated = translator.translate(text, dest=lang)
                text = translated.text
            insidelist.append(InlineKeyboardButton(text=text, url="https://t.me/+2fsm_JXtdHgxOTY1"))
            inline_keyboard.append(insidelist)
            inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard)
            text = "Join 'Small Business Community' Group To Continue..."
            if lang == "hi" or lang == "gu":
                translator = Translator()
                translated = translator.translate(text, dest=lang)
                text = translated.text
            await client.send_message(chat_id=chat_id, text=text, reply_markup=inline_keyboard_markup)


async def check_user_in_the_group(client, message):
    # print(message)
    group_chat_id = "-824402865" #replace this with group id number, if you already know it
    # try:
    #     user_id = message.callback_query.from_user.id #replace this with user id number, if you already know it
    # except:
    #     user_id = message.from_user.id
    # # Get members
    async for member in app.get_chat_members(group_chat_id):
        print(member)
    # print(message.get_chat_members(group_chat_id, user_id))
    # check = message.chat(group_chat_id,user_id)["status"] #check if the user exist in the target group
    #
    # if check != "left": #If check variable isn't null, user is in the group
    #     print('user is in the chat')
    #     return True
    # else:
    #     print('Not found')

@app.on_message(filters.command("setlogo"))
async def updatelogo(client, message):
    global caption
    text="Please ⬆️Upload New LOGO .png as a 📁 file format. \n(❗NOT AS A PHOTO❗)\n And add caption if you want but don't use (,) in your caption. (Caption will be shown as tag line of your logo.)\nExample Below..."
    if lang == "hi" or lang == "gu":
        translator = Translator()
        translated = translator.translate(text, dest=lang)
        text = translated.text
    await client.send_message(chat_id=message.chat.id, text=text)
    await client.send_photo(int(message.chat.id),
                            "AgACAgUAAxkBAAImJ2NL1En2021yjPma4flc-RT2UXbTAALesTEbcJxhVhyBcQ08SWHYAAgBAAMCAAN5AAceBA", caption="Sample Image")

    @app.on_message(filters.document)
    async def logo(client, message):

        file_name = message.document.file_name
        print(file_name.split(".")[-1])
        if file_name.split(".")[-1] != "png":
            await client.send_message(message.chat.id, "Please Upload .png file. (only png are allowed).")
            print(file_name)
        else:
            chat_id = message.chat.id
            print(chat_id)
            print(client)
            print(message)
            global i
            try:
                with open("userlogo.csv", "r", encoding="UTF-8") as f:
                    i = int(f.readlines()[-1].split(",")[0]) + 1
                    f.close()
            except:
                i = 1
            file_id = message.document.file_id
            print(file_id)
            global caption
            caption = message.caption
            if caption == "None":

                caption = ""
            print(caption)

            import csv

            logolines = []
            with open('userlogo.csv', 'r') as csv_read:
                reader = csv.reader(csv_read)
                for row in reader:
                    if row != []:
                        logolines.append(row)
                    for field in row:
                        if field.strip() == str(chat_id):
                            print(f'{field} matches {chat_id}, removing {row}')
                            logolines.remove(row)
            print(logolines)
            with open('userlogo.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerows(logolines)
                writer.writerow([str(i), str(file_id), str(chat_id), caption])


            # Logo save to database
            await app.download_media(file_id, file_name=f'userlogos\\{str(message.from_user.id)}.png')
            global identifier
            identifier = message.from_user.id
            text = "Your Logo & Caption received successfully.\nWhat You Want to wish to your customers search here..."
            if lang == "hi" or lang == "gu":
                translator = Translator()
                translated = translator.translate(text, dest=lang)
                text = translated.text
            await client.send_message(chat_id=int(chat_id), text=text)

@app.on_message(filters.text)
async def unsplash(client, message):
    global chat_id
    chat_id = message.chat.id
    if check_user_in_the_group(client, message):
        query = message.text
        global identifier
        identifier = message.from_user.id
        text = "wait for sometime ⌛ your images are being ready. \n it's might take 8 to 10 seconds...Depends on internet connection."
        if lang == "hi" or lang == "gu":
            translator = Translator()
            translated = translator.translate(text, dest=lang)
            text = translated.text
            print(chat_id)
        await client.send_message(int(chat_id), text)
        print("identifier: " + str(identifier))
        icount = 0

        with open("dictionary.csv", "r", encoding="UTF-8") as f:
            print("dictionary opened")
            file = f.readlines()
            for line in file:
                if query.lower() in line:
                    icount +=1
            if icount >= 2:
                print("icount>=2")
                for line in file:
                    if query.lower() in line:
                        print(f"query is in this line")
                        inline_keyboard = []
                        insidelist = []

                        text1 = "↖️ TOP-LEFT"
                        text2 = "TOP-RIGHT ↗️"
                        text3 = "↙️ BOTTOM-LEFT"
                        text4 = "BOTTOM-RIGHT ↘️"
                        if lang == "hi" or lang == "gu":
                            translator = Translator()
                            text1 = translator.translate(text1, dest=lang).text
                            text2 = translator.translate(text2, dest=lang).text
                            text3 = translator.translate(text3, dest=lang).text
                            text4 = translator.translate(text4, dest=lang).text


                        print(line.split(",")[2])
                        await client.send_photo(int(message.chat.id), line.split(", ")[-1].strip())
                        insidelist.append(InlineKeyboardButton(text=text1, callback_data=f"TOP-LEFT {line.split(',')[0]}"))
                        insidelist.append(InlineKeyboardButton(text=text2, callback_data=f"TOP-RIGHT {line.split(',')[0]}"))
                        inline_keyboard.append(insidelist)
                        insidelist = []
                        insidelist.append(InlineKeyboardButton(text=text3, callback_data=f"BOT-LEFT {line.split(',')[0]}"))
                        # insidelist.append(InlineKeyboardButton(text="BOT-MID", callback_data=f"BOT-MID {line.split(',')[0]}"))
                        insidelist.append(InlineKeyboardButton(text=text4, callback_data=f"BOT-RIGHT {line.split(',')[0]}"))
                        inline_keyboard.append(insidelist)
                        inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard)
                        text = "Kindly Select where to place your logo."
                        if lang == "hi" or lang == "gu":
                            translator = Translator()
                            translated = translator.translate(text, dest=lang)
                            text = translated.text
                        await client.send_message(chat_id=message.chat.id,
                                                 text=text,
                                                 reply_markup=inline_keyboard_markup)
                f.close()
            else:
                headless = True
                options = Options()
                if (headless):
                    options.add_argument('--headless')
                driver = webdriver.Chrome(
                    "C:\\Users\\KADMAD Digital Dot\\PycharmProjects\\sqloverssh\\chromedriver.exe",
                    chrome_options=options)
                number_of_images = 5
                url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947" % (
                    query)

                min_resolution = 0
                max_resolution = 1000
                max_missed = 100
                print("[INFO] Gathering image links")
                image_urls = []
                count = 0
                missed_count = 0
                driver.get(url)
                time.sleep(3)
                indx = 1

                while number_of_images > count:
                    try:
                        # find and click image
                        imgurl = driver.find_element_by_xpath(
                            '//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (str(indx)))
                        imgurl.click()
                        missed_count = 0
                    except Exception:
                        # print("[-] Unable to click this photo.")
                        missed_count = missed_count + 1
                        if (missed_count > max_missed):
                            print("[INFO] Maximum missed photos reached, exiting...")
                            break

                    try:
                        # select image from the popup
                        time.sleep(1)
                        class_names = ["n3VNCb"]
                        images = [driver.find_elements_by_class_name(class_name) for class_name in class_names if
                                  len(driver.find_elements_by_class_name(class_name)) != 0][0]
                        iline = 1

                        for image in images:
                            # only download images that starts with http
                            src_link = image.get_attribute("src")

                            if (("http" in src_link) and (not "encrypted" in src_link)):
                                inline_keyboard = []
                                insidelist = []
                                print(src_link)
                                msg = await client.send_photo(message.chat.id, f"{src_link}")
                                file_id = pyrogram.types.Photo
                                print(file_id)
                                # file_id = msg.photo[0].file_id
                                print(file_id)
                                with open("dictionary.csv", "r+", encoding="UTF-8") as f:
                                    srccounts = 0
                                    directory = f.readlines()
                                    try:
                                        i = int(directory[-1].split(",")[0]) + 1
                                    except:
                                        i = 0
                                    for x in directory:

                                        if src_link.strip() == x.split(", ")[-1].strip():
                                            srccounts += 1
                                    if srccounts == 0:
                                        f.write("%s, %s, %s, %s\n" % (str(i), query.lower(), file_id, src_link))
                                        f.close()
                                        iline +=1
                                    else:
                                        pass
                                with open("dictionary.csv", "r", encoding="UTF-8") as f:
                                    idfile = f.readlines()
                                    for idlines in idfile:
                                        if src_link in idlines:
                                            fileindex = idlines.split(",")[0].strip()
                                            print(fileindex)

                                text1 = "↖️ TOP-LEFT"
                                text2 = "TOP-RIGHT ↗️"
                                text3 = "↙️ BOTTOM-LEFT"
                                text4 = "BOTTOM-RIGHT ↘️"
                                if lang == "hi" or lang == "gu":
                                    translator = Translator()
                                    text1 = translator.translate(text1, dest=lang).text
                                    text2 = translator.translate(text2, dest=lang).text
                                    text3 = translator.translate(text3, dest=lang).text
                                    text4 = translator.translate(text4, dest=lang).text

                                insidelist.append(InlineKeyboardButton(text=text1, callback_data=f"TOP-LEFT {fileindex}"))
                                insidelist.append(InlineKeyboardButton(text=text2, callback_data=f"TOP-RIGHT {fileindex}"))
                                inline_keyboard.append(insidelist)
                                insidelist = []
                                insidelist.append(InlineKeyboardButton(text=text3, callback_data=f"BOT-LEFT {fileindex}"))
                                # insidelist.append(InlineKeyboardButton(text="BOT-MID", callback_data=f"BOT-MID {fileindex}"))
                                insidelist.append(InlineKeyboardButton(text=text4, callback_data=f"BOT-RIGHT {fileindex}"))
                                inline_keyboard.append(insidelist)
                                inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard)
                                text = "Kindly Select where to place your logo."
                                if lang == "hi" or lang == "gu":
                                    translator = Translator()
                                    translated = translator.translate(text, dest=lang)
                                    text = translated.text
                                await client.send_message(chat_id=message.chat.id, text=text,
                                                        reply_markup=inline_keyboard_markup)
                                print(
                                    f"[INFO] {query.lower()} \t #{count} \t {src_link}")
                                image_urls.append(src_link)
                                count += 1
                                break

                    except Exception as e:
                        print("[INFO] Unable to get link", e)

                    try:
                        # scroll page to load next image
                        if (count % 3 == 0):
                            driver.execute_script("window.scrollTo(0, " + str(indx * 60) + ");")
                        element = driver.find_element_by_class_name("mye4qd")
                        element.click()
                        print("[INFO] Loading next page")
                        time.sleep(3)
                    except Exception:
                        time.sleep(1)
                    indx += 1
                driver.quit()
                print("[INFO] Google search ended")

    else:
        inline_keyboard = []
        insidelist = []
        text = "Join Now 🤗"
        if lang == "hi" or lang == "gu":
            translator = Translator()
            translated = translator.translate(text, dest=lang)
            text = translated.text
        insidelist.append(InlineKeyboardButton(text=text, url="https://t.me/+2fsm_JXtdHgxOTY1"))
        inline_keyboard.append(insidelist)
        inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard)
        text="Join 'Small Business Community' Group To Continue..."
        if lang == "hi" or lang == "gu":
            translator = Translator()
            translated = translator.translate(text, dest=lang)
            text = translated.text
        await client.send_message(chat_id=chat_id, text=text, reply_markup=inline_keyboard_markup)



buttonarray = []
@app.on_callback_query(filters=filters.regex(f"[A-Z0-9- ]"))
async def watermarker(client, callback_query):

        pos = callback_query.data
        buttonarray.append(pos)
        print(f"button arrray: {buttonarray}")
        print(pos)
        indx = pos.split(" ")[-1]
        print(indx)
        with open("dictionary.csv", "r", encoding="UTF-8") as f:
            srclnkfile = f.readlines()
            print("reading files")
            for srclnkline in srclnkfile:
                if indx == srclnkline.split(",")[0]:
                    imgsrc = srclnkline.split(", ")[-1].strip()
                    query = srclnkline.split(",")[1].strip()
        async def watermark_with_transparency(input_image_path,
                                        output_image_path,
                                        watermark_image_path,
                                        position):

            print(input_image_path)
            response = requests.get(input_image_path)
            base_image = Image.open(BytesIO(response.content)).convert("RGBA")

            watermark = Image.open(watermark_image_path).convert("RGBA")


            # kadmark = Image.open("kad.png").convert("RGBA")
            watermarkbox = watermark.crop(watermark.getbbox())
            # kadmarkbox = kadmark.crop(kadmark.getbbox())
            w, h = base_image.size
            print(w, h)
            # beforew, beforeh = kadmarkbox.size
            ww, wh = watermarkbox.size
            # print(beforew, beforeh)

            if w >= h:
                I1 = ImageDraw.Draw(base_image)
                myFont = ImageFont.truetype("arial.ttf", round(w*2.3/100), encoding="unic")
                watermarkbox = watermarkbox.resize((int(w*20/100), int(wh/ww*(w*20/100))))
                # kadmark = kadmarkbox.resize((int(w * 20 / 100), int(beforeh / beforew * (w * 20 / 100))))

                width, height = base_image.size
                if position == "TOP-LEFT":
                    I1.text((int(w*.0321), int(h*.0321)+int(wh/ww*(w*20/100)+6)), caption, font=myFont,
                            fill=(0, 0, 0))
                    position = (int(w*.0321), int(h*.0321))
                if position == "TOP-RIGHT":
                    I1.text((int(w - int(w * 20 / 100) - int(w*.0321)), int(h*.0321)+int(wh/ww*(w*20/100)+8)), caption, font=myFont,
                            fill=(0, 0, 0))
                    position = (int(w - int(w * 20 / 100) - int(w*.0321)), int(h*.0321))

                if position == "BOT-LEFT":
                    I1.text((int(w*.0321), h - int(h*.0321*2) ), caption, font=myFont,
                            fill=(0, 0, 0))
                    position = (int(w*.0321), h - int(wh / ww * (w * 20 / 100) + int(h*.0321*2))-5)
                # if position == "BOT-MID":
                #     position = (int(w / 120), int(h - (h / 100) - wh))
                if position == "BOT-RIGHT":
                    I1.text((int(w - int(w * 20 / 100) - int(w*.0321)), h - int(h*.0321*2)), caption, font=myFont,
                            fill=(0, 0, 0))
                    position = (int(w - int(w * 20 / 100) - int(w*.0321)), h - int(wh / ww * (w * 20 / 100) + int(h*.0321*2))-5)
            else:
                I1 = ImageDraw.Draw(base_image)
                myFont = ImageFont.truetype("arial.ttf", round(h * 2.3 / 100), encoding="unic")
                watermarkbox = watermarkbox.resize((int(ww/wh*(h*5/100)), int(h*5/100)))
                # kadmark = kadmarkbox.resize((int(beforew / beforeh * (h * 15 / 100)), int(h * 15 / 100)))

                width, height = base_image.size
                if position == "TOP-LEFT":
                    I1.text((int(w * .0321), int(h * .0321) + int(h*5/100)+6), caption, font=myFont,
                            fill=(0, 0, 0))
                    position = (int(w*.0321), int(h*.0321))
                if position == "TOP-RIGHT":
                    I1.text((int(w - int(ww/wh*(h*5/100)) - int(w*.0321)),
                             int(h * .0321) + int(h*5/100)+6), caption, font=myFont,
                            fill=(0, 0, 0))
                    position = (int(w - int(ww/wh*(h*5/100)) - int(w*.0321)), int(h*.0321))

                if position == "BOT-LEFT":
                    I1.text((int(w * .0321),
                             h - int(h*.0321)),
                            caption, font=myFont,
                            fill=(0, 0, 0))
                    position = (int(w*.0321), h - int(h*5/100) - int(h*.0321))
                # if position == "BOT-MID":
                #     position = (int(w / 120), int(h - (h / 100) - wh))
                if position == "BOT-RIGHT":
                    I1.text((int(w - int(ww/wh*(h*5/100)) - int(w*.0321)), h- int(h*.0321)),
                            caption, font=myFont,
                            fill=(0, 0, 0))
                    position = (int(w - int(ww/wh*(h*5/100)) - int(w*.0321)), h - int(h*5/100) - int(h*.0321))

            transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            transparent.paste(base_image, (0, 0))
            # transparent.paste(kadmark, (int(width / 2), int(height / 2)), mask=kadmark)
            transparent.paste(watermarkbox, position, mask=watermarkbox)
            # transparent.convert("RGB")
            # transparent.paste(kadmark, (int(width/2), int(height/2)), mask=kadmark)
            transparent.convert("RGB").save(output_image_path)
            inline_keyboard = []
            insidelist = []
            text = "SENT ✅"
            text1 = "↖️ TOP-LEFT"
            text2 = "TOP-RIGHT ↗️"
            text3 = "↙️ BOTTOM-LEFT"
            text4 = "BOTTOM-RIGHT ↘️"
            if lang == "hi" or lang == "gu":
                translator = Translator()
                text = translator.translate(text, dest=lang).text
                text1 = translator.translate(text1, dest=lang).text
                text2 = translator.translate(text2, dest=lang).text
                text3 = translator.translate(text3, dest=lang).text
                text4 = translator.translate(text4, dest=lang).text
            # button = user_data[POS].split(" ")[0]
            if f"TOP-LEFT {indx}" in buttonarray:
                insidelist.append(InlineKeyboardButton(text=text, callback_data=f"done"))

            else:
                insidelist.append(InlineKeyboardButton(text=text1, callback_data=f"TOP-LEFT {indx}"))

            if f"TOP-RIGHT {indx}" in buttonarray:
                insidelist.append(InlineKeyboardButton(text=text, callback_data=f"done"))

            else:
                insidelist.append(InlineKeyboardButton(text=text2, callback_data=f"TOP-RIGHT {indx}"))

            inline_keyboard.append(insidelist)
            insidelist = []

            if f"BOT-LEFT {indx}" in buttonarray:
                insidelist.append(InlineKeyboardButton(text=text, callback_data="done"))

            else:
                insidelist.append(InlineKeyboardButton(text=text3, callback_data=f"BOT-LEFT {indx}"))

            if f"BOT-RIGHT {indx}" in buttonarray:
                insidelist.append(InlineKeyboardButton(text=text, callback_data=f"done"))

            else:
                insidelist.append(InlineKeyboardButton(text=text4, callback_data=f"BOT-RIGHT {indx}"))

            inline_keyboard.append(insidelist)
            inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard)

            text = "Your image is ready at bottom.."
            if lang == "hi" or lang == "gu":
                translator = Translator()
                translated = translator.translate(text, dest=lang)
                text = translated.text

            await callback_query.edit_message_text(text=text,
                                     reply_markup=inline_keyboard_markup)

            await client.send_photo(int(chat_id), open(output_image_path, "rb"))

        with open("userlogo.csv", "r", encoding="UTF-8") as f:
            lines = f.readlines()
            captions = [line.split(",")[-1] for line in lines if str(chat_id) in line]
            caption = captions[0]
            print(f"caption {caption}")
        print("this is path" + f"userlogos\\{identifier}.png")
        if pos == f"TOP-LEFT {indx}":
            await watermark_with_transparency(imgsrc, query + ".jpg",
                                        f'userlogos\\{identifier}.png', position="TOP-LEFT")
        if pos == f"TOP-RIGHT {indx}":
            await watermark_with_transparency(imgsrc, query + ".jpg",
                                        f'userlogos\\{identifier}.png', position="TOP-RIGHT")
        if pos == f"BOT-LEFT {indx}":
            await watermark_with_transparency(imgsrc, query + ".jpg",
                                        f'userlogos\\{identifier}.png', position="BOT-LEFT")


        if pos == f"BOT-RIGHT {indx}":
            await watermark_with_transparency(imgsrc, query + ".jpg",
                                        f'userlogos\\{identifier}.png', position="BOT-RIGHT")



app.run()
