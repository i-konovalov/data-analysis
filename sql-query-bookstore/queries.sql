-- Запрос 1. Посчитайте, сколько книг вышло после 1 января 2000 года.
  SELECT COUNT(DISTINCT(book_id))
    FROM books
   WHERE publication_date >= '2000-01-01';
 
-- Запрос 2. Для каждой книги посчитайте количество обзоров и среднюю оценку.
  SELECT books.title AS title,
         count(distinct(review_id)) AS cnt_reviews,
         avg(rating) AS avg_rating
    FROM books
         LEFT JOIN reviews
         ON books.book_id = reviews.book_id
         LEFT JOIN ratings
         ON books.book_id = ratings.book_id
GROUP BY books.book_id;

-- Запрос 3. Определите издательство, которое выпустило наибольшее число книг толще 50 страниц — так вы исключите из анализа брошюры.
  SELECT SBQ.publisher
    FROM (SELECT publishers.publisher AS publisher,
                 COUNT(DISTINCT(books.book_id)) AS cnt_books
            FROM books
                 LEFT JOIN publishers
                 ON books.publisher_id = publishers.publisher_id
           WHERE books.num_pages > 50
        GROUP BY publishers.publisher
        ORDER BY COUNT(DISTINCT(books.book_id)) DESC
           LIMIT 1) AS SBQ;
           
-- Запрос 4. Определите автора с самой высокой средней оценкой книг — учитывайте только книги с 50 и более оценками.
  SELECT authors.author AS author
    FROM books
         LEFT JOIN ratings
         ON books.book_id = ratings.book_id
         LEFT JOIN authors
         ON books.author_id = authors.author_id
   WHERE books.author_id IN
         (SELECT books.author_id
            FROM books
                 LEFT JOIN ratings
                 ON books.book_id = ratings.book_id
        GROUP BY books.book_id,
                 books.author_id
          HAVING count(ratings.rating_id) >= 50)
GROUP BY authors.author
ORDER BY AVG(ratings.rating) DESC
   LIMIT 1;
   
-- Запрос 5. Посчитайте среднее количество обзоров от пользователей, которые поставили больше 50 оценок.
  SELECT AVG(SBQ.count) AS avg_count
    FROM (SELECT username,
                 COUNT(review_id) AS count
            FROM reviews
           WHERE username IN
                 (SELECT username
                    FROM ratings
                GROUP BY username
                  HAVING COUNT(rating_id) > 50)
        GROUP BY username) AS SBQ;
