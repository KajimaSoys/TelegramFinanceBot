create table budget(
    codename varchar(255) primary key,
    daily_limit integer
);

create table category_exp(
    codename varchar(255) primary key,
    name varchar(255),
    is_base_expense boolean,
    aliases text
);

create table category_inc(
    codename varchar(255) primary key,
    name varchar(255),
    is_base_expense boolean,
    aliases text
);

create table expense(
    id integer primary key,
    amount integer,
    created datetime,
    category_exp_codename integer,
    raw_text text,
    FOREIGN KEY(category_exp_codename) REFERENCES category_exp(codename)
);

create table income(
    id integer primary key,
    amount integer,
    created datetime,
    category_inc_codename integer,
    raw_text text,
    FOREIGN KEY(category_inc_codename) REFERENCES category_inc(codename)
);

insert into category_exp (codename, name, is_base_expense, aliases)
values
    ("products", "продукты", true, "еда"),
    ("coffee", "кофе", true, ""),
    ("dinner", "обед", true, "столовая, ланч, бизнес-ланч, бизнес ланч"),
    ("cafe", "кафе", true, "ресторан, рест, мак, макдональдс, макдак, kfc, ilpatio, il patio"),
    ("trasfer", "перевод", true, "сбер, альфа, тинькофф, банк, сбербанк"),
    ("transport", "общ. транспорт", false, "метро, автобус, metro"),
    ("taxi", "такси", false, "яндекс такси, yandex taxi"),
    ("phone", "телефон", false, "теле2, связь"),
    ("books", "книги", false, "литература, литра, лит-ра"),
    ("internet", "интернет", false, "инет, inet"),
    ("subscriptions", "подписки", false, "подписка"),
    ("other", "прочее", true, "");

insert into category_inc (codename, name, is_base_expense, aliases)
values
    ("salary", "зарплата", false, "зп, работа"),
    ("scholarship", "стипендия", false ,"стипа, вуз, ВУЗ"),
    ("trasfer", "перевод", true, "сбер, альфа, тинькофф, банк, сбербанк"),
    ("other", "прочее", true, "");

insert into budget(codename, daily_limit) values ('base', 500);
