create database nfu;

use nfu;

create table dormitory
(
    id       int      not null primary key,
    building char(15) not null,
    floor    char(2)  not null,
    room     int      not null
);

create table electric
(
    id      bigint unsigned primary key auto_increment,
    room_id int   not null,
    value   float not null,
    date    date  not null,
    index index_room_id (room_id)
);

