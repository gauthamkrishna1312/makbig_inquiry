from flask import Flask, render_template, request, redirect, url_for, flash
import gspread
import os
import datetime
import traceback

app = Flask(__name__, template_folder='.')
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Google Sheets Setup
# IMPORTANT: You need to download your JSON key file and name it 'credentials.json'
CREDENTIALS_FILE = 'credentials.json'
# REPLACE THIS WITH YOUR FULL GOOGLE SHEET URL
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1fVlvAEUlCKCjBREy08O0OYcGbUc-BaKnHna21Ucm_Uk/edit?usp=sharing'

def get_sheet():
    try:
        # Modern gspread authentication (simpler and more robust)
        # ensure credentials.json is in the same directory
        client = gspread.service_account(filename=CREDENTIALS_FILE)
        # Open by URL is much SAFER than by name (avoids typos/duplicates)
        sheet = client.open_by_url(SHEET_URL).sheet1
        return sheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        # Print full traceback to see exactly what went wrong
        traceback.print_exc()
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        qualification = request.form.get('qualification')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Basic validation
        if not fullname or not phone or not qualification:
            flash('All fields are required!', 'error')
            return redirect(url_for('index'))

        sheet = get_sheet()
        if sheet:
            try:
                sheet.append_row([timestamp, fullname, phone, qualification])
                flash('Application Submitted Successfully!', 'success')
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
        else:
            flash('Could not connect to Google Sheets. Check server logs/credentials.', 'error')

        return redirect(url_for('index'))

if __name__ == '__main__':
    # Running on 0.0.0.0 to be accessible if needed, port 5000
    app.run(debug=True, host='0.0.0.0', port=5001)
