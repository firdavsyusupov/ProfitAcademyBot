import os
import re

from django.conf import settings
from django.core.management import BaseCommand
from dotenv import load_dotenv
from telegram import ReplyKeyboardRemove, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from .configs import STATE, regions
from .database import Database
from .keyboards import regions_button, course_buttons, contact_button, apply_course, payment, check_button, \
    channel_button, skip_button, admin_button, user_button
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

db = Database("db.sqlite3")


async def start(update, context):

    userid = update.message.from_user.id

    context.user_data["discount"] = ""
    context.user_data["promocode"] = ""

    user = db.get_user_by_id(userid)
    print(user)

    if user:
        courses = db.get_all_courses()

        await update.message.reply_text(f"Assalomu alaykum, {user['name']}!\n\n"
                                        f"Sizning shahringiz: {user['city']}\n"
                                        f"Sizning telefon raqamingiz: {user['phone']}\n\n"
                                        "Endi siz kursga yozilishingiz mumkin.",
                                        reply_markup=course_buttons(courses))

        context.user_data["state"] = STATE["course"]

    else:
        await update.message.reply_text("Assalomu alaykum!\n\n✍️Ro'yxatdan o'tish uchun ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
        context.user_data["state"] = STATE["name"]

async def message_handler(update, context):

    message = update.message.text

    for course in db.get_all_courses():
        if message == course["title"]:
            context.user_data["state"] = STATE["course"]

    try:
        state = context.user_data["state"]

        print("state>>", state)

        user = update.message.from_user

        if state == STATE["name"]:
            context.user_data["name"] = message


            await update.message.reply_text("Turar shahar yoki viloyatingizni tanlang:",
                                            reply_markup=regions_button())

            context.user_data["state"] = STATE["city"]

        if state == STATE["phone"]:

            phone_number_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')

            if phone_number_pattern.match(message):

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

            else:
                await update.message.reply_text("⚠️Raqam noto'g'ri formatda kiritildi!\n\n"
                                                "Siz bilan bog'lana olishimiz uchun telefon raqamingizni (901234567) ko'rinishida qoldiring toki tugmani bosing👇", reply_markup=contact_button())

                context.user_data["state"] = STATE["phone"]

        if state == STATE["course"] or state == STATE["payment"]:

            context.user_data["discount"] = ""
            context.user_data["promocode"] = ""

            course = db.get_course_by_title(message)

            context.user_data["course"] = course["id"]

            await update.message.reply_photo(photo=open(f'media/{course["photo"]}', "rb"),
                                             caption=f"<b>{course['title']}</b>\n\n"
                                                     f"{course['description']}\n\n"
                                                     f"Narxi: {course['price']}\n\n"
                                                     f"Davomiyligi: {course['duration']} oy",
                                             parse_mode="HTML",
                                             reply_markup=apply_course(course_id=course["id"]))

        if state == STATE["promocode"]:

            promocodes = db.get_promocodes_by_course_id(context.user_data["course"])

            print(promocodes)

            if len(promocodes) != 0:
                print(12345)
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

                                context.user_data["discount"] = price

                                await update.message.reply_photo(photo=open(f'media/{course["photo"]}', "rb"),
                                                                 caption=f"<b>{course['title']}</b>\n\n"
                                                                         f"{course['description']}\n\n"
                                                                         f"✅ Promo-kod muvaffaqiyatli qo'llanildi!\n"
                                                                         f"Yangi narxi: <s>{course['price']}</s> ➡️ "
                                                                         f"<i>{price}</i>\n\n"
                                                                         f"Davomiyligi: {course['duration']} oy",
                                                                 parse_mode="HTML",
                                                                 reply_markup=payment(promo=False, course_id=course["id"]))

                            else:
                                await update.message.reply_text("⚠️ Bu promokoddan foydalanish limiti tugagan!", reply_markup=skip_button())

                    else:
                        await update.message.reply_text("⚠️ Bunday promokod mavjud emas", reply_markup=skip_button())
            else:
                await update.message.reply_text("⚠️ Bunday promokod mavjud emas", reply_markup=skip_button())


    except Exception as e:
        print(e)


def is_promocode_expired(promocode):

    if promocode:
        print("promokod>>", promocode)
        expiry_date_str = promocode["end"]

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

    print(data)

    if data in regions:
        context.user_data["city"] = data

        await query.message.delete()

        await query.message.reply_text("Siz bilan bog'lana olishimiz uchun telefon raqamingizni (901234567) ko'rinishida qoldiring toki tugmani bosing👇", reply_markup=contact_button())

        context.user_data["state"] = STATE["phone"]


    if data.startswith("apply"):
        sp = data.split("_")
        await query.message.edit_reply_markup(reply_markup=payment(course_id=int(sp[1])))

    if data == "promocode":

        await query.message.edit_reply_markup(InlineKeyboardMarkup([[]]))
        await query.message.reply_text("🎟 Promokodni kiriting:", reply_markup=ReplyKeyboardRemove())

        context.user_data["state"] = STATE["promocode"]

    if data.startswith("payment"):
        sp = data.split("_")

        course = db.get_course_by_id(int(sp[1]))

        context.user_data["course"] = course["id"]

        price = course["price"]
        context.user_data["payment"] = price

        if "discount" in context.user_data:
            if len(str(context.user_data["discount"])) != 0:
                price = context.user_data["discount"]
                context.user_data["payment"] = price
            else:
                price = course["price"]
                context.user_data["payment"] = price

        await query.message.edit_reply_markup(InlineKeyboardMarkup([[]]))
        await query.message.edit_caption(caption=f"<b>{course['title']}</b>\n\n"
                                                 f"Narxi: {price}\n\n"
                                                 f"Davomiyligi: {course['duration']} oy\n\n"
                                                 f"To'lov uchun link: [link]\n\n"
                                                 f"<i>To'lov qilib, chekini ushbu botga yuboring</i>",
                                         parse_mode="HTML")

        context.user_data["state"] = STATE["payment"]

    if data.startswith("approve"):
        sp = data.split(".")

        course_id = sp[-1]
        user_id = sp[1]

        channel = db.get_channel_by_course_id(course_id)

        print(query.message.caption)
        print(query.message)
        print(query)

        await query.answer(text="Tasdiqlandi✅")
        await query.message.edit_caption(
            caption=f"{query.message.caption}\n\nTasdiqlandi✅",
            reply_markup=user_button(url=f"tg://user?id={user_id}"),
            parse_mode="HTML"
        )
        # await query.message.edit_reply_markup(InlineKeyboardMarkup([[]]))
        await context.bot.send_message(chat_id=user_id,
                                       text="🎓 Kursingiz boshlanadi!\n"
                                            "Darslarni boshlashdan oldin ro'yxatdan o'tganingizga ishonch hosil qiling.\n\n"
                                            "Kanalga qo'shiling👇",
                                       reply_markup=channel_button(channel["url"]),
                                       parse_mode="HTML")

        context.user_data["state"] = STATE["course"]

    if data.startswith("reject"):
        sp = data.split(".")

        user_id = sp[1]

        await query.answer(text="Rad etildi 🚫")
        await query.message.edit_caption(caption=f"{query.message.caption}\n\nRad etildi🚫",
                                         reply_markup=user_button(url=f"tg://user?id={user_id}"),
                                         parse_mode="HTML")

        await context.bot.send_message(chat_id=user_id,
                                       text=f"To'lov bo'yicha xatolik bor. Admin bilan bog'laning.",
                                       reply_markup=admin_button(url=f"tg://user?id={query.from_user.id}"),
                                       parse_mode="HTML")

    if data == "skip":

        course = db.get_course_by_id(context.user_data["course"])

        await query.message.reply_photo(photo=open(f'media/{course["photo"]}', "rb"),
                                         caption=f"<b>{course['title']}</b>\n\n"
                                                 f"{course['description']}\n\n"
                                                 f"Narxi: {course['price']}\n\n"
                                                 f"Davomiyligi: {course['duration']} oy",
                                         parse_mode="HTML",
                                         reply_markup=payment(promo=False, course_id=course["id"]))


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

            cheques_dir = os.path.join(settings.MEDIA_ROOT, 'photos', 'cheques')
            os.makedirs(cheques_dir, exist_ok=True)

            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

            file_name = f"{user.id}_{current_time}_{photo.file_unique_id}.jpg"
            file_path = os.path.join(cheques_dir, file_name)

            await photo.download_to_drive(file_path)

            print(file_path.split("media/")[-1])

            await update.message.reply_text(
                text="Tez orada to'lovingiz tasdiqlanadi va kurs talabasi bo'lasiz.",
                reply_markup=course_buttons(db.get_all_courses())
            )

            print(context.user_data["course"])
            course = db.get_course_by_id(int(context.user_data["course"]))

            print(context.user_data)

            price = context.user_data["payment"]
            promocode_id = None
            promocode = "-"
            discount_text = ""

            if "promocode" in context.user_data:
                if len(str(context.user_data['promocode'])) != 0:
                    promocode_id = context.user_data["promocode"]
                    promocode = db.get_promocode_by_id(promocode_id)["code"]
                    discount_text = f"<s>{course['price']}</s>"

            userid = db.get_user_by_id(userid=user.id)['id']

            db.insert_payment(user=userid,
                              photo=file_path.split("media/")[-1],
                              course=course['id'],
                              payment=price,
                              promocode=promocode_id)


            try:
                groups = db.get_groups()
                for group in groups:
                    await context.bot.send_photo(
                        chat_id=group["chat_id"],
                        photo=photo.file_id,
                        caption=f"<a href='tg://user?id={update.message.from_user.id}'>{update.message.from_user.first_name}</a>\n\n"
                                f"Kurs: {course['title']}\n"
                                f"To'lov: {price} {discount_text}\n"
                                f"Promokod: {promocode}",
                        parse_mode="HTML",
                        reply_markup=check_button(user_id=update.message.from_user.id,
                                                  photo_id=photo.file_unique_id,
                                                  course_id=course["id"])
                    )

            except Exception as e:
                print(e)

        context.user_data["state"] = STATE["course"]

class Command(BaseCommand):
    def handle(self, *args, **options):
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT, message_handler))
        application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
        application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
        application.add_handler(CallbackQueryHandler(query_handler))

        application.run_polling()
