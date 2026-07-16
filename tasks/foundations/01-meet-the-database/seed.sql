CREATE TABLE books (
    id    integer PRIMARY KEY,
    title text    NOT NULL,
    year  integer NOT NULL
);

CREATE TABLE members (
    id   integer PRIMARY KEY,
    name text    NOT NULL
);

INSERT INTO books (id, title, year) VALUES
    (1, 'The Art of SQL',        2006),
    (2, 'Seven Databases',       2012),
    (3, 'Designing Data-Intensive Applications', 2017),
    (4, 'PostgreSQL Up & Running', 2017);

INSERT INTO members (id, name) VALUES
    (1, 'Priya'),
    (2, 'Marcus'),
    (3, 'Sofia');
