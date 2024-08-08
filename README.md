# School Management System

This is a School Management System built with Django, a high-level Python web framework. This system allows administrators to manage students, classes, subjects, and teachers efficiently.

## Features

- Add, edit, and delete students
- Add, edit, and delete classes
- Add, edit, and delete subjects
- Assign teachers to classes and subjects
- Dynamic form handling using AJAX
- Assignments for students
- Remote classes via conference call
- In-app chatting with students
- Staff dashboard for regular duties
- Student dashboard to manage their assignments, classes, lecturers, grades, etc.

## Technologies Used

- Django 4.2.11
- Python 3.11.9
- jQuery for AJAX
- PostgreSQL (or any other preferred database)
- HTML, CSS, JavaScript

## Setup and Installation

### Prerequisites

- Python 3.11.9
- PostgreSQL 

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Goodnessmbakara/school-management-system.git
   cd school-management-system/ADVANCE-SMS-IN-DJANGO
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   - Open `ADVANCE-SMS-IN-DJANGO/settings.py` and configure your database settings.

5. Run the migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser to access the admin panel:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

8. Open your browser and go to `http://127.0.0.1:8000/admin` to log in to the admin panel with your superuser account.

## Usage

### Adding a New Class

1. Go to the admin panel at `http://127.0.0.1:8000/admin`.
2. Under the "Classes" section, click "Add class".
3. Fill out the class details and click "Save".

### Adding a New Subject

1. Go to the "Add Subject" page.
2. Select the class level and class.
3. If the class has subclasses, select the appropriate subclass.
4. Select the subject teacher and click "Add Subject".

### Adding a New Student

1. Go to the admin panel at `http://127.0.0.1:8000/admin`.
2. Under the "Students" section, click "Add student".
3. Fill out the student details and click "Save".

## Additional Features

### Assignments for Students

- Teachers can create and assign homework or projects to students.
- Students can view and submit their assignments through their dashboard.

### Remote Classes

- Integration with a video conferencing service to conduct remote classes.
- Students can join classes directly from their dashboard.

### In-App Chatting

- Secure in-app messaging for communication between students and staff.

### Staff Dashboard

- Staff can manage their classes, assignments, and communicate with students.
- Access to their schedules, tasks, and administrative duties.

### Student Dashboard

- View and manage assignments.
- Join remote classes.
- View details of their lecturers.
- Download their grades and academic reports.

## Project Structure

```
school-management-system/
├── ADVANCE-SMS-IN-DJANGO/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
├── student_management_app/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── templates/
│   │   ├── hod_template/
│   │   │   ├── add_subject_template.html
│   │   │   └── base_template.html
│   │   └── ...
│   └── ...
├── manage.py
└── README.md
```

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-branch`.
5. Submit a pull request.

## License

This project is licensed under the MIT License.

## Contact

For any questions or suggestions, feel free to open an issue or contact the project maintainer.

