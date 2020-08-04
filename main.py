from random import choice
from string import digits, ascii_uppercase

from pymongo import MongoClient
from flask import Flask, session, request, render_template, url_for, redirect

client = MongoClient("rahasia")
col_admin, col_users = client.contoh.admin, client.contoh.users

app = Flask(__name__)
app.secret_key = "rahasia"

@app.route('/', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    if "admin" in request.form['email'] and col_admin.find_one({'email' : request.form['email'], 'sandi' : request.form['sandi']}) is not None:
      session['akun'] = col_admin.find_one({'email' : request.form['email'], 'sandi' : request.form['sandi']})['_id']
      return redirect(url_for('admin', id = session['akun']))

    elif col_users.find_one({'email' : request.form['email'], 'sandi' : request.form['sandi']}) is not None:
      session['akun'] = col_users.find_one({'email' : request.form['email'], 'sandi' : request.form['sandi']})['_id']
      return redirect(url_for('user', id = session['akun']))

    else:
      return render_template('login.html', pesan = 'email atau kata sandi anda salah!1!')

  elif session and "admin" in session['akun']:
    return redirect(url_for('admin', id = session['akun']))

  elif session and "admin" not in session['akun']:
    return redirect(url_for('user', id = session['akun']))
  
  else:
    return render_template('login.html')

@app.route('/admin/<id>', methods=['GET', 'POST'])
def admin(id):
  if session and id == session['akun']:
    users_data = [data for data in col_users.find()]

    if request.method == 'POST':
      col_users.insert_one({"_id" : ''.join(choice(ascii_uppercase + digits) for _ in range(8)),
                            "email" : request.form['email'],
                            "sandi" : request.form['sandi'],
                            "username" : request.form['usernm'],
                            "alamat" : request.form['alamat']})

      return redirect(url_for('admin', id = id))

    return render_template('laman_admin.html', id =id, data = users_data)
  else:
    return redirect('/')

@app.route('/user/<id>')
def user(id):
  if session and id == session['akun']:
    data = col_users.find_one({'_id' : id})
    return render_template('laman_user.html', data = data)
  else:
    return redirect('/')

@app.route('/user/edit/<id>', methods=['GET', 'POST'])
def user_edit_data(id):
  if session and id == session['akun']:
    if request.method == 'POST':
      col_users.update_one({'_id' : id},
      {"$set" : {"email" : request.form['email'],
                 "sandi" : request.form['sandi'],
                 "username" : request.form['usernm'],
                 "alamat" : request.form['alamat']
                 }})
      return redirect(url_for('user', id = id))

    return render_template('edit_data_user.html', data = col_users.find_one({'_id' : id}))
  else:
    return redirect('/')

@app.route('/user/hapus/<id>')
def user_hapus_akun(id):
  if session and id == session['akun']:
    col_users.remove({'_id' : id})
    return redirect(url_for('logout', id = id))
  else:
    return redirect('/')

@app.route('/logout')
def logout():
  if session:
    session.pop('akun')
    return redirect('/')
  else:
    return redirect('/')

#app.run(debug=True)
