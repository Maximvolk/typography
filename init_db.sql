create database typography;
use typography;

create table author (
	author_id serial primary key,
	author_full_name varchar(100) not null,
	author_itn bigint not null,
	author_passport bigint not null,
	author_address varchar(100) not null,
	author_phone_number bigint not null
);

create table book (
	book_id serial primary key,
	book_title varchar(100) not null,
	circulation int not null,
	release_date date not null,
	cost_price numeric(10, 2) not null
);

create table author_book (
	author_id bigint references author(author_id) on delete cascade,
	book_id bigint references book(book_id) on delete cascade,
	author_fee numeric(10, 2) not null
);

create table employee (
	employee_id serial primary key,
	employee_full_name varchar(100) not null,
	employee_itn bigint not null,
	employee_passport bigint not null,
	employee_address varchar(100) not null,
	employee_phone_number bigint not null,
	employee_sex varchar(7) not null,
	employee_birthdate date not null,
	employee_salary numeric(10, 2) not null,
	employee_position varchar(100) not null,
	password_hash text not null
);

create table book_editor (
	editor_id bigint references employee(employee_id),
	book_id bigint references book(book_id) on delete cascade,
	main_editor boolean not null
);

create table contract (
	contract_id serial primary key,
	book_id bigint references book(book_id),
	manager_id bigint references employee(employee_id),
	sign_date date not null
);

create table customer (
	customer_id serial primary key,
	customer_full_name varchar(100) not null,
	customer_address varchar(100) not null
);

create table customer_order (
	order_id serial primary key,
	customer_id bigint references customer(customer_id),
	receipt_date date not null,
	completion_date date
);

create table order_book (
	order_id bigint references customer_order(order_id) on delete cascade,
	book_id bigint references book(book_id),
	books_amount int not null,
	book_price numeric(10, 2) not null
);