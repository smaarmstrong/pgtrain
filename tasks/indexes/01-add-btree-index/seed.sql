CREATE TABLE events (
    id      bigint PRIMARY KEY,
    token   text   NOT NULL,
    payload text   NOT NULL
);

INSERT INTO events (id, token, payload)
SELECT g, 'tok-' || g, repeat('x', 20)
FROM generate_series(1, 5000) AS g;
