import config

import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode

payment_systems = {
    'AdvCash': '87893285',
    'Payeer': '1136053',
    'Qiwi': '26808',
    'Yandex': '57378077'
}

global_values = {
        'account': config.PAYEER_ACCOUNT,
        'apiId': config.PAYEER_API_ID,
        'apiPass': config.PAYEER_API_KEY,
        'curIn': 'USD',
        'curOut': 'USD'
    }

api_url = "https://payeer.com/ajax/api/api.php?{}"

headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}


def init_values(pay_sys, requisite, amount):
    local_values = global_values
    local_values['ps'] = payment_systems[pay_sys]
    local_values['sumIn'] = amount
    local_values['param_ACCOUNT_NUMBER'] = requisite

    if pay_sys == 'Yandex':
        local_values['curOut'] = 'RUB'
    else:
        local_values['curOut'] = 'USD'
    return local_values


def payout_possibility(pay_sys, requisite, amount, is_eng):
    local_values = init_values(pay_sys, requisite, amount)
    local_values['action'] = 'initOutput'

    request = Request(api_url.format('initOutput'), data=urlencode(local_values).encode(), headers=headers)

    response = json.loads(urlopen(request).read())
    print(response)
    errors = ""
    if (not isinstance(response['errors'], list) and response['errors'] is not None) \
            or (isinstance(response['errors'], list) and response['errors']):
        if not is_eng:
            errors += "Ошибки при обработке платежа:"
        else:
            errors += "Errors while performing payment:"
        errors += '\n'
        for key in response['errors']:
            if key == 'This type of exchange is not possible':
                if not is_eng:
                    errors += "автоматический обмен из {} в {} временно запрещен".format(local_values['curIn'],
                                                                                       local_values['curOut'])
                else:
                    errors += response['errors'][key]
                errors += '\n'
            elif response['errors'][key] == 'invalid format':
                if not is_eng:
                    errors += "неправильный формат реквизита"
                else:
                    errors += "invalid requisite format"
                errors += '\n'
            elif key == 'sum_more_max':
                if not is_eng:
                    errors += "сумма превышает максимум"
                else:
                    errors += response['errors'][key]
                errors += '\n'
            elif key == 'balans_no':
                if not is_eng:
                    errors += "на счете недостаточно средств для вывода средств"
                else:
                    errors += response['errors'][key]
                errors += '\n'
            elif key == 'sum_less_min':
                if not is_eng:
                    temp = "минимальная сумма перевода: *{} {}*"
                else:
                    temp = "minimal amount for transaction is *{} {}*"
                errors += temp.format(response['errors'][key][12:], local_values['curOut']) + '\n'
    return errors


def payout(pay_sys, requisite, amount, is_eng):
    local_values = init_values(pay_sys, requisite, amount)
    local_values['action'] = 'output'

    request = Request(api_url.format('output'), data=urlencode(local_values).encode(), headers=headers)

    response = json.loads(urlopen(request).read())
    errors = ""
    if (not isinstance(response['errors'], list) and response['errors'] is not None) \
            or (isinstance(response['errors'], list) and response['errors']):
        if is_eng:
            errors = "Something went wrong. Check validity of your requisites or try again later"
        else:
            errors = "Что-то пошло не так. Проверьте правильность введеных реквизитов или повторите попытку позднее"
    else:
        errors = "Withdraw completed successfully!" if is_eng else "Вывод завершен успешно!"
    return errors


if __name__ == '__main__':
    print(payout('AdvCash', 'lester0578@gmail.com', 10, 1))
