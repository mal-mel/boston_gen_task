create table files
(
    task_id   varchar(32)                   not null,
    email     text                          null,
    url       text                          not null,
    status    varchar(14) default 'in_work' not null,
    file_hash varchar(32)                   null,
    constraint table_name_task_id_uindex
        unique (task_id)
);