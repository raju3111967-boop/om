from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database initialization
def init_db():
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS offices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office_name TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS designations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        designation_name TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS salary_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS castes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caste_name TEXT UNIQUE NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sub_castes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caste_id INTEGER,
        sub_caste_name TEXT NOT NULL,
        FOREIGN KEY (caste_id) REFERENCES castes(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        birth_date DATE NOT NULL,
        office_id INTEGER,
        designation_id INTEGER,
        class_id INTEGER,
        salary_category_id INTEGER,
        joining_date DATE,
        joining_designation_id INTEGER,
        caste_id INTEGER,
        sub_caste_id INTEGER,
        caste_verified BOOLEAN DEFAULT FALSE,
        caste_verification_date DATE,
        bindu_number TEXT,
        department_exam_passed BOOLEAN DEFAULT FALSE,
        department_exam_year INTEGER,
        pranidhi_id TEXT,
        bank_name TEXT,
        ifsc_code TEXT,
        account_number TEXT,
        aadhar_number TEXT,
        gpf_number TEXT,
        retirement_date DATE,
        /* Transfer history fields */
        previous_office_release_date DATE,
        previous_district TEXT,
        previous_designation TEXT,
        current_joining_date DATE,
        FOREIGN KEY (office_id) REFERENCES offices(id),
        FOREIGN KEY (designation_id) REFERENCES designations(id),
        FOREIGN KEY (class_id) REFERENCES classes(id),
        FOREIGN KEY (salary_category_id) REFERENCES salary_categories(id),
        FOREIGN KEY (joining_designation_id) REFERENCES designations(id),
        FOREIGN KEY (caste_id) REFERENCES castes(id),
        FOREIGN KEY (sub_caste_id) REFERENCES sub_castes(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS office_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office_id INTEGER,
        designation_id INTEGER,
        approved_count INTEGER DEFAULT 0,
        filled_count INTEGER DEFAULT 0,
        vacant_count INTEGER DEFAULT 0,
        FOREIGN KEY (office_id) REFERENCES offices(id),
        FOREIGN KEY (designation_id) REFERENCES designations(id)
    )''')
    
    # Create office profile table
    c.execute('''CREATE TABLE IF NOT EXISTS office_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office_name TEXT,
        office_address TEXT,
        email TEXT,
        phone TEXT,
        officer_name TEXT,
        designation TEXT,
        district_name TEXT,
        senior_clerk_names TEXT,
        junior_clerk_names TEXT
    )''')
    
    # Create transfer history table
    c.execute('''CREATE TABLE IF NOT EXISTS transfer_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        previous_office_release_date DATE,
        previous_district TEXT,
        previous_designation TEXT,
        current_joining_date DATE,
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )''')
    
    # Create promotion history table
    c.execute('''CREATE TABLE IF NOT EXISTS promotion_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        designation TEXT,
        joining_date DATE,
        promotion_date DATE,
        designation_name TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )''')
    
    # Insert default data
    try:
        c.execute("INSERT INTO offices (office_name) VALUES ('मुख्यालय')")
        c.execute("INSERT INTO offices (office_name) VALUES ('उपकार्यालय 1')")
        c.execute("INSERT INTO offices (office_name) VALUES ('उपकार्यालय 2')")
        
        c.execute("INSERT INTO designations (designation_name) VALUES ('जेसी')")
        c.execute("INSERT INTO designations (designation_name) VALUES ('एनक्लेव')")
        c.execute("INSERT INTO designations (designation_name) VALUES ('लेक्टर')")
        
        c.execute("INSERT INTO classes (class_name) VALUES ('क्लास 1')")
        c.execute("INSERT INTO classes (class_name) VALUES ('क्लास 2')")
        c.execute("INSERT INTO classes (class_name) VALUES ('क्लास 3')")
        c.execute("INSERT INTO classes (class_name) VALUES ('क्लास 4')")
        
        c.execute("INSERT INTO salary_categories (category_name) VALUES ('श्रेणी A')")
        c.execute("INSERT INTO salary_categories (category_name) VALUES ('श्रेणी B')")
        c.execute("INSERT INTO salary_categories (category_name) VALUES ('श्रेणी C')")
        
        c.execute("INSERT INTO castes (caste_name) VALUES ('हिंदु')")
        c.execute("INSERT INTO castes (caste_name) VALUES ('मुस्लिम')")
        c.execute("INSERT INTO castes (caste_name) VALUES ('इतर')")
        
        c.execute("INSERT INTO sub_castes (caste_id, sub_caste_name) VALUES (1, 'मागासवर्ग')")
        c.execute("INSERT INTO sub_castes (caste_id, sub_caste_name) VALUES (1, 'अन्य मागासवर्ग')")
        c.execute("INSERT INTO sub_castes (caste_id, sub_caste_name) VALUES (3, 'इतर')")
        
        # Insert default office profile if not exists
        c.execute("SELECT COUNT(*) FROM office_profile")
        if c.fetchone()[0] == 0:
            c.execute("""INSERT INTO office_profile 
                         (office_name, office_address, email, phone, officer_name, designation, district_name, senior_clerk_names, junior_clerk_names)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                      ("मुख्यालय", "", "", "", "", "", "", "", ""))
        
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Data already exists
    
    conn.close()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple authentication
        if username == 'admin' and password == '123':
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get statistics
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Total employees
    c.execute("SELECT COUNT(*) FROM employees")
    total_employees = c.fetchone()[0]
    
    # Total offices
    c.execute("SELECT COUNT(*) FROM offices")
    total_offices = c.fetchone()[0]
    
    # Total designations
    c.execute("SELECT COUNT(*) FROM designations")
    total_designations = c.fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html', 
                          total_employees=total_employees,
                          total_offices=total_offices,
                          total_designations=total_designations)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/employees')
def employees():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT e.*, o.office_name, d.designation_name, c.class_name, sc.category_name,
                 cd.caste_name, s.sub_caste_name, jd.designation_name as joining_designation_name
                 FROM employees e
                 LEFT JOIN offices o ON e.office_id = o.id
                 LEFT JOIN designations d ON e.designation_id = d.id
                 LEFT JOIN classes c ON e.class_id = c.id
                 LEFT JOIN salary_categories sc ON e.salary_category_id = sc.id
                 LEFT JOIN castes cd ON e.caste_id = cd.id
                 LEFT JOIN sub_castes s ON e.sub_caste_id = s.id
                 LEFT JOIN designations jd ON e.joining_designation_id = jd.id''')
    
    employees = c.fetchall()
    conn.close()
    
    return render_template('employees.html', employees=employees)

@app.route('/employee/<int:id>')
def view_employee(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT e.*, o.office_name, d.designation_name, c.class_name, sc.category_name,
                 cd.caste_name, s.sub_caste_name, jd.designation_name as joining_designation_name
                 FROM employees e
                 LEFT JOIN offices o ON e.office_id = o.id
                 LEFT JOIN designations d ON e.designation_id = d.id
                 LEFT JOIN classes c ON e.class_id = c.id
                 LEFT JOIN salary_categories sc ON e.salary_category_id = sc.id
                 LEFT JOIN castes cd ON e.caste_id = cd.id
                 LEFT JOIN sub_castes s ON e.sub_caste_id = s.id
                 LEFT JOIN designations jd ON e.joining_designation_id = jd.id
                 WHERE e.id = ?''', (id,))
    
    employee = c.fetchone()
    
    if employee:
        # Get transfer history
        c.execute("SELECT * FROM transfer_history WHERE employee_id = ?", (id,))
        transfer_history = c.fetchall()
        
        # Get promotion history
        c.execute("SELECT * FROM promotion_history WHERE employee_id = ?", (id,))
        promotion_history = c.fetchall()
        
        # Get all designations for display
        c.execute("SELECT id, designation_name FROM designations")
        designations = c.fetchall()
        
        conn.close()
        
        return render_template('view_employee.html', employee=employee, 
                              transfer_history=transfer_history, 
                              promotion_history=promotion_history,
                              designations=designations)
    else:
        flash('कर्मचारी आढळला नाही')
        return redirect(url_for('employees'))

@app.route('/employee/<int:id>/edit', methods=['GET', 'POST'])
def edit_employee(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get employee data
    c.execute('''SELECT e.*, o.office_name, d.designation_name, c.class_name, sc.category_name,
                 cd.caste_name, s.sub_caste_name, jd.designation_name as joining_designation_name
                 FROM employees e
                 LEFT JOIN offices o ON e.office_id = o.id
                 LEFT JOIN designations d ON e.designation_id = d.id
                 LEFT JOIN classes c ON e.class_id = c.id
                 LEFT JOIN salary_categories sc ON e.salary_category_id = sc.id
                 LEFT JOIN castes cd ON e.caste_id = cd.id
                 LEFT JOIN sub_castes s ON e.sub_caste_id = s.id
                 LEFT JOIN designations jd ON e.joining_designation_id = jd.id
                 WHERE e.id = ?''', (id,))
    
    employee = c.fetchone()
    
    if not employee:
        flash('कर्मचारी आढळला नाही')
        return redirect(url_for('employees'))
    
    # Get transfer history
    c.execute("SELECT * FROM transfer_history WHERE employee_id = ?", (id,))
    transfer_history = c.fetchall()
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form['full_name']
        gender = request.form['gender']
        birth_date = request.form['birth_date']
        office_id = request.form['office_id']
        designation_id = request.form['designation_id']
        class_id = request.form['class_id']
        salary_category_id = request.form['salary_category_id']
        joining_date = request.form['joining_date']
        joining_designation_id = request.form['joining_designation_id']
        caste_id = request.form['caste_id']
        sub_caste_id = request.form.get('sub_caste_id', None)
        caste_verified = 'caste_verified' in request.form
        caste_verification_date = request.form.get('caste_verification_date', None)
        bindu_number = request.form['bindu_number']
        department_exam_passed = 'department_exam_passed' in request.form
        department_exam_year = request.form.get('department_exam_year', None)
        pranidhi_id = request.form['pranidhi_id']
        bank_name = request.form['bank_name']
        ifsc_code = request.form['ifsc_code']
        account_number = request.form['account_number']
        aadhar_number = request.form['aadhar_number']
        gpf_number = request.form['gpf_number']
        
        # Transfer history fields (first row)
        previous_office_release_date = request.form.get('previous_office_release_date', None)
        previous_district = request.form.get('previous_district', '')
        previous_designation = request.form.get('previous_designation', '')
        current_joining_date = request.form.get('current_joining_date', None)
        
        # Calculate retirement date based on birth date and class
        # For classes 1-4: 58 years from birth date
        # For class 4: 60 years from birth date
        retirement_date = None
        if birth_date:
            birth_datetime = datetime.strptime(birth_date, '%Y-%m-%d')
            if class_id in ['1', '2', '3']:  # Classes 1-3
                retirement_date = birth_datetime.replace(year=birth_datetime.year + 58).strftime('%Y-%m-%d')
            elif class_id == '4':  # Class 4
                retirement_date = birth_datetime.replace(year=birth_datetime.year + 60).strftime('%Y-%m-%d')
        
        # Store old office and designation for position update
        old_office_id = employee['office_id']
        old_designation_id = employee['designation_id']
        
        # Update employee data
        c.execute('''UPDATE employees SET
            full_name = ?, gender = ?, birth_date = ?, office_id = ?, designation_id = ?, class_id = ?, 
            salary_category_id = ?, joining_date = ?, joining_designation_id = ?, caste_id = ?, 
            sub_caste_id = ?, caste_verified = ?, caste_verification_date = ?, bindu_number = ?, 
            department_exam_passed = ?, department_exam_year = ?, pranidhi_id = ?, bank_name = ?, 
            ifsc_code = ?, account_number = ?, aadhar_number = ?, gpf_number = ?, retirement_date = ?,
            previous_office_release_date = ?, previous_district = ?, 
            previous_designation = ?, current_joining_date = ?
            WHERE id = ?''',
        (full_name, gender, birth_date, office_id, designation_id, class_id, 
         salary_category_id, joining_date, joining_designation_id, caste_id, 
         sub_caste_id, caste_verified, caste_verification_date, bindu_number, 
         department_exam_passed, department_exam_year, pranidhi_id, bank_name, 
         ifsc_code, account_number, aadhar_number, gpf_number, retirement_date,
         previous_office_release_date, previous_district, 
         previous_designation, current_joining_date, id))
        
        conn.commit()
        
        # Handle existing transfer history records
        existing_transfer_ids = request.form.getlist('existing_transfer_id[]')
        existing_release_dates = request.form.getlist('existing_transfer_release_date[]')
        existing_districts = request.form.getlist('existing_transfer_district[]')
        existing_designations = request.form.getlist('existing_transfer_designation[]')
        existing_joining_dates = request.form.getlist('existing_transfer_joining_date[]')
        
        # Update or delete existing records
        for i in range(len(existing_transfer_ids)):
            transfer_id = existing_transfer_ids[i]
            release_date = existing_release_dates[i] if i < len(existing_release_dates) else None
            district = existing_districts[i] if i < len(existing_districts) else ''
            designation = existing_designations[i] if i < len(existing_designations) else ''
            joining_date = existing_joining_dates[i] if i < len(existing_joining_dates) else None
            
            if district or designation:
                # Update existing record
                c.execute('''UPDATE transfer_history SET 
                            previous_office_release_date = ?, 
                            previous_district = ?, previous_designation = ?, current_joining_date = ?
                            WHERE id = ?''',
                          (release_date, district, designation, joining_date, transfer_id))
            else:
                # Delete record if all fields are empty
                c.execute("DELETE FROM transfer_history WHERE id = ?", (transfer_id,))
        
        conn.commit()
        
        # Add new transfer history records
        transfer_release_dates = request.form.getlist('transfer_release_date[]')
        transfer_districts = request.form.getlist('transfer_district[]')
        transfer_designations = request.form.getlist('transfer_designation[]')
        transfer_joining_dates = request.form.getlist('transfer_joining_date[]')
        
        for i in range(len(transfer_release_dates)):
            release_date = transfer_release_dates[i] if i < len(transfer_release_dates) else None
            district = transfer_districts[i] if i < len(transfer_districts) else ''
            designation = transfer_designations[i] if i < len(transfer_designations) else ''
            joining_date = transfer_joining_dates[i] if i < len(transfer_joining_dates) else None
            
            if district or designation:
                c.execute('''INSERT INTO transfer_history 
                            (employee_id, previous_office_release_date, 
                             previous_district, previous_designation, current_joining_date)
                            VALUES (?, ?, ?, ?, ?)''',
                          (id, release_date, district, designation, joining_date))
                conn.commit()
        
        # Update promotion history
        # For now, we'll just update the initial joining record
        c.execute('''UPDATE promotion_history SET 
                    designation = ?, joining_date = ?, promotion_date = ?
                    WHERE employee_id = ? AND joining_date = promotion_date''',
                  (joining_designation_id, joining_date, joining_date, id))
        conn.commit()
        
        # Handle existing promotion history records
        existing_promotion_ids = request.form.getlist('existing_promotion_id[]')
        existing_promotion_designation_ids = request.form.getlist('existing_promotion_designation_id[]')
        existing_promotion_joining_dates = request.form.getlist('existing_promotion_joining_date[]')
        existing_promotion_dates = request.form.getlist('existing_promotion_date[]')
        existing_promotion_designation_names = request.form.getlist('existing_promotion_designation_name[]')
        
        # Update or delete existing records
        for i in range(len(existing_promotion_ids)):
            promotion_id = existing_promotion_ids[i]
            designation_id = existing_promotion_designation_ids[i] if i < len(existing_promotion_designation_ids) else None
            joining_date = existing_promotion_joining_dates[i] if i < len(existing_promotion_joining_dates) else None
            promotion_date = existing_promotion_dates[i] if i < len(existing_promotion_dates) else None
            designation_name = existing_promotion_designation_names[i] if i < len(existing_promotion_designation_names) else ''
            
            if designation_id and promotion_date:
                # Update existing record
                c.execute('''UPDATE promotion_history SET 
                            designation = ?, joining_date = ?, promotion_date = ?, designation_name = ?
                            WHERE id = ?''',
                          (designation_id, joining_date, promotion_date, designation_name, promotion_id))
            else:
                # Delete record if required fields are empty (but not the initial joining record)
                c.execute("SELECT joining_date, promotion_date FROM promotion_history WHERE id = ?", (promotion_id,))
                record = c.fetchone()
                if record and record[0] != record[1]:  # Don't delete the initial joining record
                    c.execute("DELETE FROM promotion_history WHERE id = ?", (promotion_id,))
        
        conn.commit()
        
        # Add new promotion history records
        promotion_designation_ids = request.form.getlist('promotion_designation_id[]')
        promotion_joining_dates = request.form.getlist('promotion_joining_date[]')
        promotion_dates = request.form.getlist('promotion_date[]')
        promotion_designation_names = request.form.getlist('promotion_designation_name[]')
        
        for i in range(len(promotion_designation_ids)):
            designation_id = promotion_designation_ids[i] if i < len(promotion_designation_ids) else None
            joining_date = promotion_joining_dates[i] if i < len(promotion_joining_dates) else None
            promotion_date = promotion_dates[i] if i < len(promotion_dates) else None
            designation_name = promotion_designation_names[i] if i < len(promotion_designation_names) else ''
            
            if designation_id and promotion_date:
                c.execute('''INSERT INTO promotion_history 
                            (employee_id, designation, joining_date, promotion_date, designation_name)
                            VALUES (?, ?, ?, ?, ?)''',
                          (id, designation_id, joining_date, promotion_date, designation_name))
                conn.commit()
        
        conn.close()
        
        # Update office position counts for old position if it changed
        if old_office_id != office_id or old_designation_id != designation_id:
            # Update old position counts
            update_office_position_counts(old_office_id, old_designation_id)
            # Update new position counts
            update_office_position_counts(office_id, designation_id)
        else:
            # Position didn't change, just update the current position
            update_office_position_counts(office_id, designation_id)
        
        flash('कर्मचारी यशस्वीरित्या अद्यतनित केला गेला!')
        return redirect(url_for('employees'))
    
    # Get dropdown data
    c.execute("SELECT id, office_name FROM offices")
    offices = c.fetchall()
    
    c.execute("SELECT id, designation_name FROM designations")
    designations = c.fetchall()
    
    c.execute("SELECT id, class_name FROM classes")
    classes = c.fetchall()
    
    c.execute("SELECT id, category_name FROM salary_categories")
    salary_categories = c.fetchall()
    
    c.execute("SELECT id, caste_name FROM castes")
    castes = c.fetchall()
    
    c.execute("SELECT id, sub_caste_name FROM sub_castes")
    sub_castes = c.fetchall()
    
    conn.close()
    
    return render_template('edit_employee.html', 
                          employee=employee,
                          offices=offices,
                          designations=designations,
                          classes=classes,
                          salary_categories=salary_categories,
                          castes=castes,
                          sub_castes=sub_castes)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form['full_name']
        gender = request.form['gender']
        birth_date = request.form['birth_date']
        office_id = request.form['office_id']
        designation_id = request.form['designation_id']
        class_id = request.form['class_id']
        salary_category_id = request.form['salary_category_id']
        joining_date = request.form['joining_date']
        joining_designation_id = request.form['joining_designation_id']
        caste_id = request.form['caste_id']
        sub_caste_id = request.form.get('sub_caste_id', None)
        caste_verified = 'caste_verified' in request.form
        caste_verification_date = request.form.get('caste_verification_date', None)
        bindu_number = request.form['bindu_number']
        department_exam_passed = 'department_exam_passed' in request.form
        department_exam_year = request.form.get('department_exam_year', None)
        pranidhi_id = request.form['pranidhi_id']
        bank_name = request.form['bank_name']
        ifsc_code = request.form['ifsc_code']
        account_number = request.form['account_number']
        aadhar_number = request.form['aadhar_number']
        gpf_number = request.form['gpf_number']
        
        # Transfer history fields (first row)
        previous_office_release_date = request.form.get('previous_office_release_date', None)
        previous_district = request.form.get('previous_district', '')
        previous_designation = request.form.get('previous_designation', '')
        current_joining_date = request.form.get('current_joining_date', None)
        
        # Calculate retirement date based on birth date and class
        # For classes 1-4: 58 years from birth date
        # For class 4: 60 years from birth date
        retirement_date = None
        if birth_date:
            birth_datetime = datetime.strptime(birth_date, '%Y-%m-%d')
            if class_id in ['1', '2', '3']:  # Classes 1-3
                retirement_date = birth_datetime.replace(year=birth_datetime.year + 58).strftime('%Y-%m-%d')
            elif class_id == '4':  # Class 4
                retirement_date = birth_datetime.replace(year=birth_datetime.year + 60).strftime('%Y-%m-%d')
        
        # Insert employee data
        c.execute('''INSERT INTO employees (
            full_name, gender, birth_date, office_id, designation_id, class_id, 
            salary_category_id, joining_date, joining_designation_id, caste_id, 
            sub_caste_id, caste_verified, caste_verification_date, bindu_number, 
            department_exam_passed, department_exam_year, pranidhi_id, bank_name, 
            ifsc_code, account_number, aadhar_number, gpf_number, retirement_date,
            previous_office_release_date, previous_district, 
            previous_designation, current_joining_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (full_name, gender, birth_date, office_id, designation_id, class_id, 
         salary_category_id, joining_date, joining_designation_id, caste_id, 
         sub_caste_id, caste_verified, caste_verification_date, bindu_number, 
         department_exam_passed, department_exam_year, pranidhi_id, bank_name, 
         ifsc_code, account_number, aadhar_number, gpf_number, retirement_date,
         previous_office_release_date, previous_district, 
         previous_designation, current_joining_date))
        
        employee_id = c.lastrowid
        conn.commit()
        
        # Insert transfer history records
        # First row (main fields)
        if previous_district or previous_designation:
            c.execute('''INSERT INTO transfer_history 
                        (employee_id, previous_office_release_date, 
                         previous_district, previous_designation, current_joining_date)
                        VALUES (?, ?, ?, ?, ?)''',
                      (employee_id, previous_office_release_date,
                       previous_district, previous_designation, current_joining_date))
            conn.commit()
        
        # Additional transfer rows
        transfer_release_dates = request.form.getlist('transfer_release_date[]')
        transfer_districts = request.form.getlist('transfer_district[]')
        transfer_designations = request.form.getlist('transfer_designation[]')
        transfer_joining_dates = request.form.getlist('transfer_joining_date[]')
        
        for i in range(len(transfer_release_dates)):
            release_date = transfer_release_dates[i] if i < len(transfer_release_dates) else None
            district = transfer_districts[i] if i < len(transfer_districts) else ''
            designation = transfer_designations[i] if i < len(transfer_designations) else ''
            joining_date = transfer_joining_dates[i] if i < len(transfer_joining_dates) else None
            
            if district or designation:
                c.execute('''INSERT INTO transfer_history 
                            (employee_id, previous_office_release_date, 
                             previous_district, previous_designation, current_joining_date)
                            VALUES (?, ?, ?, ?, ?)''',
                          (employee_id, release_date, district, designation, joining_date))
                conn.commit()
        
        # Insert promotion history if provided
        # For new employees, we'll add the initial joining as the first promotion
        c.execute('''INSERT INTO promotion_history 
                    (employee_id, designation, joining_date, promotion_date)
                    VALUES (?, ?, ?, ?)''',
                  (employee_id, joining_designation_id, joining_date, joining_date))
        conn.commit()
        
        # Add additional promotion history records
        promotion_designation_ids = request.form.getlist('promotion_designation_id[]')
        promotion_joining_dates = request.form.getlist('promotion_joining_date[]')
        promotion_dates = request.form.getlist('promotion_date[]')
        promotion_designation_names = request.form.getlist('promotion_designation_name[]')
        
        for i in range(len(promotion_designation_ids)):
            designation_id = promotion_designation_ids[i] if i < len(promotion_designation_ids) else None
            joining_date = promotion_joining_dates[i] if i < len(promotion_joining_dates) else None
            promotion_date = promotion_dates[i] if i < len(promotion_dates) else None
            designation_name = promotion_designation_names[i] if i < len(promotion_designation_names) else ''
            
            if designation_id and promotion_date:
                c.execute('''INSERT INTO promotion_history 
                            (employee_id, designation, joining_date, promotion_date, designation_name)
                            VALUES (?, ?, ?, ?, ?)''',
                          (employee_id, designation_id, joining_date, promotion_date, designation_name))
                conn.commit()
        
        conn.close()
        
        # Update office position counts
        update_office_position_counts(office_id, designation_id)
        
        flash('कर्मचारी यशस्वीरित्या जोडला गेला!')
        return redirect(url_for('employees'))
    
    # Get dropdown data
    c.execute("SELECT id, office_name FROM offices")
    offices = c.fetchall()
    
    c.execute("SELECT id, designation_name FROM designations")
    designations = c.fetchall()
    
    c.execute("SELECT id, class_name FROM classes")
    classes = c.fetchall()
    
    c.execute("SELECT id, category_name FROM salary_categories")
    salary_categories = c.fetchall()
    
    c.execute("SELECT id, caste_name FROM castes")
    castes = c.fetchall()
    
    c.execute("SELECT id, sub_caste_name FROM sub_castes")
    sub_castes = c.fetchall()
    
    conn.close()
    
    return render_template('add_employee.html', 
                          offices=offices,
                          designations=designations,
                          classes=classes,
                          salary_categories=salary_categories,
                          castes=castes,
                          sub_castes=sub_castes)

@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM offices")
    offices = c.fetchall()
    
    c.execute("SELECT * FROM designations")
    designations = c.fetchall()
    
    c.execute("SELECT * FROM classes")
    classes = c.fetchall()
    
    c.execute("SELECT * FROM salary_categories")
    salary_categories = c.fetchall()
    
    c.execute("SELECT * FROM castes")
    castes = c.fetchall()
    
    c.execute("SELECT s.*, c.caste_name FROM sub_castes s JOIN castes c ON s.caste_id = c.id")
    sub_castes = c.fetchall()
    
    conn.close()
    
    return render_template('settings.html',
                          offices=offices,
                          designations=designations,
                          classes=classes,
                          salary_categories=salary_categories,
                          castes=castes,
                          sub_castes=sub_castes)

# API routes for settings management
@app.route('/api/offices', methods=['POST'])
def add_office():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    office_name = data.get('name')
    
    if not office_name:
        return jsonify({'error': 'Office name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO offices (office_name) VALUES (?)", (office_name,))
        conn.commit()
        office_id = c.lastrowid
        conn.close()
        return jsonify({'id': office_id, 'name': office_name}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Office already exists'}), 400

@app.route('/api/offices/<int:office_id>', methods=['PUT'])
def update_office(office_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    office_name = data.get('name')
    
    if not office_name:
        return jsonify({'error': 'Office name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("UPDATE offices SET office_name = ? WHERE id = ?", (office_name, office_id))
        conn.commit()
        rows_affected = c.rowcount
        conn.close()
        
        if rows_affected == 0:
            return jsonify({'error': 'Office not found'}), 404
        
        return jsonify({'id': office_id, 'name': office_name}), 200
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Office name already exists'}), 400

@app.route('/api/offices/<int:office_id>', methods=['DELETE'])
def delete_office(office_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Check if office is being used
    c.execute("SELECT COUNT(*) FROM employees WHERE office_id = ?", (office_id,))
    employee_count = c.fetchone()[0]
    
    if employee_count > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete office. It is assigned to employees.'}), 400
    
    c.execute("DELETE FROM offices WHERE id = ?", (office_id,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Office not found'}), 404
    
    return jsonify({'message': 'Office deleted successfully'}), 200

# API routes for designations
@app.route('/api/designations', methods=['POST'])
def add_designation():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    designation_name = data.get('name')
    
    if not designation_name:
        return jsonify({'error': 'Designation name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO designations (designation_name) VALUES (?)", (designation_name,))
        conn.commit()
        designation_id = c.lastrowid
        conn.close()
        return jsonify({'id': designation_id, 'name': designation_name}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Designation already exists'}), 400

@app.route('/api/designations/<int:designation_id>', methods=['PUT'])
def update_designation(designation_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    designation_name = data.get('name')
    
    if not designation_name:
        return jsonify({'error': 'Designation name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("UPDATE designations SET designation_name = ? WHERE id = ?", (designation_name, designation_id))
        conn.commit()
        rows_affected = c.rowcount
        conn.close()
        
        if rows_affected == 0:
            return jsonify({'error': 'Designation not found'}), 404
        
        return jsonify({'id': designation_id, 'name': designation_name}), 200
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Designation name already exists'}), 400

@app.route('/api/designations/<int:designation_id>', methods=['DELETE'])
def delete_designation(designation_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Check if designation is being used
    c.execute("SELECT COUNT(*) FROM employees WHERE designation_id = ? OR joining_designation_id = ?", (designation_id, designation_id))
    employee_count = c.fetchone()[0]
    
    if employee_count > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete designation. It is assigned to employees.'}), 400
    
    c.execute("DELETE FROM designations WHERE id = ?", (designation_id,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Designation not found'}), 404
    
    return jsonify({'message': 'Designation deleted successfully'}), 200

# API routes for classes
@app.route('/api/classes', methods=['POST'])
def add_class():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    class_name = data.get('name')
    
    if not class_name:
        return jsonify({'error': 'Class name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO classes (class_name) VALUES (?)", (class_name,))
        conn.commit()
        class_id = c.lastrowid
        conn.close()
        return jsonify({'id': class_id, 'name': class_name}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Class already exists'}), 400

@app.route('/api/classes/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    class_name = data.get('name')
    
    if not class_name:
        return jsonify({'error': 'Class name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("UPDATE classes SET class_name = ? WHERE id = ?", (class_name, class_id))
        conn.commit()
        rows_affected = c.rowcount
        conn.close()
        
        if rows_affected == 0:
            return jsonify({'error': 'Class not found'}), 404
        
        return jsonify({'id': class_id, 'name': class_name}), 200
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Class name already exists'}), 400

@app.route('/api/classes/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Check if class is being used
    c.execute("SELECT COUNT(*) FROM employees WHERE class_id = ?", (class_id,))
    employee_count = c.fetchone()[0]
    
    if employee_count > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete class. It is assigned to employees.'}), 400
    
    c.execute("DELETE FROM classes WHERE id = ?", (class_id,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Class not found'}), 404
    
    return jsonify({'message': 'Class deleted successfully'}), 200

# API routes for salary categories
@app.route('/api/salary_categories', methods=['POST'])
def add_salary_category():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    category_name = data.get('name')
    
    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO salary_categories (category_name) VALUES (?)", (category_name,))
        conn.commit()
        category_id = c.lastrowid
        conn.close()
        return jsonify({'id': category_id, 'name': category_name}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Salary category already exists'}), 400

@app.route('/api/salary_categories/<int:category_id>', methods=['PUT'])
def update_salary_category(category_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    category_name = data.get('name')
    
    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("UPDATE salary_categories SET category_name = ? WHERE id = ?", (category_name, category_id))
        conn.commit()
        rows_affected = c.rowcount
        conn.close()
        
        if rows_affected == 0:
            return jsonify({'error': 'Salary category not found'}), 404
        
        return jsonify({'id': category_id, 'name': category_name}), 200
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Salary category name already exists'}), 400

@app.route('/api/salary_categories/<int:category_id>', methods=['DELETE'])
def delete_salary_category(category_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Check if salary category is being used
    c.execute("SELECT COUNT(*) FROM employees WHERE salary_category_id = ?", (category_id,))
    employee_count = c.fetchone()[0]
    
    if employee_count > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete salary category. It is assigned to employees.'}), 400
    
    c.execute("DELETE FROM salary_categories WHERE id = ?", (category_id,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Salary category not found'}), 404
    
    return jsonify({'message': 'Salary category deleted successfully'}), 200

# API routes for castes
@app.route('/api/castes', methods=['POST'])
def add_caste():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    caste_name = data.get('name')
    
    if not caste_name:
        return jsonify({'error': 'Caste name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO castes (caste_name) VALUES (?)", (caste_name,))
        conn.commit()
        caste_id = c.lastrowid
        conn.close()
        return jsonify({'id': caste_id, 'name': caste_name}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Caste already exists'}), 400

@app.route('/api/castes/<int:caste_id>', methods=['PUT'])
def update_caste(caste_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    caste_name = data.get('name')
    
    if not caste_name:
        return jsonify({'error': 'Caste name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("UPDATE castes SET caste_name = ? WHERE id = ?", (caste_name, caste_id))
        conn.commit()
        rows_affected = c.rowcount
        conn.close()
        
        if rows_affected == 0:
            return jsonify({'error': 'Caste not found'}), 404
        
        return jsonify({'id': caste_id, 'name': caste_name}), 200
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Caste name already exists'}), 400

@app.route('/api/castes/<int:caste_id>', methods=['DELETE'])
def delete_caste(caste_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Check if caste is being used
    c.execute("SELECT COUNT(*) FROM employees WHERE caste_id = ?", (caste_id,))
    employee_count = c.fetchone()[0]
    
    if employee_count > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete caste. It is assigned to employees.'}), 400
    
    # Also delete sub castes
    c.execute("DELETE FROM sub_castes WHERE caste_id = ?", (caste_id,))
    c.execute("DELETE FROM castes WHERE id = ?", (caste_id,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Caste not found'}), 404
    
    return jsonify({'message': 'Caste deleted successfully'}), 200

# API routes for sub-castes
@app.route('/api/sub_castes', methods=['POST'])
def add_sub_caste():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    caste_id = data.get('caste_id')
    sub_caste_name = data.get('name')
    
    if not caste_id or not sub_caste_name:
        return jsonify({'error': 'Caste ID and sub caste name are required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO sub_castes (caste_id, sub_caste_name) VALUES (?, ?)", (caste_id, sub_caste_name))
        conn.commit()
        sub_caste_id = c.lastrowid
        conn.close()
        return jsonify({'id': sub_caste_id, 'caste_id': caste_id, 'name': sub_caste_name}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Sub caste already exists for this caste'}), 400

@app.route('/api/sub_castes/<int:sub_caste_id>', methods=['PUT'])
def update_sub_caste(sub_caste_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    sub_caste_name = data.get('name')
    
    if not sub_caste_name:
        return jsonify({'error': 'Sub caste name is required'}), 400
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    try:
        c.execute("UPDATE sub_castes SET sub_caste_name = ? WHERE id = ?", (sub_caste_name, sub_caste_id))
        conn.commit()
        rows_affected = c.rowcount
        conn.close()
        
        if rows_affected == 0:
            return jsonify({'error': 'Sub caste not found'}), 404
        
        return jsonify({'id': sub_caste_id, 'name': sub_caste_name}), 200
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Sub caste name already exists'}), 400

@app.route('/api/sub_castes/<int:sub_caste_id>', methods=['DELETE'])
def delete_sub_caste(sub_caste_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Check if sub caste is being used
    c.execute("SELECT COUNT(*) FROM employees WHERE sub_caste_id = ?", (sub_caste_id,))
    employee_count = c.fetchone()[0]
    
    if employee_count > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete sub caste. It is assigned to employees.'}), 400
    
    c.execute("DELETE FROM sub_castes WHERE id = ?", (sub_caste_id,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Sub caste not found'}), 404
    
    return jsonify({'message': 'Sub caste deleted successfully'}), 200

@app.route('/office_positions')
def office_positions():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get all offices and positions with counts
    c.execute('''SELECT op.*, o.office_name, d.designation_name,
                 COALESCE(op.approved_count, 0) as approved_count,
                 COALESCE(op.filled_count, 0) as filled_count,
                 COALESCE(op.vacant_count, 0) as vacant_count
                 FROM office_positions op
                 JOIN offices o ON op.office_id = o.id
                 JOIN designations d ON op.designation_id = d.id''')
    
    positions = c.fetchall()
    
    # Get offices and designations for dropdowns
    c.execute("SELECT id, office_name FROM offices")
    offices = c.fetchall()
    
    c.execute("SELECT id, designation_name FROM designations")
    designations = c.fetchall()
    
    # Get office-wise totals
    c.execute('''SELECT o.office_name,
                 COALESCE(SUM(op.approved_count), 0) as total_approved,
                 COALESCE(SUM(op.filled_count), 0) as total_filled,
                 COALESCE(SUM(op.vacant_count), 0) as total_vacant
                 FROM offices o
                 LEFT JOIN office_positions op ON o.id = op.office_id
                 GROUP BY o.id, o.office_name''')
    
    office_totals = c.fetchall()
    
    # Get designation-wise totals
    c.execute('''SELECT d.designation_name,
                 COALESCE(SUM(op.approved_count), 0) as total_approved,
                 COALESCE(SUM(op.filled_count), 0) as total_filled,
                 COALESCE(SUM(op.vacant_count), 0) as total_vacant
                 FROM designations d
                 LEFT JOIN office_positions op ON d.id = op.designation_id
                 GROUP BY d.id, d.designation_name''')
    
    designation_totals = c.fetchall()
    
    # Get overall totals
    c.execute('''SELECT 
                 COALESCE(SUM(op.approved_count), 0) as overall_approved,
                 COALESCE(SUM(op.filled_count), 0) as overall_filled,
                 COALESCE(SUM(op.vacant_count), 0) as overall_vacant
                 FROM office_positions op''')
    
    overall_totals = c.fetchone()
    
    conn.close()
    
    return render_template('office_positions.html', 
                          positions=positions,
                          offices=offices,
                          designations=designations,
                          office_totals=office_totals,
                          designation_totals=designation_totals,
                          overall_totals=overall_totals)

# Function to update office position counts
def update_office_position_counts(office_id, designation_id):
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Count filled positions (employees with this office and designation)
    c.execute("""SELECT COUNT(*) FROM employees 
                 WHERE office_id = ? AND designation_id = ?""", 
              (office_id, designation_id))
    filled_count = c.fetchone()[0]
    
    # Check if office position exists
    c.execute("SELECT id, approved_count FROM office_positions WHERE office_id = ? AND designation_id = ?", 
              (office_id, designation_id))
    position = c.fetchone()
    
    if position:
        # Update existing position
        vacant_count = position[1] - filled_count  # approved_count - filled_count
        c.execute('''UPDATE office_positions 
                     SET filled_count = ?, vacant_count = ?
                     WHERE id = ?''', 
                  (filled_count, vacant_count, position[0]))
        conn.commit()
    
    conn.close()

@app.route('/add_office_position', methods=['POST'])
def add_office_position():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    office_id = request.form['office_id']
    designation_id = request.form['designation_id']
    approved_count = request.form['approved_count']
    
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    
    # Check if position already exists
    c.execute("SELECT id FROM office_positions WHERE office_id = ? AND designation_id = ?", 
              (office_id, designation_id))
    
    existing = c.fetchone()
    
    # Count filled positions (employees with this office and designation)
    c.execute("""SELECT COUNT(*) FROM employees 
                 WHERE office_id = ? AND designation_id = ?""", 
              (office_id, designation_id))
    filled_count = c.fetchone()[0]
    
    # Calculate vacant count
    vacant_count = int(approved_count) - filled_count
    
    if existing:
        # Update existing
        c.execute('''UPDATE office_positions 
                     SET approved_count = ?, filled_count = ?, vacant_count = ?
                     WHERE id = ?''', 
                  (approved_count, filled_count, vacant_count, existing[0]))
    else:
        # Insert new
        c.execute('''INSERT INTO office_positions (office_id, designation_id, approved_count, filled_count, vacant_count)
                     VALUES (?, ?, ?, ?, ?)''', 
                  (office_id, designation_id, approved_count, filled_count, vacant_count))
    
    conn.commit()
    conn.close()
    
    flash('कार्यालय पद यशस्वीरित्या अद्यतनित केले गेले!')
    return redirect(url_for('office_positions'))

@app.route('/office_profile', methods=['GET', 'POST'])
def office_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'POST':
        # Get form data
        office_name = request.form['office_name']
        office_address = request.form['office_address']
        email = request.form['email']
        phone = request.form['phone']
        officer_name = request.form['officer_name']
        designation = request.form['designation']
        district_name = request.form['district_name']
        senior_clerk_names = request.form['senior_clerk_names']
        junior_clerk_names = request.form['junior_clerk_names']
        
        # Update office profile (assuming only one office profile for now)
        c.execute("""UPDATE office_profile 
                     SET office_name = ?, office_address = ?, email = ?, phone = ?, 
                         officer_name = ?, designation = ?, district_name = ?, 
                         senior_clerk_names = ?, junior_clerk_names = ?
                     WHERE id = 1""", 
                  (office_name, office_address, email, phone, officer_name, 
                   designation, district_name, senior_clerk_names, junior_clerk_names))
        
        conn.commit()
        conn.close()
        
        flash('कार्यालय प्रोफाइल यशस्वीरित्या अद्यतनित केले गेले!')
        return redirect(url_for('office_profile'))
    
    # Get office profile data
    c.execute("SELECT * FROM office_profile WHERE id = 1")
    office_profile = c.fetchone()
    
    conn.close()
    
    return render_template('office_profile.html', office_profile=office_profile)

@app.route('/get_sub_castes/<int:caste_id>')
def get_sub_castes(caste_id):
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT id, sub_caste_name FROM sub_castes WHERE caste_id = ?", (caste_id,))
    sub_castes = c.fetchall()
    
    conn.close()
    
    # Return as JSON-like structure for JavaScript
    result = []
    for sub_caste in sub_castes:
        result.append({
            'id': sub_caste['id'],
            'name': sub_caste['sub_caste_name']
        })
    
    return {'sub_castes': result}

if __name__ == '__main__':
    init_db()
    app.run(debug=True)