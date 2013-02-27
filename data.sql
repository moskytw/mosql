drop table if exists details;
drop table if exists users;

create table users (
    user_id varchar(128) primary key,
    name    varchar(256)
);

create table details (
    detail_id serial primary key,
    user_id   varchar(128) references users(user_id),
    key       varchar(256),
    val       varchar(256)
);

create index details_user_id_key_index on details (user_id, key);

insert into users values ('mosky', 'Mosky Liu');
insert into users values ('andy' , 'Andy Warhol');
insert into users values ('bob'  , 'Bob Dylan');
insert into users values ('cindy', 'Cindy Crawford');

insert into details values (default, 'mosky', 'email', 'mosky.tw@gmail.com');
insert into details values (default, 'mosky', 'email', 'mosky.liu@pinkoi.com');

insert into details values (default, 'mosky', 'address', 'It is my first address.');
insert into details values (default, 'mosky', 'address', 'It is my second address.');

insert into details values (default, 'andy', 'email', 'andy@gmail.com');

insert into details values (default, 'bob', 'email', 'bob@yahoo.com');
insert into details values (default, 'bob', 'email', 'bob@gmail.com');

insert into details values (default, 'cindy', 'email', 'cindy@facebook.com');
insert into details values (default, 'cindy', 'email', 'cindy@gmail.com');

insert into details values (default, 'mosky', 'email', 'mosky@ubuntu-tw.org');
