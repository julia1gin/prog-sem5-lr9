logins = set()
cashbacks = []
persons = {}

class person:
    def __init__(self, login):
        self.login = login
        logins.add(login)
        self.expenses = 0


class cashback:
    def __init__(self, name, percent, threshold):
        self.name = name
        self.percent = percent
        self.threshold = threshold
        self.next = ''


def sort_cashbacks():
    global cashbacks
    cashbacks = sorted(cashbacks, key=lambda cb: cb.threshold)

def add_person(login, password):
    persons[login + password] = person(login)

def get_person(login, password):
    return persons[login+password]

def check_discount_lvl(nperson: person):
    print('in progress')
    nplan = cashbacks[0]
    for plan in range(len(cashbacks)):
        if nperson.expenses >= cashbacks[plan].threshold:
            nplan = cashbacks[plan]
            if plan+1 < len(cashbacks):
                print(cashbacks[plan].name)
                nplan.next = 'через ' + str(cashbacks[plan+1].threshold-nperson.expenses) + ' рублей'
            else:
                nplan.next = 'Максимальный уровень'
    return nplan

def few_tests():
    cashbacks.append(cashback('Отсутствует', 0, 0))
    cashbacks.append(cashback('Серебряный', 10, 15_000))
    cashbacks.append(cashback('Золотой', 20, 75_000))
    cashbacks.append(cashback('Платиновый', 30, 300_000))
    sort_cashbacks()

    add_person('Admin', 'admin')
    persons['Adminadmin'].expenses = 25_000
    add_person('NewPerson', 'Password')
    persons['NewPersonPassword'].expenses = 100_000
    add_person('Petya', 'qqqwww12!')
    persons['Petyaqqqwww12!'].expenses = 1_000_000
    add_person('NewPerson2', 'addingnewperson')


if __name__ == "__main__":
    few_tests()
    p = persons['Petyaqqqwww12!']
    print(check_discount_lvl(p).name)