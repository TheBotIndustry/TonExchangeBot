month_dict = {
    "1": "января",
    "2": "февраля",
    "3": "марта",
    "4": "апреля",
    "5": "мая",
    "6": "июня",
    "7": "июля",
    "8": "августа",
    "9": "сентября",
    "10": "октября",
    "11": "ноября",
    "12": "декабря",
}


async def with_us_naming(date):
    month = month_dict.get(str(date.month))
    return f"{date.day} {month} {date.year} года"
