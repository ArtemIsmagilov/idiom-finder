CREATE TABLE all_idioms (
name VARCHAR UNIQUE NOT NULL
);

INSERT INTO all_idioms(name)
SELECT name FROM wiki_idioms
UNION
SELECT name FROM xdfd_idioms
ORDER BY name;
