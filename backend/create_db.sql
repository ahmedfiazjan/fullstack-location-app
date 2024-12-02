CREATE TABLE countries (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE states (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(id)
);

CREATE TABLE cities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    state_id INTEGER NOT NULL,
    FOREIGN KEY (state_id) REFERENCES states(id)
);

CREATE TABLE locations (
    city_id INTEGER NOT NULL,
    state_id INTEGER NOT NULL,
    country_id INTEGER NOT NULL,
    zip_code TEXT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES cities(id),
    FOREIGN KEY (state_id) REFERENCES states(id),
    FOREIGN KEY (country_id) REFERENCES countries(id)
); 