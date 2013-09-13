drop table if exists details;
drop table if exists users;

drop table if exists detail;
drop table if exists person;

create table person (
    person_id varchar(128) primary key,
    name      varchar(256)
);

create table detail (
    detail_id serial primary key,
    person_id varchar(128) references person(person_id),
    key       varchar(256),
    val       varchar(256)
);

create index detail_person_id_key_index on detail (person_id, key);

insert into person values ('mosky', 'Mosky Liu');
insert into person values ('andy' , 'Andy Warhol');
insert into person values ('bob'  , 'Bob Dylan');
insert into person values ('cindy', 'Cindy Crawford');

insert into detail values (default, 'mosky', 'email', 'mosky.tw@gmail.com');
insert into detail values (default, 'mosky', 'email', 'mosky.liu@pinkoi.com');

insert into detail values (default, 'mosky', 'address', 'It is my first address.');
insert into detail values (default, 'mosky', 'address', 'It is my second address.');

insert into detail values (default, 'andy', 'email', 'andy@gmail.com');

insert into detail values (default, 'bob', 'email', 'bob@yahoo.com');
insert into detail values (default, 'bob', 'email', 'bob@gmail.com');

insert into detail values (default, 'cindy', 'email', 'cindy@facebook.com');
insert into detail values (default, 'cindy', 'email', 'cindy@gmail.com');

insert into detail values (default, 'mosky', 'email', 'mosky@ubuntu-tw.org');
