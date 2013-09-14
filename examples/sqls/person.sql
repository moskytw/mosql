drop table if exists person cascade;

create table person (
    person_id varchar(128) primary key,
    name      varchar(256)
);

create index detail_person_id_key_index on detail (person_id, key);

insert into person values ('mosky', 'Mosky Liu');
insert into person values ('alice', 'Andy');
insert into person values ('bob'  , 'Bob');
insert into person values ('carol', 'Carol');
