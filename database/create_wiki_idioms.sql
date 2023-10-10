CREATE TABLE wiki_idioms (
name VARCHAR UNIQUE NOT NULL
);

INSERT INTO wiki_idioms(name)
SELECT name FROM idiom
UNION
SELECT name FROM form_idiom
ORDER BY name;
