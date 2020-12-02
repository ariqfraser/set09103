DROP TABLE if EXISTS users;
DROP TABLE if EXISTS cards;
DROP TABLE if EXISTS decks;

CREATE TABLE users (
    name varchar PRIMARY KEY NOT NULL UNIQUE,
    pass binary NOT NULL,
    joined date DEFAULT CURRENT_DATE,
    wpm30 DEFAULT 0,
    wpm60 DEFAULT 0,
    wpm15 DEFAULT 0,
    lang15 varchar,
    lang30 varchar,
    lang60 varchar
);

CREATE TABLE cards (
    cardID INTEGER PRIMARY KEY AUTOINCREMENT,
    deckID varchar NOT NULL,
    sideA varchar,
    sideB varchar
);

CREATE TABLE decks (
    deckID integer PRIMARY KEY AUTOINCREMENT,
    owner integer,
    title varchar,
    lastUpdated date
);