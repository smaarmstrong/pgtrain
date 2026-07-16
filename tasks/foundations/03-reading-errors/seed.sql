CREATE TABLE plants (
    id        integer PRIMARY KEY,
    name      text    NOT NULL,
    room      text,
    waterings integer NOT NULL
);

INSERT INTO plants (id, name, room, waterings) VALUES
    (1, 'Fern',     'Kitchen', 12),
    (2, 'Monstera', 'Lounge',   8),
    (3, 'Cactus',   NULL,       1),
    (4, 'Basil',    'Kitchen', 20);
