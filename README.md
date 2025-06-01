# Quiz Website - Setup and Usage Guide

## Overview

This is a comprehensive quiz website built with PHP, HTML, CSS, JavaScript, and MySQL. The system features user authentication with admin approval, quiz creation and management, timed quiz-taking, and detailed result tracking.

## Features

- **User Authentication**
  - Registration with admin approval requirement
  - Secure login system
  - User profile management

- **Admin Features**
  - User registration approval
  - Quiz creation and management
  - Question and answer management
  - Detailed quiz attempt analytics

- **Quiz Taking**
  - 30-second timer for each question
  - Options to mark answers as correct/wrong
  - Ability to skip questions
  - Option to leave quiz early with progress saved

- **Result Tracking**
  - Detailed performance statistics
  - Time tracking for each answer
  - Complete answer history

## Technical Implementation

- **Backend**: PHP with MySQL database
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Authentication**: Custom implementation with secure password hashing
- **Database**: Relational database with tables for users, quizzes, questions, options, attempts, and answers

## Setup Instructions

### Prerequisites

- PHP 7.4+ or 8.0+
- MySQL 5.7+ or MariaDB 10.3+
- Web server (Apache/Nginx)
- Composer (for dependency management)

### Database Setup

1. Create a new MySQL database:
   ```sql
   CREATE DATABASE quiz_db;
   ```

2. Create a database user (or use an existing one):
   ```sql
   CREATE USER 'quizuser'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON quiz_db.* TO 'quizuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. The application will automatically create the necessary tables on first run.

### Application Setup

1. Clone or extract the project files to your web server directory.

2. Configure your database connection:
   - Edit the database connection settings in `src/main.py` if needed.
   - Default settings use:
     - Username: root
     - Password: password
     - Host: localhost
     - Port: 3306
     - Database: quiz_db

3. Install dependencies:
   ```bash
   cd /path/to/quiz_website
   pip install -r requirements.txt
   ```

4. Start the application:
   ```bash
   cd /path/to/quiz_website
   python src/main.py
   ```

5. Access the application at `http://localhost:5000`

### Default Admin Account

On first run, the system creates a default admin account:
- Username: admin
- Password: admin123

**Important**: Change the default admin password immediately after first login.

## Usage Guide

### Admin Tasks

1. **Approving User Registrations**:
   - Log in as admin
   - Go to Admin Dashboard
   - Click "Pending Approvals"
   - Review and approve/reject registrations

2. **Creating Quizzes**:
   - Go to "Quizzes" in the admin dashboard
   - Click "Create New Quiz"
   - Fill in quiz details
   - Add questions and options

3. **Managing Questions**:
   - Go to a specific quiz
   - Click "Questions"
   - Add, edit, or delete questions
   - For each question, specify options and mark the correct answer

4. **Viewing Results**:
   - Go to "Quiz Attempts" in the admin dashboard
   - View overall statistics
   - Click on specific attempts for detailed analysis

### User Tasks

1. **Registration**:
   - Click "Register" on the homepage
   - Fill in required information
   - Wait for admin approval

2. **Taking Quizzes**:
   - Log in with approved account
   - Browse available quizzes
   - Start a quiz
   - Answer questions within 30 seconds each
   - View results after completion

## Security Considerations

- All passwords are securely hashed
- User sessions are managed securely
- Admin-only routes are protected
- Input validation is implemented throughout
- CSRF protection is enabled

## Customization

- Styling: Edit CSS files in `src/static/css/`
- Frontend behavior: Modify JavaScript in `src/static/js/`
- Templates: Edit HTML templates in `src/templates/`

## Troubleshooting

- **Database Connection Issues**: Verify database credentials and ensure MySQL service is running
- **Permission Errors**: Check file/directory permissions
- **Missing Dependencies**: Ensure all requirements are installed

## License

This project is provided for educational and demonstration purposes.

---

For any questions or support, please contact the developer.
