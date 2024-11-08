import requests
from bs4 import BeautifulSoup
import json


# Функция для сбора данных с одной страницы
def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = []
    for quote in soup.find_all('div', class_='quote'):
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        tags = [tag.text for tag in quote.find_all('a', class_='tag')]
        quotes.append({'text': text, 'author': author, 'tags': tags})
    return quotes


# Функция для сбора всех цитат по тегу
def scrape_tag(tag_url, unique_only, seen_quotes):
    page_number = 1
    all_quotes = []
    while True:
        url = f'{tag_url}/page/{page_number}/'
        quotes_on_page = scrape_page(url)
        if not quotes_on_page:
            break  # Останавливаем цикл, если на странице нет цитат

        for quote in quotes_on_page:
            quote_id = (quote['text'], quote['author'])
            if unique_only:
                if quote_id not in seen_quotes:
                    seen_quotes.add(quote_id)
                    all_quotes.append(quote)
            else:
                all_quotes.append(quote)

        page_number += 1
    return all_quotes


# Функция для сбора всех тегов с сайта и их сохранения в файл
def collect_all_tags():
    base_url = 'http://quotes.toscrape.com'
    all_tags = set()
    page_number = 1

    while True:
        url = f'{base_url}/page/{page_number}/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_tags = set()
        for quote in soup.find_all('div', class_='quote'):
            quote_tags = [tag.text for tag in quote.find_all('a', class_='tag')]
            page_tags.update(quote_tags)
        if not page_tags:
            break  # Останавливаем цикл, если на странице нет тегов

        all_tags.update(page_tags)
        page_number += 1

    # Сохраняем теги в файл all_tags.txt
    with open('all_tags.txt', 'w', encoding='utf-8') as f:
        for tag in all_tags:
            f.write(tag + '\n')

    return list(all_tags)


# Основная функция
def main():
    base_url = 'http://quotes.toscrape.com/tag'

    # Спрашиваем пользователя, нужны ли только уникальные цитаты
    unique_only = input("Вы желаете искать все цитаты (0) или только уникальные (1)? ").strip() == '1'

    # Очищаем файлы перед началом работы
    open('all_tags.txt', 'w').close()
    open('resoult.json', 'w').close()

    # Сбор всех тегов
    tags = collect_all_tags()

    # Информационное сообщение о количестве найденных тегов
    print(f"Найдено тегов: {len(tags)}")

    # Список для хранения всех цитат
    all_quotes = []
    seen_quotes = set()
    unique_quotes = set()  # множество для отслеживания уникальных цитат

    # Цикл по тегам
    for tag in tags:
        tag_url = f'{base_url}/{tag}'
        tag_quotes = scrape_tag(tag_url, unique_only, seen_quotes)
        all_quotes.extend(tag_quotes)

    # Сохранение данных в JSON-файл
    file_name = 'resoult.json'
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(all_quotes, f, ensure_ascii=False, indent=4)

    # Анализ уникальных цитат
    for quote in all_quotes:
        quote_id = (quote['text'], quote['author'])
        unique_quotes.add(quote_id)

    # Вывод сообщения о количестве найденных цитат
    if unique_only:
        print(f"Собрано всего {len(all_quotes)} уникальных цитат.")
    else:
        print(
            f"Собрано всего {len(all_quotes)} цитат (включая повторяющиеся), из которых {len(unique_quotes)} уникальных.")

    print(f"Цитаты вы найдете в папке со скриптом в файле {file_name}.")


if __name__ == "__main__":
    main()
