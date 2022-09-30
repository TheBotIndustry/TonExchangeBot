from utils.database_api.commands.courses import DB_Courses
from utils.database_api.models.users import Users


async def makeRoundFloatDollars(number):
    floatNumber = float(number)
    strNumber = str(floatNumber)
    if "e" in strNumber:
        countExp = strNumber[-2:]
        intCountExp = int(countExp)
        if intCountExp == 1:
            return f"{floatNumber:.1f}"
        else:
            return f"{floatNumber:.2f}"
    elif "." in strNumber:
        count = abs(strNumber.find(".") - len(strNumber)) - 1
        if count == 1:
            rest = floatNumber % 1
            if rest == 0:
                return int(floatNumber)
            else:
                return f"{floatNumber:.1f}"
        else:
            return f"{floatNumber:.2f}"
    else:
        try:
            return f"{round(floatNumber, 2)}"
        except:
            return number


async def amount_in_dollars(user: Users):
    toncoin = await DB_Courses().get_course('TON')
    amount = 0
    amount += user.balance_toncoin * toncoin.course
    return await makeRoundFloatDollars(amount)


async def makeRoundFloatTON(number):
    floatNumber = float(number)
    strNumber = str(floatNumber)
    if "e" in strNumber:
        countExp = strNumber[-2:]
        intCountExp = int(countExp)
        if intCountExp == 1:
            return f"{floatNumber:.1f}"
        elif intCountExp == 2:
            return f"{floatNumber:.2f}"
        elif intCountExp == 3:
            return f"{floatNumber:.3f}"
        else:
            return f"{floatNumber:.4f}"
    elif "." in strNumber:
        count = abs(strNumber.find(".") - len(strNumber)) - 1
        if count == 1:
            rest = floatNumber % 1
            if rest == 0:
                return int(floatNumber)
            else:
                return f"{floatNumber:.1f}"
        elif count == 2:
            return f"{floatNumber:.2f}"
        elif count == 3:
            return f"{floatNumber:.3f}"
        else:
            return f"{floatNumber:.4f}"
    else:
        try:
            return f"{round(floatNumber, 4)}"
        except:
            return number


async def spaceAmount(amount):
    stringAmount = str(amount)
    stringAmountSplit = stringAmount.split(".")
    if len(stringAmountSplit) > 1:
        integerPart = stringAmountSplit[0]
        floatPart = "." + stringAmountSplit[1]
    else:
        integerPart = stringAmount
        floatPart = ""

    finishAmount = ""
    i = len(integerPart) - 1
    step = 1
    while i >= 0:
        if step == 3:
            finishAmount = " " + integerPart[i] + finishAmount
            step = 1
        else:
            finishAmount = integerPart[i] + finishAmount
            step += 1
        i -= 1

    finishAmount = finishAmount[1:] if finishAmount[0] == " " else finishAmount
    finishAmount += floatPart
    return finishAmount
