def valid_number(elem):
    count = len([i for i in elem if i.isdigit()])
    if count == 10:
        elem = '8' + elem
    # Проверка на начальные символы номера телефона
    if elem[0] == '8' or elem[0:2] == '+7':
        elem = elem.replace('+', '', 1)
        # Проверка на количество цифр
        if count == 10 or (count == 11 and elem[0] == '8') or (count == 11 and elem[0] == '7'):
            valid_chars = set('0123456789()+-. ')

            # Проверка на допустимые символы
            if all(char in valid_chars for char in elem):
                # Преобразование номера к нужному формату
                elem = elem.replace('(', '').replace(')', '').replace('-', '').replace('.', '').replace(' ', '')
                formatted_number = '8-{}-{}-{}-{}'.format(elem[1:4], elem[4:7], elem[7:9], elem[9:])
                return True, formatted_number
            else:
                return False, "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
        else:
            return False, "Недопустимый ввод. Неверное количество цифр."
    else:
        return False, "Недопустимый ввод. Начало номера должно быть '8' или '+7' если не указать то автоматически добавляется цифра 8."

