# -*- coding: utf-8 -*-
#Этой строкой разрешаем писать русские буквы в скрипте
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import argparse
'''
Парсим страницу https://bessmertnybarak.ru/pamyatnik/,
ищем ссылку вот в такой структуре
    <div class="item-foto">
            <div class="shell">
                <a href="/tsigelman_lyubov_moiseevna/" class="story-foto"><img src="/filesSt/9328_tsigelman_lyubov_moiseevna/tsigelman_lyubov_moiseevna.jpg" alt="Цигельман Любовь Моисеевна"></a>
                <a href="/tsigelman_lyubov_moiseevna/" class="story-name"><span>Цигельман Любовь Моисеевна</span></a>
            </div>
    </div>
РЕЗУЛЬТАТ = /tsigelman_lyubov_moiseevna/

По полученной ссылке загружаем страницу репрессированного человека
https://bessmertnybarak.ru/tsigelman_lyubov_moiseevna/
Тамищем структуру типа:
                    <div class="event">
                        <div class="nameEvent">Дата рождения:</div><div class="dataEvent">8 января 1864г.</div>
						<div class="nameEvent">Дата смерти:</div><div class="dataEvent">28 октября 1937г., на 74 году жизни</div>
						<div class="nameEvent">Социальный статус:</div><div class="dataEvent">священник, протоиерей, служил в Спасской церкви Большой Усмани, а после ее закрытия "по просьбам населения" — в Воронеже</div>
						<div class="nameEvent">Образование:</div><div class="dataEvent">Воронежская духовная семинария, окончил по 1 разряду</div>
						<div class="nameEvent">Воинское звание:</div><div class="dataEvent">не служил</div>
                        <div class="nameEvent">Место рождения:<button data="3818"></button></div><div class="dataEvent">Хмелевое <span>село</span>, Красненский район, Белгородская область, Россия <
Сверяем заголовки из этой структуры с нужными нам ключами (keys) и запоминаем данные в person_data:
{'Дата рождения': '8 января 1864г.', 'Место рождения': 'Хмелевое ', 'Место проживания': 'Воронеж, Воронежская область, Россия ', 'Национальность': 'русский', 'Дата ареста': '10 октября 1937г.'....}
добавляем данные человека в panda  data_frame и так по всем людям, но не более 100шт

сохраняем data_frame в Эксель

!!!!!!! В задании не указано, что надо сохранять фамилии репрессированных - выглядит странно!!!!!!!!!!

'''


def main():
    parser = argparse.ArgumentParser(description='Parsing the page from bessmertnybarak.ru')
    parser.add_argument('--page', help = 'URL for parsing') # Добавляем аргументы запуска скрипта: обязательный аргумент  --page
#    source = 'https://bessmertnybarak.ru/pamyatnik/' - Это больше не нужно, можем удалить
    args = parser.parse_args()  # парсим все аргументы
    source = args.page          # вытаскиваем --page в source
    keys=[  'Дата рождения',        # Эти данные мы будем сохранять, остальное проигнорируем..
            'Место рождения',
            'Место проживания',
            'Лагерное управление',
            'Национальность',
            'Дата ареста',
            'Кем приговорен',
            'Приговор',
            'Книга Памяти'
            ]
    data_frame=pd.DataFrame(columns=keys)       #Пустой dataFrame - в него будем складывать данные по людям (одна строка - один человек)

    print(f'Загружаем список со страницы {source}')
    try:
        page = requests.get(source)             #Пробуем загрузить страницу
    except requests.exceptions as e:
        print(f'Не могу загрузить исходную страницу. Ошибка:{e}')
        quit(1)
    soup = BeautifulSoup(page.text,'html.parser') #разбираем страницу парсером, получаем объект BeautifulSoup в soup
    print(f'Список успешно загружен')
    max = 100
    for n,item in enumerate(soup.find_all(class_='story-name')): #найдем на общей странице все ссылки на персонильные страницы людей и пробежим по ссылкам, за одно будем считать, сколько получилось
        if n == max: #если обработано 100 записей - то больше не надо
            break
        person_data={}                              #сюда будем сохранять данные по текщему человеку
        try:
            item.page=requests.get('https://bessmertnybarak.ru'+item.attrs['href']) # получим персональную страничку
        except requests.exceptions as e:    # Ошибка загрузки :(
            print(f'Error loading page: https://bessmertnybarak.ru/{item.attrs["href"]}, Ошибка {e} ')
            max +=1                    #Поскольку надо загрузить 100 страниц, а у нас не все получается - добавим единичку к счетчику нужных страниц
            continue                   #не получилось загрузить страницу - пробуем следующую
        print(f'\rОбработка страницы {n} ({item.contents[0].text})', end="") # выводим ход выполнения на экран, а то скучно ждать Здесь item.contents[0].text - ФИО
        item_soup=BeautifulSoup(item.page.text,'html.parser')                # Разбираем парсером страницу репрессированного
        all_items_of_current_person=item_soup.find_all(class_=['nameEvent', 'dataEvent']) #выбираем все заголовки и сами данные (нам нужно содержание элементов двух классов)
        for i,data_item in enumerate(all_items_of_current_person):  #пробежим по данным одного человека ...
            if data_item.attrs['class'][0] == 'nameEvent':     # если текущий элемент - заголовок
                if data_item.contents[0][:-1] in keys:      # если данные, без поледнего двоеточия нам нужны (столбец есть в наших ключах keys)
                    person_data.update({data_item.contents[0][:-1]:all_items_of_current_person[i+1].contents[0]})   #- сохраним данные в dict person_data {'Дата рождения': '8 января 1864г.', 'Место рождения': 'Хмелевое ', 'Место проживания': 'Воронеж, Воронежская область, Россия ', 'Национальность': 'русский', 'Дата ареста': ...'}
        try:
            data_frame=data_frame.append(person_data,ignore_index=True) #Больше нет даных по этому человеку, Добавляем person_data в data_frame (что нашлось - то и добавим)
        except TypeError as e:
            print(f'Не смогЛА добавить запись о человеке: {person_data}, ошибка:{e}') #что-то пошло не так... не добавился.. увеличим макс количество на 1
            max += 1
    data_frame = data_frame.replace(np.nan, 'NaN', regex=False)     #Заменяем пустые яейки (np.nan) на NaN - так по заданию
    try:
        data_frame.to_excel("output.xlsx")                              #Записываем excell file
    except (IOError,OSError) as e:
        print(f'Не могу записать файл, ошибка:{e}')

if __name__ == "__main__":      #запускам программу только если она запущена как скрипт, не запускаем при импорте
    main()