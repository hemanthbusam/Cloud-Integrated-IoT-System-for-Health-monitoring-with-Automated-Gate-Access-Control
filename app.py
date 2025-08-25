from flask import Flask, render_template, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Function to get a new database connection
def get_db_connection():
    return mysql.connector.connect(host="localhost", user="root", password="", database="iothealth")

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/report', methods=['GET'])
def index():
    return render_template('report.html')

@app.route('/history', methods=['GET'])
def get_attendance():
    status = request.args.get('status', '')

    employee = request.args.get('employee', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    temp = request.args.get('temp', '')
    mask = request.args.get('mask', '')
    alcohol = request.args.get('alcohol', '')
    statusstr=''
    if status=='All':
        statusstr=' and  1=1'
    if status=='Allowed':
        statusstr=' and  ( h.temperature<37.5 and h.mask_detected=1 and h.alcohol_detected=0 )'
    if status=='NotAllowed':
        statusstr=' and ( h.temperature>37.4 or h.mask_detected=0 or  h.alcohol_detected=1 )'
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT e.empid, e.empname, 
               h.timestamp, h.temperature<37.5 and h.mask_detected=1 and h.alcohol_detected=0
        FROM empmaster e
        LEFT JOIN employee_health_monitor h ON e.empid = h.employee_id
        WHERE 1=1
    """
    
    params = []

    if employee:
        query += " AND e.empname LIKE %s"
        params.append(f"%{employee}%")

    if from_date:
        query += " AND h.timestamp >= %s"
        params.append(from_date)

    if to_date:
        query += " AND h.timestamp <= %s"
        params.append(to_date)

    if temp:
        query += " AND h.temperature >= %s"
        params.append(temp)

    if mask in ['0', '1']:
        query += " AND h.mask_detected = %s"
        params.append(mask)

    if alcohol in ['0', '1']:
        query += " AND h.alcohol_detected = %s"
        params.append(alcohol)
    query += statusstr 
    # query += " and temperature<15 and h.alcohol_detected=0 and h.mask_detected=1 "
    query += " ORDER BY h.timestamp DESC"
    print(query)
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()

    return render_template('history.html', attendance_data=data)

@app.route('/data', methods=['GET'])
def get_data():
    empid = request.args.get('empid', '')
    temperature = request.args.get('temperature', '')
    alcohol = request.args.get('alcohol', '')
    mask_detected = request.args.get('mask_detected', '')
    all_conditions = request.args.get('all_conditions', '')  # New condition
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM employee_health_monitor WHERE 1=1"
    params = []

    if empid:
        query += " AND employee_id = %s"
        params.append(empid)

    if temperature:
        query += " AND temperature >= %s"
        params.append(temperature)

    if alcohol in ['0', '1']:
        query += " AND alcohol_detected = %s"
        params.append(alcohol)

    if mask_detected in ['0', '1']:
        query += " AND mask_detected = %s"
        params.append(mask_detected)

    if all_conditions:  # If "All" is selected, filter detected cases only
        query += " AND (temperature >= 37.5 OR alcohol_detected = 1 OR mask_detected = 0)"

    if from_date:
        query += " AND timestamp >= %s"
        params.append(from_date + " 00:00:00")  # Ensures start of the day

    if to_date:
        query += " AND timestamp <= %s"
        params.append(to_date + " 23:59:59")  # Ensures end of the day

    query += " ORDER BY timestamp DESC"

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()

    return jsonify(data)

 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
