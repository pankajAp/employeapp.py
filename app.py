import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Employee model
class Employee(db.Model):
    emp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_address = db.Column(db.String(255), nullable=False)
    emp_fullname = db.Column(db.String(255), nullable=False)
    emp_contact = db.Column(db.String(20), nullable=False)
    emp_username = db.Column(db.String(50), unique=True, nullable=False)
    emp_dept = db.Column(db.String(50), nullable=False)
    emp_pass = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

# Define the Position model
class Position(db.Model):
    pos_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pos_title = db.Column(db.String(100), unique=True, nullable=False)
    pos_description = db.Column(db.Text, nullable=True)

# Define the EmployeePosition model
class EmployeePosition(db.Model):
    emp_id = db.Column(db.Integer, db.ForeignKey('employee.emp_id'), primary_key=True)
    pos_id = db.Column(db.Integer, db.ForeignKey('position.pos_id'), primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    employee = db.relationship('Employee', backref='positions')
    position = db.relationship('Position', backref='employees')

# Define the Leaves model
class Leaves(db.Model):
    leave_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employee.emp_id'), nullable=False)
    leave_start_date = db.Column(db.Date, nullable=False)
    leave_end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    leave_status = db.Column(db.String(50), nullable=False)
    employee = db.relationship('Employee', backref='leaves')

# Helper function to serialize SQLAlchemy objects
def serialize_query(query):
    return [dict(row) for row in query]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees')
def employees():
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)

@app.route('/positions')
def positions():
    positions = Position.query.all()
    return render_template('positions.html', positions=positions)

@app.route('/employee_positions')
def employee_positions():
    employee_positions = EmployeePosition.query.all()
    return render_template('employee_positions.html', employee_positions=employee_positions)

@app.route('/leaves')
def leaves():
    leaves = Leaves.query.all()
    return render_template('leaves.html', leaves=leaves)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        data = request.form
        try:
            new_employee = Employee(
                emp_address=data.get('emp_address'),
                emp_fullname=data.get('emp_fullname'),
                emp_contact=data.get('emp_contact'),
                emp_username=data.get('emp_username'),
                emp_dept=data.get('emp_dept'),
                emp_pass=data.get('emp_pass'),
                created_date=datetime.strptime(data.get('created_date', ''), '%Y-%m-%d')  # Ensure date is in the correct format
            )
            db.session.add(new_employee)
            db.session.commit()
            return redirect(url_for('employees'))
        except KeyError as e:
            return jsonify({"error": f"Missing field: {str(e)}"}), 400
        except ValueError as e:
            return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    return render_template('add_employee.html')

@app.route('/add_position', methods=['GET', 'POST'])
def add_position():
    if request.method == 'POST':
        data = request.form
        try:
            new_position = Position(
                pos_title=data.get('pos_title'),
                pos_description=data.get('pos_description', '')  # Default to empty string if not provided
            )
            db.session.add(new_position)
            db.session.commit()
            return redirect(url_for('positions'))
        except KeyError as e:
            return jsonify({"error": f"Missing field: {str(e)}"}), 400
    return render_template('add_position.html')

@app.route('/add_leave', methods=['GET', 'POST'])
def add_leave():
    if request.method == 'POST':
        data = request.form
        try:
            new_leave = Leaves(
                emp_id=int(data.get('emp_id')),
                leave_start_date=datetime.strptime(data.get('leave_start_date', ''), '%Y-%m-%d'),
                leave_end_date=datetime.strptime(data.get('leave_end_date', ''), '%Y-%m-%d'),
                leave_type=data.get('leave_type'),
                leave_status=data.get('leave_status')
            )
            db.session.add(new_leave)
            db.session.commit()
            return redirect(url_for('leaves'))
        except KeyError as e:
            return jsonify({"error": f"Missing field: {str(e)}"}), 400
        except ValueError as e:
            return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    return render_template('add_leave.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
