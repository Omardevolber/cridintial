from flask import render_template, request, flash, redirect, url_for
from app import app
from services.selenium_service import run_selenium_script

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def run_script():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash('يرجى إدخال البريد الإلكتروني وكلمة المرور', 'error')
        return redirect(url_for('index'))

    try:
        credentials = run_selenium_script(email, password)
        if credentials:
            return render_template('result.html', credentials=credentials)
        else:
            flash('لم يتم العثور على بيانات الاعتماد', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('index'))
