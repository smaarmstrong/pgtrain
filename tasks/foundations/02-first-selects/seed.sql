CREATE TABLE snacks (
    id    integer PRIMARY KEY,
    name  text    NOT NULL,
    price numeric NOT NULL,
    stock integer NOT NULL
);

INSERT INTO snacks (id, name, price, stock) VALUES
    (1, 'Flapjack',      1.20, 40),
    (2, 'Crisps',        0.90, 75),
    (3, 'Chocolate bar', 1.50, 32),
    (4, 'Apple',         0.60, 18),
    (5, 'Popcorn',       1.10, 26),
    (6, 'Cereal bar',    1.00, 51);
