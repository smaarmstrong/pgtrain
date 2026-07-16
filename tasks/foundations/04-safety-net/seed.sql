CREATE TABLE vault (
    id   integer PRIMARY KEY,
    item text    NOT NULL
);

INSERT INTO vault (id, item) VALUES
    (1, 'deed'),
    (2, 'will'),
    (3, 'medal');
