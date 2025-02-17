from datetime import datetime, timedelta


def week_to_timestamp(year, week_number):
    #utowrzenie obiektu datetime dla podziałku zadanego tygodnia
    monday = datetime.strptime(f'{year}-W{week_number:02d}-1', r'%G-W%V-%u')
    #odejmuję 12 godzin w sekundach, ponieważ wyżej utworzony datetime domyślnie przyjmuje godzinę 12
    return int(monday.timestamp());