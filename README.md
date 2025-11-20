# Employee Management System

A Python web application built with Flask for managing employee records with a comprehensive dashboard and login system.

## Features

- Secure login system (Username: admin, Password: 123)
- Employee management with detailed personal and professional information
- Office position tracking with approved, filled, and vacant positions
- Settings management for offices, designations, classes, salary categories, and castes
- Responsive dashboard with statistics and navigation

## Requirements

- Python 3.6 or higher
- Flask

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Navigate to the project directory
2. Run the application:
   ```
   python app.py
   ```
3. Open your web browser and go to `http://localhost:5000`

## Login Credentials

- Username: `admin`
- Password: `123`

## Database

The application uses SQLite database which is automatically created when you run the application for the first time. The database file is named `employee.db`.

## Features Included

1. **Login Form**: Secure authentication system
2. **Dashboard**: Overview of system statistics
3. **Employee Management**: 
   - Add new employees with comprehensive information
   - View all employees in a table format
4. **Office Positions**: 
   - Track approved, filled, and vacant positions per office
5. **Settings**: 
   - Manage offices, designations, classes, salary categories, and castes

## Employee Information Fields

The employee form includes the following 21 fields:
1. संपुर्ण नांव (Full Name)
2. जेंडर (Gender)
3. जन्मतारीख (Birth Date)
4. कार्यालयाचे नांव (Office Name)
5. पदनाम (Designation)
6. क्लास (Class)
7. वेतनश्रेणी (Salary Category)
8. नोकरीत हजर दिनांक (Joining Date)
9. नोकरीत कोणत्या पदावर हजर (Joining Designation)
10. जात (Caste)
11. जात प्रवर्ग (Sub Caste)
12. जात पडताळणी झाली आहे काय? (Caste Verified)
13. बिंदु नामावतील क्रमाक (Bindu Number)
14. विभागीय परिक्षा पास आहे काय? (Department Exam Passed)
15. आर सरीता आय डी (PRAN ID)
16. बॅकचे नांव (Bank Name)
17. आयएफसी कोड (IFSC Code)
18. अकाऊट नंबर (Account Number)
19. आधार नंबर (Aadhar Number)
20. जी पी एफ नंबर (GPF Number)
21. सेवा निवृत्तीचा दिनांक (Retirement Date)

## Office Position Management

The system tracks:
- Approved positions per office
- Filled positions per office
- Vacant positions per office

## Technologies Used

- Python
- Flask (Web Framework)
- SQLite (Database)
- Bootstrap 5 (Frontend Framework)
- HTML/CSS/JavaScript

## License

This project is open source and available under the MIT License.