import logging
from telegram import (Update, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

(START_REPLY, COMPANY_NAME, CONTACT_PERSON, CONTACT_INFO, TASK_DESCRIPTION,
 TASK_GOAL, SELECT_ITEMS, QUANTITY, MATERIALS, APPLICATION, DESIGN_FILES,
 DESIGN_STYLE, BUDGET, DEADLINES, ADDITIONAL_REQ, CONFIRMATION) = range(16)

ITEMS = [
    ('Футболка TL', 1350),
    ('Лонг TL', 1600),
    ('Свитшот TL', 1800),
    ('Халф-зип TL', 2000),
    ('Шоппер TL', 500),
    ('Худи TL', 2000),
    ('Зип-худи TL', 2000),
    ('Штаны TL', 2000),
    ('Джинсы TL', 5000),
    ('Жилет­ка TL', 1300),
    ('Шорты TL', 1300),
]

item_keyboard = [[item[0]] for item in ITEMS]

def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text(
        'Привет! Я помогу вам сформировать коммерческое предложение по каталогу Total Lookas. Готовы начать?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return START_REPLY

def start_reply(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() != 'да':
        update.message.reply_text('Хорошо, обращайтесь, когда будете готовы.',
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    update.message.reply_text('Укажите, пожалуйста, полное название вашей компании.',
                              reply_markup=ReplyKeyboardRemove())
    return COMPANY_NAME

def company_name(update: Update, context: CallbackContext) -> int:
    context.user_data['company_name'] = update.message.text
    update.message.reply_text('Контактное лицо (ФИО и должность).')
    return CONTACT_PERSON

def contact_person(update: Update, context: CallbackContext) -> int:
    context.user_data['contact_person'] = update.message.text
    update.message.reply_text('Телефон и e-mail для обратной связи.')
    return CONTACT_INFO

def contact_info(update: Update, context: CallbackContext) -> int:
    context.user_data['contact_info'] = update.message.text
    update.message.reply_text('Что именно нужно закупить? Опишите задачу кратко (одежда, аксессуары, сувенирка и т. п.).')
    return TASK_DESCRIPTION

def task_description(update: Update, context: CallbackContext) -> int:
    context.user_data['task_description'] = update.message.text
    update.message.reply_text('Какова цель заказа? (мероприятие, подарки сотрудникам, промо-акция и т. д.)')
    return TASK_GOAL

def task_goal(update: Update, context: CallbackContext) -> int:
    context.user_data['task_goal'] = update.message.text
    keyboard = [[item[0]] for item in ITEMS]
    update.message.reply_text('Выберите позиции (можно несколько), после чего отправьте "Готово".',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False))
    context.user_data['selected_items'] = []
    return SELECT_ITEMS

def select_items(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text.lower() == 'готово':
        if not context.user_data['selected_items']:
            update.message.reply_text('Пожалуйста, выберите хотя бы одну позицию.')
            return SELECT_ITEMS
        context.user_data['quantity'] = {}
        item = context.user_data['selected_items'].pop(0)
        update.message.reply_text(f'Сколько единиц "{item}" вы планируете заказать?')
        context.user_data['current_item'] = item
        return QUANTITY
    elif text in [name for name, _ in ITEMS]:
        if text not in context.user_data['selected_items']:
            context.user_data['selected_items'].append(text)
    else:
        update.message.reply_text('Выберите позицию из списка или отправьте "Готово".')
    return SELECT_ITEMS

def quantity(update: Update, context: CallbackContext) -> int:
    qty_text = update.message.text
    if not qty_text.isdigit():
        update.message.reply_text('Пожалуйста, введите число.')
        return QUANTITY
    qty = int(qty_text)
    item = context.user_data['current_item']
    context.user_data.setdefault('quantity', {})[item] = qty
    if context.user_data['selected_items']:
        item = context.user_data['selected_items'].pop(0)
        context.user_data['current_item'] = item
        update.message.reply_text(f'Сколько единиц "{item}" вы планируете заказать?')
        return QUANTITY
    update.message.reply_text('Какие материалы предпочитаете? (пример: хлопок 200 г/м², футер, нейлон и т. д.)',
                              reply_markup=ReplyKeyboardRemove())
    return MATERIALS

def materials(update: Update, context: CallbackContext) -> int:
    context.user_data['materials'] = update.message.text
    update.message.reply_text('Какие способы нанесения? (вышивка, шелкография, ДТФ…)')
    return APPLICATION

def application(update: Update, context: CallbackContext) -> int:
    context.user_data['application'] = update.message.text
    update.message.reply_text('У вас есть готовые макеты или логотипы? Пришлите файлы или напишите "Нет".')
    return DESIGN_FILES

def design_files(update: Update, context: CallbackContext) -> int:
    if update.message.text and update.message.text.lower() == 'нет':
        context.user_data['design_files'] = 'Нет'
    else:
        context.user_data['design_files'] = 'Файлы предоставлены'
    update.message.reply_text('Какой стиль оформления предпочитаете? (минимализм, яркий арт, провокационный уличный стиль…)')
    return DESIGN_STYLE

def design_style(update: Update, context: CallbackContext) -> int:
    context.user_data['design_style'] = update.message.text
    update.message.reply_text('Укажите ориентировочный бюджет на проект.')
    return BUDGET

def budget(update: Update, context: CallbackContext) -> int:
    context.user_data['budget'] = update.message.text
    update.message.reply_text('Желаемые сроки производства и доставки (дата или промежуток).')
    return DEADLINES

def deadlines(update: Update, context: CallbackContext) -> int:
    context.user_data['deadlines'] = update.message.text
    update.message.reply_text('Есть ли особые требования? (упаковка, комплектация, “Честный Знак”, и т. п.) Если нет, напишите "Нет".')
    return ADDITIONAL_REQ

def additional_req(update: Update, context: CallbackContext) -> int:
    context.user_data['additional_req'] = update.message.text
    summary = (
        f'Компания: {context.user_data.get("company_name")}\n'
        f'Контактное лицо: {context.user_data.get("contact_person")}\n'
        f'Контакты: {context.user_data.get("contact_info")}\n'
        f'Задача: {context.user_data.get("task_description")}\n'
        f'Цель: {context.user_data.get("task_goal")}\n'
        f'Позиции и тираж: {context.user_data.get("quantity")}\n'
        f'Материалы/технологии: {context.user_data.get("materials")}; {context.user_data.get("application")}\n'
        f'Дизайн: {context.user_data.get("design_files")}; {context.user_data.get("design_style")}\n'
        f'Бюджет/сроки: {context.user_data.get("budget")}; {context.user_data.get("deadlines")}\n'
        f'Пожелания: {context.user_data.get("additional_req")}'
    )
    update.message.reply_text(
        'Проверьте всё ещё раз:\n' + summary + '\n\nСогласны отправить этот бриф?',
        reply_markup=ReplyKeyboardMarkup([['Да', 'Нет, хочу исправить']], one_time_keyboard=True))
    context.user_data['summary'] = summary
    return CONFIRMATION

def confirmation(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower().startswith('да'):
        update.message.reply_text('Спасибо! Сейчас формирую КП…', reply_markup=ReplyKeyboardRemove())
        # Here could be generation of commercial offer
        return ConversationHandler.END
    update.message.reply_text('Какой шаг хотите исправить? (1-8)', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Диалог прерван.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    updater = Updater('YOUR_TOKEN_HERE')
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START_REPLY: [MessageHandler(Filters.text & ~Filters.command, start_reply)],
            COMPANY_NAME: [MessageHandler(Filters.text & ~Filters.command, company_name)],
            CONTACT_PERSON: [MessageHandler(Filters.text & ~Filters.command, contact_person)],
            CONTACT_INFO: [MessageHandler(Filters.text & ~Filters.command, contact_info)],
            TASK_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, task_description)],
            TASK_GOAL: [MessageHandler(Filters.text & ~Filters.command, task_goal)],
            SELECT_ITEMS: [MessageHandler(Filters.text & ~Filters.command, select_items)],
            QUANTITY: [MessageHandler(Filters.text & ~Filters.command, quantity)],
            MATERIALS: [MessageHandler(Filters.text & ~Filters.command, materials)],
            APPLICATION: [MessageHandler(Filters.text & ~Filters.command, application)],
            DESIGN_FILES: [MessageHandler((Filters.text | Filters.document) & ~Filters.command, design_files)],
            DESIGN_STYLE: [MessageHandler(Filters.text & ~Filters.command, design_style)],
            BUDGET: [MessageHandler(Filters.text & ~Filters.command, budget)],
            DEADLINES: [MessageHandler(Filters.text & ~Filters.command, deadlines)],
            ADDITIONAL_REQ: [MessageHandler(Filters.text & ~Filters.command, additional_req)],
            CONFIRMATION: [MessageHandler(Filters.text & ~Filters.command, confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
