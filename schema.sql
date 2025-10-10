CREATE TABLE trips (
  id INT PRIMARY KEY,
  city VARCHAR(255),
  status VARCHAR(255),
  trip_date DATE
);

CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(255)
);