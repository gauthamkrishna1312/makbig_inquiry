from flask import Flask, render_template, request, redirect, url_for, flash
import gspread
import os
import datetime
import traceback
import json

# Adjust template_folder and static_folder because this file is inapi/
# and templates/static are likely in the root (../)
# Adjust template_folder and static_folder because this file is inapi/
# and templates/static are likely in the root (../)
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'supersecretkey'

# Google Sheets Setup
# REPLACE THIS WITH YOUR FULL GOOGLE SHEET URL
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1fVlvAEUlCKCjBREy08O0OYcGbUc-BaKnHna21Ucm_Uk/edit?usp=sharing'

def get_sheet():
    try:
        # 1. Try to get credentials from Environment Variable (Best for Vercel)
        creds_json_str = os.environ.get('GOOGLE_CREDENTIALS')
        
        if creds_json_str:
            print("Loading credentials from environment variable...")
            creds_dict = json.loads(creds_json_str)
            client = gspread.service_account_from_dict(creds_dict)
        else:
            # 2. Fallback to local file (Best for local development)
            # Look for credentials.json in the project root (one directory up)
            print("Loading credentials from local file...")
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            creds_file_path = os.path.join(base_dir, 'credentials.json')
            
            client = gspread.service_account(filename=creds_file_path)

        # Open by URL is much SAFER than by name
        sheet = client.open_by_url(SHEET_URL).sheet1
        return sheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
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
                flash('Application Submitted Successfully!<br> Link to discord: <a href="https://discord.gg/4j528888" target="_blank" style="color: #4ade80; text-decoration: underline;">Join Discord</a>', 'success')
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
        else:
            flash('Could not connect to Google Sheets. Check server logs/credentials.', 'error')

        return redirect(url_for('index'))

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
