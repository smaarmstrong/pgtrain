CREATE TABLE employees (
    id         integer PRIMARY KEY,
    name       text    NOT NULL,
    department text    NOT NULL,
    salary     numeric NOT NULL
);

INSERT INTO employees (id, name, department, salary) VALUES
    (1, 'Ada',    'Engineering', 95000),
    (2, 'Bjorn',  'Engineering', 58000),
    (3, 'Chen',   'Engineering', 72000),
    (4, 'Dara',   'Sales',       65000),
    (5, 'Evie',   'Engineering', 60000),
    (6, 'Faisal', 'Support',     48000),
    (7, 'Gwen',   'Engineering', 81000);
