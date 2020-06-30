insert into employee values (default, 'Администратор', 1234321, 4018654234,
	'Варшавская, д.11, кв.342', 89312242211, 'Мужской', '02-01-2019', 80000,
	'admin', 'pbkdf2:sha256:150000$58rqYvqQ$e3f1dd1959fc2b309d66776af98ac505e160d3722c31751179314b58703151db');

insert into "author" values
    (default, 'Л.Н. Толстой', 189098723, 4013876543, 'Кирочная, д.11, кв.32', 89324566345),
    (default, 'Ф.М. Достоевский', 123456789, 4012987234, '1-ая Советская, д.3, кв.11', 87563542415),
    (default, 'М.А. Булгаков', 987654321, 5748263547, 'Кузнецовская, д.13, кв.48', 78645672534),
    (default, 'А.П. Чехов', 756392854, 5746273658, 'Хошимина, д.1, кв.107', 89076785674),
    (default, 'И.А. Бродский', 574826453, 5867263547, 'Луначарского, д.23, кв.65', 83457658754),
    (default, 'А.Н. Стругацкий', 364857696, 4756364578, 'Тверская, д.55, кв.123', 85342653476),
    (default, 'Б.Н. Стругацкий', 657485623, 6857465376, 'Садовая, д.89, кв.34', 86455437698);

insert into "book" values
    (default, 'Понедельник начинается в субботу', 12000, '1965-01-12', 100000),
    (default, 'Анна Каренина', 200000, '1877-02-04', 130),
    (default, 'Идиот', 200000, '1869-08-11', 1000),
    (default, 'Дьяволиада', 30000, '1924-10-03', 1670),
    (default, 'Дуэль', 40000, '1891-12-01', 1100),
    (default, 'Меньше единицы', 1000, '1986-07-22', 11100),
    (default, 'Бесы', 170000, '1872-11-11', 100000),
    (default, 'Сказка о тройке', 100000, '1968-08-21', 20000),
    (default, 'Мастер и Маргарита', 400000, '1967-02-11', 10000),
    (default, 'Трудно быть богом', 120000, '1964-06-13', 8000);

insert into "author_book" values
    (1, 2, 7680),
    (2, 3, 10000),
    (2, 7, 5),
    (3, 4, 880),
    (3, 9, 150),
    (4, 5, 1000),
    (5, 6, 5),
    (6, 1, 450),
    (6, 8, 4789),
    (6, 10, 22267),
    (7, 1, 3345),
    (7, 8, 9870),
    (7, 10, 340);

insert into customer values 
	(default, 'М.В. Волков', 'Кирочная, д.11, кв.32'),
	(default, 'А.С. Сидоров', 'Тверская, д.55, кв.123'),
	(default, 'В.В. Николаев', 'Садовая, д.89, кв.34');

insert into customer_order values
	(default, 1, '01-01-2016', '01-15-2016'),
	(default, 2, '10-03-2014', '10-14-2014'),
	(default, 3, '05-09-2019', '06-01-2019');

insert into order_book values
	(1, 3, 2, 800),
	(1, 6, 1, 1300),
	(2, 10, 5, 1000),
	(3, 2, 4, 3300);

insert into book_editor values
	(2, 1, false),
	(2, 2, true),
	(2, 3, true),
	(5, 3, false),
	(5, 4, true),
	(2, 5, false),
	(5, 5, true),
	(5, 6, true),
	(2, 7, true),
	(2, 8, true),
	(2, 9, true),
	(5, 10, true);

insert into contract values
	(default, 1, 3, '06-03-2019'),
	(default, 2, 3, '07-11-2018'),
	(default, 3, 3, '10-10-2010'),
	(default, 4, 6, '06-01-2020'),
	(default, 5, 6, '11-01-2019'),
	(default, 6, 3, '06-01-1999'),
	(default, 7, 6, '08-02-1996'),
	(default, 8, 3, '06-07-1988'),
	(default, 9, 3, '09-06-1998'),
	(default, 10, 6, '12-01-2014');