DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
  id INTEGER NOT NULL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  phone VARCHAR(32) NOT NULL,
  token VARCHAR(64) NOT NULL
);