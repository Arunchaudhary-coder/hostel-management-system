from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'hostel_secret_key'
DATA_FILE = '/home/hostetmanagement/mysite/hostel_data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "B-101": {"type": "Boys", "students": []},
            "B-102": {"type": "Boys", "students": []},
            "B-103": {"type": "Boys", "students": []},
            "G-101": {"type": "Girls", "students": []},
            "G-102": {"type": "Girls", "students": []},
            "G-103": {"type": "Girls", "students": []}
        }
        save_data(initial_data)
        return initial_data
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == 'admin' and pwd == '123':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid Username or Password!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    rooms = load_data()
    return render_template('index.html', rooms=rooms, message=request.args.get('msg'))

@app.route('/allot', methods=['POST'])
def allot_room():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    name = request.form.get('name').strip()
    roll_no = request.form.get('roll_no').strip()
    phone = request.form.get('phone').strip()
    gender = request.form.get('gender')
    room_no = request.form.get('room_no')
    rooms = load_data()
    
    if room_no in rooms:
        if rooms[room_no]["type"] != gender:
            return redirect(url_for('index', msg=f"Error: Room {room_no} is strictly for {rooms[room_no]['type']} only!"))
        
        if len(rooms[room_no]["students"]) < 2:
            rooms[room_no]["students"].append({
                "name": name,
                "roll_no": roll_no,
                "phone": phone,
                "fee": "Pending",
                "attendance": "Present"
            })
            save_data(rooms)
            return redirect(url_for('index', msg=f"Success: Room {room_no} ({gender}) allotted to {name}!"))
        else:
            return redirect(url_for('index', msg=f"Error: Room {room_no} is already full!"))
    return redirect(url_for('index', msg="Error: Invalid Room Number!"))

@app.route('/toggle_fee/<room_no>/<roll_no>')
def toggle_fee(room_no, roll_no):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    rooms = load_data()
    if room_no in rooms:
        for s in rooms[room_no]["students"]:
            if s['roll_no'] == roll_no:
                s['fee'] = 'Paid' if s.get('fee') == 'Pending' else 'Pending'
        save_data(rooms)
    return redirect(url_for('index', msg=f"Success: Mess fee status updated for Roll No {roll_no}."))

@app.route('/toggle_att/<room_no>/<roll_no>')
def toggle_att(room_no, roll_no):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    rooms = load_data()
    if room_no in rooms:
        for s in rooms[room_no]["students"]:
            if s['roll_no'] == roll_no:
                s['attendance'] = 'Absent' if s.get('attendance') == 'Present' else 'Present'
        save_data(rooms)
    return redirect(url_for('index', msg=f"Success: Attendance updated for Roll No {roll_no}."))

@app.route('/vacate/<room_no>/<roll_no>')
def vacate_seat(room_no, roll_no):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    rooms = load_data()
    if room_no in rooms:
        rooms[room_no]["students"] = [s for s in rooms[room_no]["students"] if s['roll_no'] != roll_no]
        save_data(rooms)
        return redirect(url_for('index', msg=f"Success: Student removed from Room {room_no}."))
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
