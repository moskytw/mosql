drop table if exists person cascade;

create table person (
    person_id varchar(128) primary key,
    name      varchar(256)
);

create index detail_person_id_key_index on detail (person_id, key);

insert into person values ('mosky', 'Mosky Liu');
insert into person values ('andy' , 'Andy Warhol');
insert into person values ('bob'  , 'Bob Dylan');
insert into person values ('cindy', 'Cindy Crawford');
