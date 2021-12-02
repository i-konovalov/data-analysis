# Аналитика в авиакомпании
# Задача
При помощи парсинга и SQL-запроса выгрузить данные с сайта и из базы, а затем проанализировать.
### Что использовал
`SQL`, `Python`, `Pandas`, `Matplotlib`, `Seaborn`, `Requests`, `BeautifulSoup`
### План
1. Изучить данные.
2. Найти пропуски, дубликаты. Обработать ошибки.
3. Анализ данных. Построить графики.
4. Написать вывод.
### Что сделал
Написал [код](#parce) для парсинга сайта, написал [запрос](#sql) к базе. Выгрузил данные, проанализировал и визуализировал.
***
### Содержание запроса к сайту <a id='parce'></a>
```python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
URL = 'https://***/festival_news/index.html'
req = requests.get(URL)
soup = BeautifulSoup(req.text, 'lxml')
columns = []
for th in soup.find('table', id='best_festivals').find('tr').find_all('th'):
    columns.append(th.text)
data = []
for i in soup.find('table', id='best_festivals').find_all('tr'):
    if not i.find_all('th'):
        row = []
        for td in i.find_all('td'):
            row.append(td.text)
        data.append(row)
festivals = pd.DataFrame(data=data, columns=columns)
```
### Содержание SQL-запроса <a id='sql'></a>
```SQL
SELECT
    SBQ.week_number AS week_number,
    SUM(SBQ.ticket_amount) AS ticket_amount,
    SBQ1.festival_week AS festival_week,
    SBQ1.festival_name AS festival_name
FROM (
    SELECT
        EXTRACT(WEEK FROM arrival_time) AS week_number,
        COUNT(ticket_flights.ticket_no) AS ticket_amount
    FROM flights
        RIGHT JOIN ticket_flights ON flights.flight_id = ticket_flights.flight_id
    WHERE
        arrival_airport IN (
            SELECT
                airport_code
            FROM
                airports
            WHERE
                city = 'Москва'
        )
        AND arrival_time::DATE BETWEEN '2018-07-23' AND '2018-09-30'
    GROUP BY
        arrival_time
) AS SBQ
    LEFT JOIN (
        SELECT
            festival_name,
            EXTRACT(WEEK FROM festival_date) AS festival_week
        FROM
            festivals
        WHERE
            festival_city = 'Москва'
            AND festival_date::date BETWEEN '2018-07-23' AND '2018-09-30'
) AS SBQ1 ON SBQ.week_number = SBQ1.festival_week
GROUP BY
    week_number,
    festival_week,
    festival_name
ORDER BY
    week_number;
```
