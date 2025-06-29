import mysql.connector
from mysql.connector import Error

# -----------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         
    'password': 'yourpassword', 
    'database': 'GameRental'
}

# -----------------------------
def create_tables_and_data():
    schema_sql = """
    DROP DATABASE IF EXISTS GameRental;
    CREATE DATABASE GameRental;
    USE GameRental;

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

    CREATE OR REPLACE VIEW View_TotalRevenue AS
    SELECT SUM(G.RentalFee) AS TotalRevenue
    FROM Rentals R
    JOIN Games G ON R.GameCode = G.GameCode;
    """

    procedure_sql = """
    DROP PROCEDURE IF EXISTS GetTopRentedGames;
    CREATE PROCEDURE GetTopRentedGames(IN TopN INT)
    BEGIN
        SELECT G.Title, COUNT(*) AS TimesRented
        FROM Rentals R
        JOIN Games G ON R.GameCode = G.GameCode
        GROUP BY G.GameCode
        ORDER BY TimesRented DESC
        LIMIT TopN;
    END;
    """

    try:
        connection = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], password=DB_CONFIG['password'])
        cursor = connection.cursor()
        for q in schema_sql.strip().split(';'):
            if q.strip():
                cursor.execute(q + ';')
        cursor.execute(procedure_sql)
        print("Tables, sample data, view, and procedure created.")
    except Error as e:
        print(f"Error creating schema: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# -----------------------------
def run_query(query, params=None):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(query, params or ())

        if cursor.with_rows:
            result = cursor.fetchall()
            for row in result:
                print(row)
        else:
            connection.commit()
            print("Query executed successfully.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# -----------------------------
import warnings

def call_procedure(proc_name, args):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.callproc(proc_name, args)

        # Suppress DeprecationWarning temporarily
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            for result in cursor.stored_results():  # use () to avoid TypeError
                for row in result.fetchall():
                    print(row)

    except Error as e:
        print(f"Error in procedure: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# -----------------------------
def run_interview_queries():
    queries = {
        "Gamers with more than 2 rentals":
        """
        SELECT GamerID, COUNT(*) AS RentalCount
        FROM Rentals
        GROUP BY GamerID
        HAVING RentalCount > 2;
        """,

        "Total revenue from rentals":
        "SELECT * FROM View_TotalRevenue;",

        "Most rented game":
        """
        SELECT G.Title, COUNT(*) AS TimesRented
        FROM Rentals R
        JOIN Games G ON R.GameCode = G.GameCode
        GROUP BY G.GameCode
        ORDER BY TimesRented DESC
        LIMIT 1;
        """,

        "Games never rented":
        """
        SELECT Title FROM Games
        WHERE GameCode NOT IN (SELECT GameCode FROM Rentals);
        """,

        "Average rental fee by genre":
        "SELECT Genre, AVG(RentalFee) FROM Games GROUP BY Genre;",

        "Games returned late (more than 7 days)":
        """
        SELECT RentalID, DATEDIFF(ReturnDate, RentalDate) AS DaysRented
        FROM Rentals
        WHERE DATEDIFF(ReturnDate, RentalDate) > 7;
        """,

        "Most active gamer":
        """
        SELECT GamerID, COUNT(*) AS Rentals
        FROM Rentals
        GROUP BY GamerID
        ORDER BY Rentals DESC
        LIMIT 1;
        """,

        "Average salary by role":
        "SELECT Role, AVG(Salary) FROM Staff GROUP BY Role;",

        "Games rented more than once":
        """
        SELECT GameCode, COUNT(*) AS TimesRented
        FROM Rentals
        GROUP BY GameCode
        HAVING TimesRented > 1;
        """,

        "Games rented in last 30 days":
        """
        SELECT * FROM Rentals
        WHERE RentalDate >= CURDATE() - INTERVAL 30 DAY;
        """,

        "Gamer with earliest signup":
        "SELECT * FROM Gamers ORDER BY SignupDate LIMIT 1;",

        "Number of rentals per platform":
        """
        SELECT Platform, COUNT(*) AS RentalCount
        FROM Rentals R
        JOIN Games G ON R.GameCode = G.GameCode
        GROUP BY Platform;
        """,

        "Game count by developer":
        "SELECT Developer, COUNT(*) FROM Games GROUP BY Developer;",

        "Most popular genre":
        """
        SELECT Genre, COUNT(*) AS Count
        FROM Rentals R JOIN Games G ON R.GameCode = G.GameCode
        GROUP BY Genre ORDER BY Count DESC LIMIT 1;
        """,

        "Staff count per game center":
        "SELECT CenterID, COUNT(*) FROM Staff GROUP BY CenterID;"
    }

    for title, query in queries.items():
        print(f"\n{title}")
        run_query(query)

# -----------------------------
if __name__ == '__main__':
    print("\n----------------Game Rental System Interface------------\n")

    create_tables_and_data()

    print("\n ------Top 3 Most Rented Games------")
    call_procedure("GetTopRentedGames", [3])

    print("\n---------Queries--------------")
    run_interview_queries()

    print("\n---------Script completed---------")
