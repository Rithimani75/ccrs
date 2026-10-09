from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

import os
import random
import string

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


app = Flask(__name__)

# =========================================================
# FLASK CONFIGURATION
# =========================================================

app.secret_key = 'ccrs_secret_key_2026'


# =========================================================
# MYSQL CONFIGURATION
# =========================================================

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ccrs'

mysql = MySQL(app)


# =========================================================
# EMAIL CONFIGURATION
# =========================================================
# IMPORTANT:
# Replace these two values with your Gmail address and
# Gmail APP PASSWORD. Do not use your normal Gmail password.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'rithikamani05@gmail.com'
app.config['MAIL_PASSWORD'] = 'kyee avqh qwpm gxpo'
app.config['MAIL_DEFAULT_SENDER'] = 'rithikamani05@gmail.com'

mail = Mail(app)


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    'static',
    'uploads'
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg',
    'gif'
}

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def allowed_file(filename):

    return (
        '.' in filename
        and
        filename.rsplit('.', 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def send_status_email(student_email, student_name, complaint_id,
                      status, remarks=''):

    if not student_email:
        print('EMAIL ERROR: Student email is empty.')
        return False

    try:
        if status == 'Resolved':
            subject = f'CCRS Complaint Resolved - {complaint_id}'
            message = f'''Hello {student_name},

Your complaint has been RESOLVED.

Complaint ID: {complaint_id}
Status: Resolved
Remarks: {remarks if remarks else 'Your complaint has been resolved successfully.'}

You can login to the Campus Complaint Registry System
to view the complete complaint history.

Regards,
Campus Complaint Registry System
'''
        else:
            subject = f'CCRS Complaint Status Updated - {complaint_id}'
            message = f'''Hello {student_name},

Your complaint status has been updated.

Complaint ID: {complaint_id}
New Status: {status}
Remarks: {remarks if remarks else 'No remarks'}

You can login to the Campus Complaint Registry System
to view the complete complaint history.

Regards,
Campus Complaint Registry System
'''

        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[student_email]
        )

        msg.body = message
        mail.send(msg)

        print('EMAIL SENT SUCCESSFULLY TO:', student_email)
        return True

    except Exception as e:
        # Email failure should NOT break the complaint update.
        print('EMAIL ERROR:', e)
        return False


def generate_complaint_id():

    while True:

        code = 'CCR' + ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=9
            )
        )

        cur = mysql.connection.cursor()

        cur.execute(
            """
            SELECT id
            FROM complaints
            WHERE complaint_id = %s
            """,
            (code,)
        )

        existing = cur.fetchone()

        cur.close()

        if not existing:
            return code


# =========================================================
# HOME
# =========================================================

@app.route('/')
def index():

    return redirect('/login')


# =========================================================
# REGISTER
# =========================================================

@app.route(
    '/register',
    methods=['GET', 'POST']
)
def register():

    if request.method == 'POST':

        name = request.form.get(
            'name',
            ''
        ).strip()

        register_number = request.form.get(
            'register_number',
            ''
        ).strip()

        email = request.form.get(
            'email',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        if (
            not name
            or not register_number
            or not email
            or not password
        ):

            flash(
                'Please fill all fields.'
            )

            return redirect(
                '/register'
            )

        hashed_password = generate_password_hash(
            password
        )

        cur = mysql.connection.cursor()

        try:

            cur.execute(
                """
                INSERT INTO users
                (
                    name,
                    register_number,
                    email,
                    password,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'student'
                )
                """,
                (
                    name,
                    register_number,
                    email,
                    hashed_password
                )
            )

            mysql.connection.commit()

            flash(
                'Registration successful. Please login.'
            )

            return redirect(
                '/login'
            )

        except Exception as e:

            mysql.connection.rollback()

            if 'Duplicate entry' in str(e):

                flash(
                    'Email already registered.'
                )

            else:

                flash(
                    'Registration failed.'
                )

            return redirect(
                '/register'
            )

        finally:

            cur.close()

    return render_template(
        'register.html'
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    '/login',
    methods=['GET', 'POST']
)
def login():

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        cur = mysql.connection.cursor()

        cur.execute(
            """
            SELECT
                id,
                name,
                email,
                password,
                role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cur.fetchone()

        cur.close()

        if (
            user
            and
            check_password_hash(
                user[3],
                password
            )
        ):

            session.clear()

            session['user_id'] = user[0]
            session['name'] = user[1]
            session['email'] = user[2]
            session['role'] = user[4]

            if user[4] == 'admin':

                return redirect(
                    '/admin_dashboard'
                )

            elif user[4] == 'staff':

                return redirect(
                    '/staff_dashboard'
                )

            else:

                return redirect(
                    '/student_dashboard'
                )

        flash(
            'Invalid email or password.'
        )

        return redirect(
            '/login'
        )

    return render_template(
        'login.html'
    )


# =========================================================
# TEST EMAIL
# =========================================================

@app.route('/test_email')
def test_email():

    if 'user_id' not in session:
        return redirect('/login')

    # Send the test email to the currently logged-in user's email.
    recipient = session.get('email')

    if not recipient:
        return 'No email address found for the logged-in user.', 400

    try:
        msg = Message(
            subject='CCRS Email Test',
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient]
        )

        msg.body = '''Hello,

This is a test email from the
Campus Complaint Registry System.

Email notification is working successfully.

Regards,
CCRS Admin
'''

        mail.send(msg)

        return f'Test email sent successfully to {recipient}!'

    except Exception as e:
        print('TEST EMAIL ERROR:', e)
        return f'Unable to send email. Check your Gmail configuration. Error: {e}', 500


# =========================================================
# LOGOUT
# =========================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect(
        '/login'
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route('/student_dashboard')
def student_dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'student':
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT
            id,
            complaint_id,
            category,
            description,
            status,
            created_at
        FROM complaints
        WHERE student_id = %s
        ORDER BY created_at DESC
        """,
        (
            session['user_id'],
        )
    )

    complaints = cur.fetchall()

    cur.close()

    return render_template(
        'student_dashboard.html',
        complaints=complaints
    )


# =========================================================
# SUBMIT COMPLAINT
# =========================================================

@app.route(
    '/submit_complaint',
    methods=['GET', 'POST']
)
def submit_complaint():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'student':
        return redirect('/login')

    if request.method == 'POST':

        category = request.form.get(
            'category',
            ''
        ).strip()

        description = request.form.get(
            'description',
            ''
        ).strip()

        if not category or not description:

            flash(
                'Please enter category and description.'
            )

            return redirect(
                '/submit_complaint'
            )

        image_filename = None

        if 'image' in request.files:

            file = request.files['image']

            if file and file.filename:

                if allowed_file(
                    file.filename
                ):

                    filename = secure_filename(
                        file.filename
                    )

                    image_filename = filename

                    file.save(
                        os.path.join(
                            app.config['UPLOAD_FOLDER'],
                            filename
                        )
                    )

                else:

                    flash(
                        'Invalid image format.'
                    )

                    return redirect(
                        '/submit_complaint'
                    )

        complaint_id = generate_complaint_id()

        cur = mysql.connection.cursor()

        try:

            cur.execute(
                """
                INSERT INTO complaints
                (
                    complaint_id,
                    student_id,
                    category,
                    description,
                    image,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'Submitted'
                )
                """,
                (
                    complaint_id,
                    session['user_id'],
                    category,
                    description,
                    image_filename
                )
            )

            complaint_db_id = cur.lastrowid

            cur.execute(
                """
                INSERT INTO complaint_updates
                (
                    complaint_id,
                    status,
                    remarks,
                    updated_by
                )
                VALUES
                (
                    %s,
                    'Submitted',
                    'Complaint submitted by student',
                    %s
                )
                """,
                (
                    complaint_db_id,
                    session['user_id']
                )
            )

            mysql.connection.commit()

            flash(
                'Complaint submitted successfully. Complaint ID: '
                + complaint_id
            )

            return redirect(
                '/my_complaints'
            )

        except Exception as e:

            mysql.connection.rollback()

            print(
                'SUBMIT COMPLAINT ERROR:',
                e
            )

            flash(
                'Unable to submit complaint.'
            )

            return redirect(
                '/submit_complaint'
            )

        finally:

            cur.close()

    return render_template(
        'submit_complaint.html'
    )


# =========================================================
# MY COMPLAINTS
# =========================================================

@app.route('/my_complaints')
def my_complaints():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'student':
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT
            id,
            complaint_id,
            category,
            description,
            image,
            status,
            created_at
        FROM complaints
        WHERE student_id = %s
        ORDER BY created_at DESC
        """,
        (
            session['user_id'],
        )
    )

    complaints = cur.fetchall()

    cur.close()

    return render_template(
        'my_complaints.html',
        complaints=complaints
    )


# =========================================================
# COMPLAINT DETAILS
# =========================================================

@app.route(
    '/complaint/<int:complaint_id>'
)
def complaint_details(
    complaint_id
):

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT
            c.id,
            c.complaint_id,
            c.student_id,
            u.name,
            c.category,
            c.description,
            c.image,
            c.status,
            c.assigned_to,
            c.created_at,
            c.resolved_at
        FROM complaints c
        JOIN users u
            ON c.student_id = u.id
        WHERE c.id = %s
        """,
        (
            complaint_id,
        )
    )

    complaint = cur.fetchone()

    cur.close()

    if not complaint:

        return (
            'Complaint not found',
            404
        )

    return render_template(
        'complaint_details.html',
        complaint=complaint
    )


# =========================================================
# COMPLAINT HISTORY
# =========================================================

@app.route(
    '/complaint_history/<int:complaint_id>'
)
def complaint_history(
    complaint_id
):

    if 'user_id' not in session:

        return redirect(
            '/login'
        )

    cur = mysql.connection.cursor()

    # -----------------------------------------------------
    # GET COMPLAINT INFORMATION
    # -----------------------------------------------------

    cur.execute(
        """
        SELECT
            id,
            complaint_id,
            student_id,
            status,
            assigned_to
        FROM complaints
        WHERE id = %s
        """,
        (
            complaint_id,
        )
    )

    complaint = cur.fetchone()

    if not complaint:

        cur.close()

        return (
            'Complaint not found',
            404
        )

    # -----------------------------------------------------
    # ACCESS CONTROL
    # -----------------------------------------------------

    role = session.get(
        'role'
    )

    if role == 'student':

        if complaint[2] != session['user_id']:

            cur.close()

            return (
                'Access denied',
                403
            )

    elif role == 'staff':

        if complaint[4] != session['user_id']:

            cur.close()

            return (
                'Access denied',
                403
            )

    elif role != 'admin':

        cur.close()

        return (
            'Access denied',
            403
        )

    # -----------------------------------------------------
    # GET HISTORY
    # -----------------------------------------------------

    cur.execute(
        """
        SELECT
            cu.status,
            cu.remarks,
            u.name,
            u.role,
            cu.updated_at
        FROM complaint_updates cu
        LEFT JOIN users u
            ON cu.updated_by = u.id
        WHERE cu.complaint_id = %s
        ORDER BY cu.updated_at DESC
        """,
        (
            complaint_id,
        )
    )

    history = cur.fetchall()

    cur.close()

    # -----------------------------------------------------
    # VERY IMPORTANT:
    # complaint AND history ARE BOTH PASSED TO TEMPLATE
    # -----------------------------------------------------

    return render_template(
        'complaint_history.html',
        complaint=complaint,
        history=history
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return redirect('/login')

    search = request.args.get(
        'search',
        ''
    ).strip()

    status_filter = request.args.get(
        'status',
        ''
    ).strip()

    category_filter = request.args.get(
        'category',
        ''
    ).strip()

    cur = mysql.connection.cursor()

    # -----------------------------------------------------
    # COMPLAINT QUERY
    # -----------------------------------------------------

    query = """
        SELECT
            c.id,
            c.complaint_id,
            u.name,
            u.email,
            c.category,
            c.description,
            c.status,
            c.assigned_to,
            c.created_at
        FROM complaints c
        JOIN users u
            ON c.student_id = u.id
        WHERE 1=1
    """

    params = []

    if search:

        query += """
            AND (
                c.complaint_id LIKE %s
                OR u.name LIKE %s
                OR u.email LIKE %s
                OR c.description LIKE %s
            )
        """

        search_value = '%' + search + '%'

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    if status_filter:

        query += """
            AND c.status = %s
        """

        params.append(
            status_filter
        )

    if category_filter:

        query += """
            AND c.category = %s
        """

        params.append(
            category_filter
        )

    query += """
        ORDER BY c.created_at DESC
    """

    cur.execute(
        query,
        tuple(params)
    )

    complaints = cur.fetchall()

    # -----------------------------------------------------
    # STAFF
    # -----------------------------------------------------

    cur.execute(
        """
        SELECT
            id,
            name,
            email
        FROM users
        WHERE role = 'staff'
        ORDER BY name
        """
    )

    staff = cur.fetchall()

    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    cur.execute(
        """
        SELECT DISTINCT category
        FROM complaints
        ORDER BY category
        """
    )

    categories = cur.fetchall()

    cur.close()

    return render_template(
        'admin_dashboard.html',
        complaints=complaints,
        staff=staff,
        categories=categories,
        search=search,
        status_filter=status_filter,
        category_filter=category_filter
    )


# =========================================================
# ASSIGN COMPLAINT
# =========================================================

@app.route(
    '/assign_complaint/<int:complaint_id>',
    methods=['POST']
)
def assign_complaint(
    complaint_id
):

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return redirect('/login')

    staff_id = request.form.get(
        'staff_id'
    )

    if not staff_id:

        flash(
            'Please select a staff member.'
        )

        return redirect(
            '/admin_dashboard'
        )

    cur = mysql.connection.cursor()

    try:

        # Verify staff
        cur.execute(
            """
            SELECT id
            FROM users
            WHERE id = %s
              AND role = 'staff'
            """,
            (
                staff_id,
            )
        )

        staff_member = cur.fetchone()

        if not staff_member:

            flash(
                'Invalid staff member.'
            )

            cur.close()

            return redirect(
                '/admin_dashboard'
            )

        # Assign
        cur.execute(
            """
            UPDATE complaints
            SET
                assigned_to = %s,
                status = 'Assigned'
            WHERE id = %s
            """,
            (
                staff_id,
                complaint_id
            )
        )

        # History
        cur.execute(
            """
            INSERT INTO complaint_updates
            (
                complaint_id,
                status,
                remarks,
                updated_by
            )
            VALUES
            (
                %s,
                'Assigned',
                'Complaint assigned to staff',
                %s
            )
            """,
            (
                complaint_id,
                session['user_id']
            )
        )

        mysql.connection.commit()

        flash(
            'Complaint assigned successfully.'
        )

    except Exception as e:

        mysql.connection.rollback()

        print(
            'ASSIGNMENT ERROR:',
            e
        )

        flash(
            'Unable to assign complaint.'
        )

    finally:

        cur.close()

    return redirect(
        '/admin_dashboard'
    )


# =========================================================
# ADMIN UPDATE STATUS
# =========================================================

@app.route(
    '/admin_update_status/<int:complaint_id>',
    methods=['POST']
)
def admin_update_status(
    complaint_id
):

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return redirect('/login')

    status = request.form.get(
        'status'
    )

    remarks = request.form.get(
        'remarks',
        ''
    ).strip()

    allowed_statuses = [
        'Submitted',
        'Assigned',
        'In Progress',
        'Resolved'
    ]

    if status not in allowed_statuses:

        flash(
            'Invalid status.'
        )

        return redirect(
            '/admin_dashboard'
        )

    cur = mysql.connection.cursor()

    try:

        # Get student information for email notification
        cur.execute(
            '''
            SELECT
                c.complaint_id,
                u.name,
                u.email
            FROM complaints c
            JOIN users u
                ON c.student_id = u.id
            WHERE c.id = %s
            ''',
            (complaint_id,)
        )

        complaint_info = cur.fetchone()

        if not complaint_info:
            flash('Complaint not found.')
            return redirect('/admin_dashboard')

        email_complaint_id = complaint_info[0]
        student_name = complaint_info[1]
        student_email = complaint_info[2]

        if status == 'Resolved':

            cur.execute(
                """
                UPDATE complaints
                SET
                    status = %s,
                    resolved_at = NOW()
                WHERE id = %s
                """,
                (
                    status,
                    complaint_id
                )
            )

        else:

            cur.execute(
                """
                UPDATE complaints
                SET
                    status = %s,
                    resolved_at = NULL
                WHERE id = %s
                """,
                (
                    status,
                    complaint_id
                )
            )

        cur.execute(
            """
            INSERT INTO complaint_updates
            (
                complaint_id,
                status,
                remarks,
                updated_by
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                complaint_id,
                status,
                remarks if remarks else 'No remarks',
                session['user_id']
            )
        )

        mysql.connection.commit()

        # Send email after the database update succeeds.
        send_status_email(
            student_email,
            student_name,
            email_complaint_id,
            status,
            remarks if remarks else 'No remarks'
        )

        flash(
            'Complaint status updated.'
        )

    except Exception as e:

        mysql.connection.rollback()

        print(
            'ADMIN STATUS ERROR:',
            e
        )

        flash(
            'Unable to update complaint status.'
        )

    finally:

        cur.close()

    return redirect(
        '/admin_dashboard'
    )


# =========================================================
# STAFF DASHBOARD
# =========================================================

@app.route('/staff_dashboard')
def staff_dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'staff':
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT
            c.id,
            c.complaint_id,
            u.name,
            c.category,
            c.description,
            c.status,
            c.created_at,
            c.image
        FROM complaints c
        JOIN users u
            ON c.student_id = u.id
        WHERE c.assigned_to = %s
        ORDER BY c.created_at DESC
        """,
        (
            session['user_id'],
        )
    )

    complaints = cur.fetchall()

    cur.close()

    return render_template(
        'staff_dashboard.html',
        complaints=complaints
    )


# =========================================================
# STAFF UPDATE STATUS
# =========================================================

@app.route(
    '/staff_update_status/<int:complaint_id>',
    methods=['POST']
)
def staff_update_status(
    complaint_id
):

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'staff':
        return redirect('/login')

    status = request.form.get(
        'status'
    )

    remarks = request.form.get(
        'remarks',
        ''
    ).strip()

    allowed_statuses = [
        'Assigned',
        'In Progress',
        'Resolved'
    ]

    if status not in allowed_statuses:

        flash(
            'Invalid status.'
        )

        return redirect(
            '/staff_dashboard'
        )

    cur = mysql.connection.cursor()

    try:

        # Verify assignment
        cur.execute(
            """
            SELECT id
            FROM complaints
            WHERE id = %s
              AND assigned_to = %s
            """,
            (
                complaint_id,
                session['user_id']
            )
        )

        complaint = cur.fetchone()

        if not complaint:

            cur.close()

            flash(
                'This complaint is not assigned to you.'
            )

            return redirect(
                '/staff_dashboard'
            )

        # Get student information for email notification
        cur.execute(
            '''
            SELECT
                c.complaint_id,
                u.name,
                u.email
            FROM complaints c
            JOIN users u
                ON c.student_id = u.id
            WHERE c.id = %s
            ''',
            (complaint_id,)
        )

        complaint_info = cur.fetchone()

        if not complaint_info:
            flash('Complaint not found.')
            return redirect('/staff_dashboard')

        email_complaint_id = complaint_info[0]
        student_name = complaint_info[1]
        student_email = complaint_info[2]

        # Update complaint
        if status == 'Resolved':

            cur.execute(
                """
                UPDATE complaints
                SET
                    status = %s,
                    resolved_at = NOW()
                WHERE id = %s
                """,
                (
                    status,
                    complaint_id
                )
            )

        else:

            cur.execute(
                """
                UPDATE complaints
                SET
                    status = %s,
                    resolved_at = NULL
                WHERE id = %s
                """,
                (
                    status,
                    complaint_id
                )
            )

        # History
        cur.execute(
            """
            INSERT INTO complaint_updates
            (
                complaint_id,
                status,
                remarks,
                updated_by
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                complaint_id,
                status,
                remarks if remarks else 'No remarks',
                session['user_id']
            )
        )

        mysql.connection.commit()

        # Send email after the database update succeeds.
        send_status_email(
            student_email,
            student_name,
            email_complaint_id,
            status,
            remarks if remarks else 'No remarks'
        )

        flash(
            'Complaint status updated successfully.'
        )

    except Exception as e:

        mysql.connection.rollback()

        print(
            'STAFF STATUS ERROR:',
            e
        )

        flash(
            'Unable to update complaint.'
        )

    finally:

        cur.close()

    return redirect(
        '/staff_dashboard'
    )


# =========================================================
# ADMIN REPORTS
# =========================================================

@app.route('/admin_reports')
def admin_reports():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return redirect('/login')

    cur = mysql.connection.cursor()

    # Total
    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        """
    )

    total_complaints = cur.fetchone()[0]

    # Submitted
    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Submitted'
        """
    )

    submitted = cur.fetchone()[0]

    # Assigned
    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Assigned'
        """
    )

    assigned = cur.fetchone()[0]

    # In Progress
    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'In Progress'
        """
    )

    in_progress = cur.fetchone()[0]

    # Resolved
    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Resolved'
        """
    )

    resolved = cur.fetchone()[0]

    # Categories
    cur.execute(
        """
        SELECT
            category,
            COUNT(*) AS count
        FROM complaints
        GROUP BY category
        ORDER BY count DESC
        """
    )

    categories = cur.fetchall()

    cur.close()

    return render_template(
        'admin_reports.html',
        total_complaints=total_complaints,
        submitted=submitted,
        assigned=assigned,
        in_progress=in_progress,
        resolved=resolved,
        categories=categories
    )


# =========================================================
# DOWNLOAD PDF REPORT
# =========================================================

@app.route('/download_report')
def download_report():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return redirect('/login')

    report_path = os.path.join(
        app.root_path,
        'static',
        'ccrs_report.pdf'
    )

    cur = mysql.connection.cursor()

    # Summary
    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        """
    )

    total = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Submitted'
        """
    )

    submitted = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Assigned'
        """
    )

    assigned = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'In Progress'
        """
    )

    in_progress = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Resolved'
        """
    )

    resolved = cur.fetchone()[0]

    # Category counts
    cur.execute(
        """
        SELECT
            category,
            COUNT(*)
        FROM complaints
        GROUP BY category
        ORDER BY COUNT(*) DESC
        """
    )

    categories = cur.fetchall()

    cur.close()

    # Create PDF
    pdf = canvas.Canvas(
        report_path,
        pagesize=A4
    )

    width, height = A4

    y = height - 50

    pdf.setFont(
        'Helvetica-Bold',
        18
    )

    pdf.drawString(
        50,
        y,
        'Campus Complaint Registry System'
    )

    y -= 30

    pdf.setFont(
        'Helvetica-Bold',
        14
    )

    pdf.drawString(
        50,
        y,
        'Complaint Report'
    )

    y -= 35

    pdf.setFont(
        'Helvetica',
        11
    )

    pdf.drawString(
        50,
        y,
        f'Total Complaints: {total}'
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f'Submitted: {submitted}'
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f'Assigned: {assigned}'
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f'In Progress: {in_progress}'
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f'Resolved: {resolved}'
    )

    y -= 40

    pdf.setFont(
        'Helvetica-Bold',
        13
    )

    pdf.drawString(
        50,
        y,
        'Complaints by Category'
    )

    y -= 25

    pdf.setFont(
        'Helvetica',
        11
    )

    for category, count in categories:

        pdf.drawString(
            70,
            y,
            f'{category}: {count}'
        )

        y -= 20

        if y < 60:

            pdf.showPage()

            y = height - 50

            pdf.setFont(
                'Helvetica',
                11
            )

    pdf.save()

    return redirect(
        '/static/ccrs_report.pdf'
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == '__main__':

    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000
    )

