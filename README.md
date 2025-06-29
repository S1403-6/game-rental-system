# Game Rental System (SQL + Python)

A database-backed game rental system project demonstrating core SQL concepts, stored procedures, views, and Python-MySQL integration.

---

## Features

- MySQL schema for managing centers, staff, games, gamers, and rentals.
- 15+ analytical SQL queries.
- Stored Procedure: `GetTopRentedGames(N)`
- View: `View_TotalRevenue`
- Python integration with error handling.

---

## 🚀 How to Run

### 1. Import the SQL Schema
```bash
mysql -u root -p < game_rental.sql
