-- Drop and recreate database
DROP DATABASE IF EXISTS GameRental;
CREATE DATABASE GameRental;
USE GameRental;

-- Tables
CREATE TABLE GameCenter (
    CenterID VARCHAR(10) PRIMARY KEY,
    Location VARCHAR(50) NOT NULL,
    ManagerID VARCHAR(10),
    Contact VARCHAR(20) UNIQUE
);

CREATE TABLE Staff (
    StaffID VARCHAR(10) PRIMARY KEY,
    FullName VARCHAR(40) NOT NULL,
    Role VARCHAR(30),
    Salary DECIMAL(10,2) CHECK (Salary >= 0),
    CenterID VARCHAR(10),
    FOREIGN KEY (CenterID) REFERENCES GameCenter(CenterID)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE Gamers (
    GamerID VARCHAR(10) PRIMARY KEY,
    GamerName VARCHAR(40) NOT NULL,
    Address VARCHAR(50),
    SignupDate DATE DEFAULT (CURRENT_DATE())
);

CREATE TABLE Games (
    GameCode VARCHAR(20) PRIMARY KEY,
    Title VARCHAR(80) NOT NULL,
    Genre VARCHAR(30),
    RentalFee DECIMAL(8,2) CHECK (RentalFee >= 0),
    Available ENUM('Yes', 'No') DEFAULT 'Yes',
    Platform VARCHAR(20),
    Developer VARCHAR(40)
);

CREATE TABLE Rentals (
    RentalID VARCHAR(10) PRIMARY KEY,
    GamerID VARCHAR(10),
    GameCode VARCHAR(20),
    RentalDate DATE NOT NULL,
    ReturnDate DATE,
    FOREIGN KEY (GamerID) REFERENCES Gamers(GamerID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (GameCode) REFERENCES Games(GameCode)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Sample Data
INSERT INTO GameCenter VALUES
('C001', 'New York', 'S001', '1234567890'),
('C002', 'Los Angeles', 'S002', '0987654321');

INSERT INTO Staff VALUES
('S001', 'Alice Smith', 'Manager', 70000, 'C001'),
('S002', 'Bob Johnson', 'Manager', 68000, 'C002');

INSERT INTO Gamers VALUES
('G001', 'John Doe', 'NY', '2023-01-01'),
('G002', 'Jane Roe', 'LA', '2023-01-15'),
('G003', 'Mike Lee', 'TX', '2023-02-01');

INSERT INTO Games VALUES
('GM001', 'FIFA 22', 'Sports', 5.99, 'Yes', 'PS5', 'EA Sports'),
('GM002', 'GTA V', 'Action', 7.99, 'Yes', 'PC', 'Rockstar'),
('GM003', 'Minecraft', 'Sandbox', 4.99, 'Yes', 'PC', 'Mojang');

INSERT INTO Rentals VALUES
('R001', 'G001', 'GM001', '2023-01-02', '2023-01-09'),
('R002', 'G001', 'GM002', '2023-01-05', '2023-01-15'),
('R003', 'G002', 'GM001', '2023-01-16', '2023-01-24'),
('R004', 'G003', 'GM003', '2023-02-10', '2023-02-18'),
('R005', 'G001', 'GM003', '2023-03-01', NULL);

-- View
CREATE OR REPLACE VIEW View_TotalRevenue AS
SELECT SUM(G.RentalFee) AS TotalRevenue
FROM Rentals R
JOIN Games G ON R.GameCode = G.GameCode;

-- Stored Procedure
DROP PROCEDURE IF EXISTS GetTopRentedGames;
DELIMITER //
CREATE PROCEDURE GetTopRentedGames(IN TopN INT)
BEGIN
    SELECT G.Title, COUNT(*) AS TimesRented
    FROM Rentals R
    JOIN Games G ON R.GameCode = G.GameCode
    GROUP BY G.GameCode
    ORDER BY TimesRented DESC
    LIMIT TopN;
END;
//
DELIMITER ;

-- 1. Gamers who rented more than 2 games
SELECT GamerID, COUNT(*) AS RentalsCount
FROM Rentals
GROUP BY GamerID
HAVING RentalsCount > 2;

-- 2. Total revenue generated from rentals
SELECT SUM(G.RentalFee) AS TotalRevenue
FROM Rentals R
JOIN Games G ON R.GameCode = G.GameCode;

-- 3. Most rented game
SELECT G.Title, COUNT(*) AS RentCount
FROM Rentals R
JOIN Games G ON R.GameCode = G.GameCode
GROUP BY G.Title
ORDER BY RentCount DESC
LIMIT 1;

-- 4. Games never rented
SELECT GameCode, Title
FROM Games
WHERE GameCode NOT IN (
    SELECT DISTINCT GameCode FROM Rentals
);

-- 5. Average rental fee by genre
SELECT Genre, AVG(RentalFee) AS AvgFee
FROM Games
GROUP BY Genre;

-- 6. Rentals with late return (assuming 7-day return policy)
SELECT R.*, DATEDIFF(ReturnDate, RentalDate) AS DaysRented
FROM Rentals R
WHERE ReturnDate IS NOT NULL AND DATEDIFF(ReturnDate, RentalDate) > 7;

-- 7. Most active gamer (by number of rentals)
SELECT G.GamerID, G.GamerName, COUNT(*) AS TotalRentals
FROM Rentals R
JOIN Gamers G ON R.GamerID = G.GamerID
GROUP BY G.GamerID
ORDER BY TotalRentals DESC
LIMIT 1;

-- 8. Average salary of staff by role
SELECT Role, AVG(Salary) AS AvgSalary
FROM Staff
GROUP BY Role;

-- 9. Games that have been rented more than once
SELECT G.GameCode, G.Title, COUNT(*) AS TimesRented
FROM Rentals R
JOIN Games G ON R.GameCode = G.GameCode
GROUP BY G.GameCode
HAVING TimesRented > 1;

-- 10. Games rented in the last 30 days
SELECT G.Title, R.RentalDate
FROM Rentals R
JOIN Games G ON R.GameCode = G.GameCode
WHERE R.RentalDate >= CURDATE() - INTERVAL 30 DAY;

-- 11. Gamer who signed up the earliest
SELECT *
FROM Gamers
ORDER BY SignupDate ASC
LIMIT 1;

-- 12. Number of rentals per platform
SELECT G.Platform, COUNT(*) AS RentalCount
FROM Rentals R
JOIN Games G ON R.GameCode = G.GameCode
GROUP BY G.Platform;

-- 13. Number of games developed by each developer
SELECT Developer, COUNT(*) AS GameCount
FROM Games
GROUP BY Developer;

-- 14. Most popular genre
SELECT Genre, COUNT(*) AS RentalCount
FROM Rentals R
JOIN Games G ON R.GameCode = G.GameCode
GROUP BY Genre
ORDER BY RentalCount DESC
LIMIT 1;

-- 15. Number of staff per game center
SELECT CenterID, COUNT(*) AS StaffCount
FROM Staff
GROUP BY CenterID;
