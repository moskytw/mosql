drop table if exists "order";
drop table if exists product;
drop table if exists member;

create table member (
    member_id   varchar(128) primary key,
    member_name varchar(256)
);

create table product (
    product_id    varchar(256) primary key,
    product_name  varchar(256),
    product_price numeric(14, 4)
);

create table "order" (
    order_id       serial primary key,
    member_id      varchar(128) references member(member_id),
    product_id     varchar(256) references product(product_id),
    order_quantity smallint
);

insert into member values ('mosky' , 'Mosky Liu');
insert into member values ('albin' , 'Albin Jeng');
insert into member values ('horace', 'Horace Da');
insert into member values ('seb'   , 'Seb Te');

insert into product values ('air-2012' , 'Apple MacBook Air 13" 128G'          , 34900);
insert into product values ('iphone-5' , 'Apple iPhone 5 64G'                  , 25290);
insert into product values ('ipad-mini', 'Apple iPad Mini WiFi 64G'            , 16190);
insert into product values ('ipad-4'   , 'Apple iPad with Retina 4 4G+WiFi 32G', 21590);
insert into product values ('air-2013' , '2013 Apple MacBook Air 13" 128G '    , 34899);

insert into "order" values (default, 'seb'   , 'air-2012', 24);
insert into "order" values (default, 'albin' , 'air-2012', 1);
insert into "order" values (default, 'seb'   , 'iphone-5', 57);
insert into "order" values (default, 'horace', 'iphone-5', 1);
insert into "order" values (default, 'seb'   , 'air-2013', 45);
insert into "order" values (default, 'albin' , 'air-2013', 1);
insert into "order" values (default, 'mosky' , 'air-2013', 1);


