import random
import secrets
import string
from flask import Flask, flash, render_template, request, session, redirect, url_for, g
import sqlite3
from flask_mail import Mail, Message
import time
import dash
from dash import dcc,html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import base64
import io
import os
import sys
import numpy as np

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import datetime

from sklearn.metrics import f1_score


sys.path.append('./Code/Feature_Implementation')
sys.path.append('./Code/Algorithms')
sys.path.append('./Code/dataset')
sys.path.append('./Code/preprocessing')

from total_num_beats import total_num_beats
from PVCs_hora import total_num_pvcs
from beats_per_minute import bpms
from PVCs_hora import PVCs_hour
from read_mat_file import mat_tolists
import joblib
from windowed_ecg import window_ecg
from extract_features import features
from ecg_graph import ecg_plot
from total_cycles import count_consecutive_ones
from avg_pvc_cycle import average_pvc_cycle
from avg_beat_graph import avg_graph
algorithm_path = os.path.abspath('./Code/Algorithms/Random_Forest.joblib')
model=joblib.load(algorithm_path)


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DATABASE = 'users.db'

# Function to get a connection to the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Function to close the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create a table for users
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY NOT NULL,
                     password TEXT NOT NULL,
                     email TEXT NOT NULL,
                     reset_token TEXT);''')
        db.commit()

# Initialize the database
init_db()

# Function to check if a user exists in the database
def not_user(username, email):
    db = get_db()
    cursor = db.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
    row = cursor.fetchone()
    if row is not None:
        if row[0] == username:
            return "nome de utilizador"
        else:
            return "email"
    else:
        return None

# Function to add a new user to the database
def add_user(username, password, email):
    field = not_user(username, email)
    if field is None:
        db = get_db()
        db.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
        db.commit()
        return True
    else:
        return False



def check_user(username, password):
    db = get_db()
    cursor = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = cursor.fetchone()
    if row is not None:
        return True
    else:
        return False

def check_email(email):
    db = get_db()
    cursor = db.execute("SELECT username FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    if row is not None:
        return row[0]
    else:
        return False

def generate_reset_token(email,reset_token):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        cursor.execute("UPDATE users SET reset_token=? WHERE username=?", (reset_token, row[0]))
        db.commit()
        return True

def update_password(token, new_password):
    db = get_db()
    cursor = db.execute("SELECT email FROM users WHERE reset_token=?", (token,))
    row = cursor.fetchone()
    if row is not None:
        email = row[0]
        db.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
        db.commit()
        return True
    else:
        return False

def get_username_by_token(token):
    db = get_db()
    cursor = db.execute("SELECT username FROM users WHERE reset_token=?", (token,))
    row = cursor.fetchone()
    if row is not None:
        return True,row[0]
    else:
        return False,None

def del_token_by_username(username):
    db = get_db()
    db.execute("UPDATE users SET reset_token = NULL WHERE username = ?", (username,))
    db.commit()

def get_password_by_username(username):
    db = get_db()
    cursor = db.execute("SELECT password FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if row is not None:
        return row[0]


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if add_user(username, password, email):
            flash('Registado com sucesso', 'success')  # Specify the category as 'success'
            return redirect(url_for('login'))
        else:
            field = not_user(username, email)
            error_message = "Esse {} já existe. Escolha um {} diferente".format(field, field)
            return render_template('register.html', error_message=error_message)
    else:
        return render_template('register.html')


# Route for the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error_message='Nome de Utilizador ou Palavra-Passe inválida')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Log out feito com sucesso!','logout')
    return redirect(url_for('login'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('password.html')
    else:
        email = request.form['email']

        # Check if email is registered in your database
        # If not, display an error message
        # Otherwise, generate a reset token and send a password reset email
        user = check_email(email)
        if user is False:
            return render_template('password.html', error_message='Email não registado!')
        else:
            # Generate a reset token
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
            print("token gerado",token)

            # Store the token in your database
            set_token=generate_reset_token(email,token)
            if set_token is True:
                # Send the password reset email
                sender_email = 'pactpvc@hotmail.com'
                sender_password = 'PACTp4ct'
                recipient_email = email
                subject = 'Pedido de alteração de palavra-passe'
                message = message = f'Olá {user},\n\nPara alterar a sua palavra-passe, clique no seguinte link:\n\n{request.host_url}reset_password\n\nToken:\n{token}\n\nOs melhores cumprimentos,\nA equipa PACT'


                msg = MIMEText(message)
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject

                try:
                    smtp_server = smtplib.SMTP('smtp-mail.outlook.com', 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login(sender_email, sender_password)
                    smtp_server.send_message(msg)
                    smtp_server.quit()
                    return  render_template('password.html', success_message='Foi enviado um email com as instruções para alterar a sua palavra-passe.')
                except Exception as e:
                    print(e)
                    return  render_template('password.html', error_message='Ocurreu um erro ao enviar o email')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset():
    # Check if the reset token is valid and has not expired
    if request.method == 'POST':
        token = request.form['token']
        password = request.form['password']
        newpassword = request.form['newpassword']
        user_bool,user=get_username_by_token(token)
        print(token)
        print("user",user)
        print("user_bool",user_bool)
        if user:
            old_password=get_password_by_username(user)
            if password == newpassword:
                if password != old_password:
                    update_password(token,password)
                    del_token_by_username(user)
                    flash('Palavra-passe alterada com sucesso!','password')
                    return redirect(url_for('login'))
                else:
                    return render_template('reset_password.html',error_message='A palavra-passe coincide com a já existente')
            else:
                return render_template('reset_password.html',error_message='As palavras-passe não coincidem')
        else:
            return render_template('reset_password.html',error_message='Token inválido!')
    else:
        return render_template('reset_password.html')



external_stylesheets = ['./static/bootstrap.css']

dash_app = dash.Dash(external_stylesheets=external_stylesheets,server=app, name="Dashboard", url_base_pathname="/dash/")
dash_app.title="PACT-PVC Detection"
navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row([
                    dbc.Col(html.H1('PACT'),md=4),
                    dbc.Col([
                # Logout button
                dbc.Button("Logout",id='logout-button',color='secondary',style={"line-height":"20px","padding-left":"20px","padding-right":"20px","margin-left":"1097px"}),
                html.Div(id='logout-redirect'),
            ], md=8, style={"align": "right","margin-top":"10px"})
                ],
            ),
        )
    ],
    color= 'rgba(90, 88, 215,0.8)',
    sticky="top",


)

modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Frequência de Amostragem",close_button=False),
                dbc.ModalBody(
                    [
                        html.Div(
                            [
                                html.P("Insira um valor para a frequência de amostragem (Hz)"),
                                dbc.Input(
                                    type="number",
                                    id="frequency-input",
                                    placeholder="Insira o valor",
                                    min=0,
                                    max=1000000,
                                ),
                                html.P("Nota: Caso não insira nenhum valor ou 0 será utilizado o valor default (360Hz)", style={"font-size":"12px"})
                            ],
                        ),
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Confirmar", id="save-modal-button", className="ml-auto", color="secondary"
                        ),
                    ]
                ),
            ],
            id="frequency-modal",
            centered=True,
            size="md",
        )
    ]
)


# Layout
dash_app.layout =dbc.Spinner(spinner_class_name="loader", fullscreen=True, children=[dbc.Container(
    dbc.Row([
        dbc.Col([
            html.Div([
            navbar
        ],style={"width":"112%"}),
        ]),

        dbc.Row([
            dbc.Col([
            dbc.Button(dcc.Upload(
                                    id='upload-data',
                                    children=html.Div([
                                        'Upload ',
                                    ],),
                                    # Allow multiple files to be uploaded
                                    multiple=False
        ),color='secondary',style={'margin:': '10px',"padding-left":"20px","padding-right":"20px","margin-left":"70px"}),
    ],md=2,style={"align":'left'}),
            dbc.Col([
                html.Div(id='output-data-upload',style={"width":"95%","padding-left":"280px","padding-top":"20px","line-height":"10px"}),
                dcc.Store(id='message')
            ],md=6,style={"align":"center"}),

              dbc.Col([
                dbc.Button('Frequência',id='frequency-button',className="mr-2", color='secondary',style={"marginLeft":"160px","padding-left":"20px","padding-right":"20px"}),
            ],md=2,style={"align":"right"}),

            dbc.Col([
                        dbc.Button('Analisar', id='analyze-button',className="mr-2", color='secondary',style={"marginLeft":"60px","padding-left":"20px","padding-right":"20px"}),
                        modal,
                        dcc.Store(id='frequency-output'),
                        dcc.Store(id='dados', data=[]),
            ],md=2,style={"align":"right"})
    ]),

        dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("ECG Graph",style={"color": "#000000"}),
                            html.Div("",id='ecg-figure'),
                            html.Div(id='container-id',children=[
                                dcc.Slider(
                                    id='slider',
                                    min=1,
                                    max=30,
                                    step=1,
                                    value=1),
                                ], style={'display': 'none'}),
                    ])
                    ], color="light", outline=True, style={"height":"700px", "margin-top": "10px",
                                                        "box-shadow": "0 4px 4px 0 rgba(0,0,0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19}",
                                                        'background-color': 'rgba(255, 255, 255, 0.8)','border-color': 'transparent','opacity': 0.9})
                ],md=8,style={"align":"left","padding-left":"70px"}),
                dbc.Col([
                    dbc.Card([
                    dbc.CardBody([
                            html.H6("Numero Total de Batimentos",style={"color": "#000000"}),
                            html.H3("-",style={"color": "#5A58D7"}, id="num-total-batimentos"),
                            html.H6("PVC/h",style={"color": "#000000"}),
                            html.H3("-",style={"color": "#5A58D7"}, id="num-pvc-h"),
                            html.H6("Numero Total de PVCs",style={"color": "#000000"}),
                            html.H3("-",style={"color": "#5A58D7"}, id="num-total-pvc"),
                            html.H6("Batimentos por minuto (bpm)",style={"color": "#000000"}),
                            html.H3("-",style={"color": "#5A58D7"}, id="num-batimento-medio"),
                            html.H6("Numero total de ciclos",style={"color": "#000000"}),
                            html.H3("-",style={"color": "#5A58D7"}, id="num-ciclos"),
                            html.H6("Média de PVCs por ciclo",style={"color": "#000000"}),
                            html.H3("-",style={"color": "#5A58D7"}, id="media-ciclos"),
                            html.H6("F1-Score",style={"color": "#000000"}),
                            html.H3("-",style={"color": "#5A58D7"}, id="f1-score"),
                            html.H6("Batimento Médio",id='title-graph',style={'display':'none', "color": "#000000"}),
                            html.Div("",id='ecg-mean-graph', style={"margin-left":"-87px","margin-top":"15px"})
                        ])
                    ], color="light", outline=True, style={"margin-top": "10px",
                                                        "box-shadow": "0 4px 4px 0 rgba(0,0,0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19}",
                                                        'background-color': 'rgba(255, 255, 255, 0.8)','border-color': 'transparent','opacity': 0.8}),
                ], md=4,style={"padding-right":"-50px","align":"right"}),
    ])
    ]),style={"margin":0,"width":"100%"}
    )]
    )


@dash_app.callback(Output('logout-redirect', 'children'),
                  Input('logout-button', 'n_clicks'))
def logout(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        # Clear the session data
        session.clear()
        # Redirect the user to the login page
        return dcc.Location(pathname='/logout', id='logout-redirect-url')
    else:
        return None

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if '.mat' in filename:
            # Assuming the file is a .mat file
            ecg, r, pvc = mat_tolists(io.BytesIO(decoded))
            return dbc.Alert('Arquivo carregado com sucesso!', color="success",className="text-center",style={'align':'center'})
        else:
            return dbc.Alert('Oops! O arquivo selecionado deve ser .mat', color="primary",className="text-center",style={'align':'center'})
    except Exception as e:
        print(e)
        return dbc.Alert('Oops! Ocorreu um erro ao processar este arquivo.', color="primary",className="text-center",style={'align':'center'})


@dash_app.callback(
    [Output('dados','data'),
    Output('output-data-upload', 'children'),
    Output('num-total-batimentos', 'children'),
    Output('num-pvc-h', 'children'),
    Output('num-total-pvc', 'children'),
    Output('num-batimento-medio', 'children'),
    Output('num-ciclos', 'children'),
    Output('media-ciclos', 'children'),
    Output('f1-score','children'),
    Output('ecg-mean-graph','children'),
    Output('title-graph','style')],
    [Input('upload-data', 'contents'),
    Input('upload-data', 'filename'),
    Input('analyze-button', 'n_clicks'),
    Input("frequency-output","value")],
    [State("frequency-button", "n_clicks"),
    State('output-data-upload', 'children')])

def update_card(contents, filename, n_clicks, frequency,freq_button, upload):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'upload-data':
            try:
                if contents is not None:
                    return  [], \
                        parse_contents(contents, filename), \
                        "-" , \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "", \
                        {'display':'none'}

                else:
                    return  [], \
                        dash.no_update, \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "", \
                        {'display':'none'}

            except Exception as e:
                print(e)
                return  [], \
                        dbc.Alert('Oops! Ocorreu um erro ao processar este arquivo.', color="primary",className="text-center",style={'align':'center'}), \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "", \
                        {'display':'none'}


        elif button_id == 'analyze-button' :
            try:
                if contents is not None:
                        if upload['props']['children'] == "Arquivo carregado com sucesso!":
                            if freq_button:
                                fs=frequency
                            else:
                                fs= 360.0
                            content_type, content_string = contents.split(',')
                            decoded = base64.b64decode(content_string)
                            ecg, r, pvc = mat_tolists(io.BytesIO(decoded))
                            duracao = len(ecg)/fs/60
                            data=[ecg,r,pvc,fs]
                            ecg_window=window_ecg(ecg,r)
                            fig=avg_graph(ecg,r)
                            ftrs = features(ecg_window, r)
                            total_batimentos = total_num_beats(r)
                            predicted_pvc=model.predict(ftrs)
                            f1 = round(f1_score(pvc, predicted_pvc),2)
                            total_pvc = total_num_pvcs(predicted_pvc)
                            pvc_hora = PVCs_hour(total_pvc, time_interval = duracao)
                            batimento_medio = bpms(r, time=duracao)
                            total_ciclos,total_pvc_por_ciclos= count_consecutive_ones(predicted_pvc)
                            media_ciclos=average_pvc_cycle(total_pvc_por_ciclos)
                            return  data, \
                                dbc.Alert('Arquivo carregado com sucesso!', color="success",className="text-center",is_open=False, style={'align':'center'}), \
                                total_batimentos, \
                                pvc_hora, \
                                total_pvc, \
                                batimento_medio, \
                                total_ciclos, \
                                media_ciclos, \
                                f1, \
                                dcc.Graph(figure=fig,style={"marginLeft":"70px","color": "rgba(255,255,255,0.7)"}), \
                                {'display':'inline', "color": "#000000"}

                        else:
                            return  [], \
                                dbc.Alert('Oops! Ocorreu um erro, carregue um arquivo válido.', color="primary",className="text-center",style={'align':'center'}), \
                                "-", \
                                "-", \
                                "-", \
                                "-", \
                                "-", \
                                "-", \
                                "-", \
                                "", \
                                {'display':'none'}

                else:
                    return  [], \
                            dbc.Alert('Oops! Nenhum arquivo foi carregado.', color="primary",className="text-center",style={'align':'center'}), \
                            "-", \
                            "-", \
                            "-", \
                            "-", \
                            "-", \
                            "-", \
                            "-", \
                            "", \
                            {'display':'none'}

            except Exception as e:
                print(e)
                return  [], \
                        dbc.Alert('Oops! Ocorreu um erro ao analisar este arquivo.', color="primary",className="text-center",style={'align':'center'}), \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "-", \
                        "", \
                        {'display':'none'}




@dash_app.callback(
    Output("frequency-modal", "is_open"),
    [Input("frequency-button", "n_clicks"), Input("save-modal-button", "n_clicks")],
    [State("frequency-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@dash_app.callback(
    Output("frequency-output", "value"),
    [Input("save-modal-button", "n_clicks")],
    [State("frequency-input", "value")],
)
def update_frequency_output(n_clicks, frequency):
    if n_clicks:
        if frequency is not None and frequency > 0:
            return frequency
        else:
            return 360.0

@dash_app.callback(
    [Output('ecg-figure', 'children'),
    Output('slider','max')],
    [Input('slider', 'value'),
    Input('dados', 'data')],
    [State('output-data-upload', 'children')]
)
def update_graph(slider_value,data,upload):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if  len(data) > 0:
        if upload['props']['children'] == "Arquivo carregado com sucesso!":
            # Update the figure based on the slider value
            ecg,r,pvc,fs=data[0],data[1],data[2],data[3]
            duração=np.ceil((len(ecg)/fs)/60)
            ecg_window=window_ecg(ecg,r)
            ftrs = features(ecg_window, r)
            predicted_pvc=model.predict(ftrs)
            updated_fig = ecg_plot(ecg, r, predicted_pvc,slider_value, fs)
            updated_fig.update_layout(margin= {'l': 0, 'r': 0, 't': 0, 'b': 0}, legend=dict(orientation='h',yanchor='bottom'))
            return dcc.Graph(figure=updated_fig,style={'height':"595px","width":"900px","marginLeft":"70px","color": "rgba(255,255,255,0.7)"}),duração
    return "", 30


@dash_app.callback(
    Output('container-id','style'),
    [Input('ecg-figure','children')]
)
def show_slider(figure):
    if figure:
        return {'display':'inline'}
    else:
        return {'display':'none'}



# Route for the home page (requires login)
@app.route('/dash')
def home():
    if 'username' in session:
        return dash_app.index()
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
