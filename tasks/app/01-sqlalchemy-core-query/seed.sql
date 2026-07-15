CREATE TABLE sales (
    id     integer PRIMARY KEY,
    region text    NOT NULL,
    amount numeric NOT NULL
);

INSERT INTO sales (id, region, amount) VALUES
    (1, 'north', 100),
    (2, 'south',  50),
    (3, 'north',  25),
    (4, 'east',  200),
    (5, 'south',  75),
    (6, 'north',  10);
