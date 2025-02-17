import os

from django.core.management import BaseCommand
from dotenv import load_dotenv
from telegram import ReplyKeyboardRemove, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from .configs import STATE, regions
from .database import Database
from .keyboards import regions_button, course_buttons, contact_button, apply_course, payment, check_button
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

db = Database("db.sqlite3")


async def start(update, context):

    await update.message.reply_text("Assalomu alaykum!\n\n✍️Ro'yxatdan o'tish uchun ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
    context.user_data["state"] = STATE["name"]

async def message_handler(update, context):

    message = update.message.text

    try:
        state = context.user_data["state"]

        user = update.message.from_user

        if state == STATE["name"]:
            context.user_data["name"] = message


            await update.message.reply_text("Turar shahar yoki viloyatingizni tanlang:",
                                            reply_markup=regions_button())

            context.user_data["state"] = STATE["city"]

        if state == STATE["phone"]:

            name = context.user_data["name"]
            city = context.user_data["city"]

            db.insert_user(name=name,
                           phone=message,
                           city=city,
                           username=user.username,
                           userid=user.id)

            courses = db.get_all_courses()

            await update.message.reply_text(f"Tabriklaymiz, {context.user_data['name']}!\n\n"
                                            "🎉 Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
                                            f"Sizning shahringiz: {context.user_data['city']}\n"
                                            f"Sizning telefon raqamingiz: {message}\n\n"
                                            "Endi siz kursga yozilishingiz mumkin.",
                                            reply_markup=course_buttons(courses))

            context.user_data["state"] = STATE["course"]


        if state == STATE["course"]:

            course = db.get_course_by_title(message)

            context.user_data["course"] = course["id"]

            await update.message.reply_photo(photo=open(course["photo"], "rb"),
                                             caption=f"<b>{course['title']}</b>\n\n"
                                                     f"{course['description']}\n\n"
                                                     f"Narxi: {course['price']}\n\n"
                                                     f"Davomiyligi: {course['duration']} oy",
                                             parse_mode="HTML",
                                             reply_markup=apply_course(course_id=course["id"]))

        if state == STATE["promocode"]:
            promocodes = db.get_promocodes_by_course_id(context.user_data["course"])

            for promocode in promocodes:
                print("promo>>",promocode)
                if message == promocode["code"]:
                    if is_promocode_expired(promocode):
                        await update.message.reply_text("⚠️ Bu promokodni muddati o'tgan!")
                    else:
                        if int(promocode["limit_count"]) > 0:

                            context.user_data["promocode"] = promocode["id"]

                            print(context.user_data["course"])
                            course = db.get_course_by_id(context.user_data["course"])

                            print(course)

                            db.update_promocode(limit_count=int(promocode["limit_count"])-1, promocode_id=promocode["id"])

                            price = int(int(course["price"]) - (int(course["price"]) * promocode["discount_percentage"]) / 100)

                            context.user_data["payment"] = price

                            await update.message.reply_photo(photo=open(course["photo"], "rb"),
                                                             caption=f"<b>{course['title']}</b>\n\n"
                                                                     f"{course['description']}\n\n"
                                                                     f"✅ Promo-kod muvaffaqiyatli qo'llanildi!\n"
                                                                     f"Yangi narxi: <s>{course['price']}</s> ➡️ "
                                                                     f"<i>{price}</i>\n\n"
                                                                     f"Davomiyligi: {course['duration']} oy",
                                                             parse_mode="HTML",
                                                             reply_markup=payment(promo=False, course_id=course["id"]))

                        else:
                            await update.message.reply_text("⚠️ Bu promokoddan foydalanish limiti tugagan!")

                else:
                    await update.message.reply_text("⚠️ Bunday promokod mavjud emas")

    except Exception as e:
        print(e)


def is_promocode_expired(promocode):

    if promocode:
        print("promokod>>", promocode)
        expiry_date_str = promocode["end"]

        # Update the format to handle date and time
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")

        today = datetime.today()

        print("today", today)

        if expiry_date < today:
            return True
        else:
            return False
    else:
        return None


async def query_handler(update, context):

    query = update.callback_query

    data = query.data

    sp = data.split("_")

    print(data)

    if data in regions:
        context.user_data["city"] = data

        await query.message.delete()

        await query.message.reply_text("Siz bilan bog'lana olishimiz uchun telefon raqamingizni (901234567) ko'rinishida qoldiring.", reply_markup=contact_button())

        context.user_data["state"] = STATE["phone"]


    if data.startswith("apply"):
        sp = data.split("_")
        await query.message.edit_reply_markup(reply_markup=payment(course_id=int(sp[1])))

    if data == "promocode":

        await query.message.edit_reply_markup(InlineKeyboardMarkup([[]]))
        await query.message.reply_text("🎟 Promokodni kiriting:", reply_markup=ReplyKeyboardRemove())

        context.user_data["state"] = STATE["promocode"]

    if data.startswith("payment"):

        course = db.get_course_by_id(int(sp[1]))

        context.user_data["course"] = course["id"]

        context.user_data["payment"] = course['price']

        await query.message.edit_reply_markup(InlineKeyboardMarkup([[]]))
        await query.message.edit_caption(caption=f"<b>{course['title']}</b>\n\n"
                                                 f"Narxi: {course['price']}\n\n"
                                                 f"Davomiyligi: {course['duration']} oy\n\n"
                                                 f"To'lov uchun link: @admin\n\n"
                                                 f"<i>To'lov qilib, chekini ushbu botga yuboring</i>",
                                         parse_mode="HTML")

        context.user_data["state"] = STATE["payment"]

    # if sp[0] == "approve":
    #
    #     user = db.get_user_by_id(int(sp[1]))
    #
    #     await context.bot.send_message(chat_id=requester_id,
    #                                    text="<b>Biznes klubga qo'shilganingiz bilan tabriklayman✅</b>\n\n<i>Fikr, taklif va shikoyatlaringizni adminga yozib qoldirishingiz mumkin.\n\nAdmin: @zokirov_manager</i>",
    #                                    reply_markup=InlineKeyboardMarkup([
    #                                        [
    #                                            InlineKeyboardButton("Kanalga o'tish🚀",
    #                                                                 url="https://t.me/+N1o_xsC-sqQ5YWJi")
    #                                        ]
    #                                    ]),
    #                                    parse_mode="HTML")

async def contact_handler(update, context):

    state = context.user_data["state"]

    user = update.message.from_user

    if state == STATE["phone"]:

        contact = update.message.contact.phone_number

        name = context.user_data["name"]
        city = context.user_data["city"]

        db.insert_user(name=name,
                       phone=contact,
                       city=city,
                       username=user.username,
                       userid=user.id)

        courses = db.get_all_courses()

        await update.message.reply_text(f"Tabriklaymiz, {context.user_data['name']}!\n\n"
                                        "🎉 Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
                                        f"Sizning shahringiz: {context.user_data['city']}\n"
                                        f"Sizning telefon raqamingiz: {contact}\n\n"
                                        "Endi siz kursga yozilishingiz mumkin.",
                                        reply_markup=course_buttons(courses))

        context.user_data["state"] = STATE["course"]

async def photo_handler(update, context):

    if update.message.photo:
        state = context.user_data["state"]
        if state == STATE["payment"]:
            photo_file = update.message.photo[-1].file_id
            photo = await context.bot.get_file(photo_file)

            user = update.message.from_user

            cheques_dir = 'photos/cheques'
            if not os.path.exists(cheques_dir):
                os.makedirs(cheques_dir)

            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(cheques_dir, f"{user.id}_{current_time}_{photo.file_unique_id}.jpg")

            await photo.download_to_drive(file_path)

            await update.message.reply_text(
                text="Tez orada to'lovingiz tasdiqlanadi va kurs talabasi bo'lasiz.\n\nAdmin: @admin"
            )

            print(context.user_data["course"])
            course = db.get_course_by_id(int(context.user_data["course"]))

            print(context.user_data)

            price = context.user_data["payment"]
            promocode = None

            if "promocode" in context.user_data:
                promocode = context.user_data["promocode"]


            db.insert_payment(user=user.id,
                              photo=file_path,
                              course=course['id'],
                              payment=price,
                              promocode=promocode)

            try:
                groups = db.get_groups()
                for group in groups:
                    await context.bot.send_photo(
                        chat_id=group["chat_id"],
                        photo=photo.file_id,
                        caption=f"<a href='tg://user?id={update.message.from_user.id}'>{update.message.from_user.username}</a>",
                        parse_mode="HTML",
                        reply_markup=check_button(user_id=update.message.from_user.id,
                                                  photo_id=photo.file_unique_id)
                    )

            except Exception as e:
                print(e)


class Command(BaseCommand):
    def handle(self, *args, **options):
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT, message_handler))
        application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
        application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
        application.add_handler(CallbackQueryHandler(query_handler))

        application.run_polling()
