drop table if exists detail cascade;

create table detail (
    detail_id serial primary key,
    person_id varchar(128) references person(person_id),
    key       varchar(256),
    val       varchar(256)
);

insert into detail values (default, 'mosky', 'email', 'mosky.tw@gmail.com');
insert into detail values (default, 'mosky', 'email', 'mosky.liu@pinkoi.com');

insert into detail values (default, 'mosky', 'address', 'It is my first address.');
insert into detail values (default, 'mosky', 'address', 'It is my second address.');

insert into detail values (default, 'alice', 'email', 'alice@gmail.com');

insert into detail values (default, 'bob', 'email', 'bob@yahoo.com');
insert into detail values (default, 'bob', 'email', 'bob@gmail.com');

insert into detail values (default, 'carol', 'email', 'carol@facebook.com');
insert into detail values (default, 'carol', 'email', 'carol@gmail.com');

insert into detail values (default, 'mosky', 'email', 'mosky@ubuntu-tw.org');
