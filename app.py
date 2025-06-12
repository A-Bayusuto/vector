from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from ChatBuilder import *
from ChatWithRAGV1 import *
from RAG_Azure import *
from dotenv import load_dotenv, dotenv_values, set_key
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import json

app = Flask(__name__)

load_dotenv(override=True)
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

endpoint = os.getenv("ENDPOINT_URL")  
deployment = os.getenv("DEPLOYMENT_NAME")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")  
api_version = os.getenv("API_VERSION")
condition = os.getenv("CONDITION")

client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version=api_version,  
)
chat_builder = ChatBuilder(client=client)
system_role = os.getenv("SYSTEM_ROLE")
temperature = float(os.getenv("TEMPERATURE"))
vector_db_path = os.getenv("VECTOR_DB")

chat_builder.set_deployment(deployment)
chat_builder.set_temperature(temperature)
chat_builder.set_system(system_role)
chat_builder.messages.append(chat_builder.sys_content)

chat_history_folder = "./chat_history"
chat_history_dropdown = [f for f in os.listdir(chat_history_folder)]

# vector_db_path = os.getenv("VECTOR_DB")
vector_storage_folder = "./vector_storage"
vector_dbs = ["General Chat"]
vector_dbs += [f for f in os.listdir(vector_storage_folder) if f.endswith('.index')]
default_db = ["General Chat"]

TEMPORARY_FOLDER = 'temp_storage'
UPLOAD_FOLDER = 'vector_storage'
CONFIG_FILE = "config.json"
app.config['TEMPORARY_FOLDER'] = TEMPORARY_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'csv', 'pdf'}

def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_config():
    """Read the temperature value from the JSON file."""
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return config

def write_config(key, value):
    """Update the temperature value in the JSON file."""
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    config[key] = value

    # Write the updated contents back to the file
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def get_config_variable(variable_name):
    """Fetch a specific variable's value from the JSON config file."""
    config = read_config()
    
    # Return the requested variable if it exists, otherwise raise an error
    if variable_name in config:
        # return jsonify({variable_name: config[variable_name]})
        return config[variable_name]
    else:
        return jsonify({"error": f"Variable '{variable_name}' not found in configuration"}), 404


@app.route("/get_temperature", methods=["GET"])
def get_temperature():
    """Fetch a specific variable's value from the JSON config file."""
    config = read_config()
    
    # Return the requested variable if it exists, otherwise raise an error
    if "TEMPERATURE" in config:
        # return jsonify({variable_name: config[variable_name]})
        return config['TEMPERATURE']
    else:
        return jsonify({"error": f"Variable 'TEMPERATURE' not found in configuration"}), 404

@app.route("/update_temperature", methods=["POST"])
def update_temperature():
    """Update the temperature."""
    data = request.get_json()  # Expecting JSON payload like {"temperature": 0.5}
    new_temperature = data.get("temperature")
    if new_temperature is not None:
        write_config("TEMPERATURE", new_temperature)  # Update the JSON file
        return jsonify({"message": "Temperature updated", "temperature": new_temperature})
    return jsonify({"error": "Invalid request"}), 400

@app.route("/set_system", methods=["POST"])
def set_system():
    data = request.get_json()  # Parse JSON payload
    # default_db = data.get("default_db")
    # slider_value = data.get("slider_value")
    new_sys_role = data.get("system_role")
    if new_sys_role is not None:
        write_config("SYSTEM_ROLE", new_sys_role)
        return jsonify({"message": "System Role updated", "System Role": new_sys_role})
    return jsonify({"error": "Invalid request"}), 400

def get_latest_sys():
    new_sys_role = get_config_variable("SYSTEM_ROLE")
    chat_builder.set_system(new_sys_role)
    chat_builder.messages[0] = chat_builder.sys_content

@app.route("/save", methods=["POST"])
def save_data():
    temperature = float(os.getenv("TEMPERATURE"))
    file_name = request.form.get("file_name")
    if not file_name:  # Validate that file_name is not empty
        time_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"automated_save_{time_now}"

    try:
        # Save messages to the specified file
        print(chat_builder.messages)
        chat_builder.save_messages_to_file(file_name)
        chat_history_folder = "./chat_history"
        chat_history_dropdown = [f for f in os.listdir(chat_history_folder)]
        # Return a success message
        vector_dbs = ["General Chat"]
        vector_dbs += [f for f in os.listdir(vector_storage_folder) if f.endswith('.index')]
        vector_db_path = request.form.get("vectordb")
        temperature = get_config_variable("TEMPERATURE")
        return render_template('index.html', 
                           chat_history_dropdown=chat_history_dropdown, 
                           vector_dbs=vector_dbs, 
                           messages=chat_builder.messages[1:],
                           default_db = vector_db_path,
                           temperature = temperature)
    except Exception as e:
        # Handle any errors during the save process
        return jsonify({"error": str(e)}), 500

@app.route("/load", methods=["POST"])
def load_data():
    temperature = float(os.getenv("TEMPERATURE"))
    file_name = request.form.get("chat_name")
    print('file name: ')
    print(file_name)
    chat_builder.load_messages_from_file(file_name)
    assistant_response = f"Messages loaded from file: {file_name}"
    print(chat_builder.messages)
    messages = chat_builder.messages
    messages.append({"role": "assistant", "content": assistant_response})
    vector_dbs = ["General Chat"]
    vector_dbs += [f for f in os.listdir(vector_storage_folder) if f.endswith('.index')]
    vector_db_path = request.form.get("vectordb")
    temperature = get_config_variable("TEMPERATURE")
    chat_history_dropdown = [f for f in os.listdir(chat_history_folder)]
    return render_template('index.html', 
                            chat_history_dropdown=chat_history_dropdown, 
                            vector_dbs=vector_dbs, 
                            messages=chat_builder.messages[1:],
                            default_db = vector_db_path,
                            temperature = temperature)

@app.route("/upload", methods=["POST"])
def upload_data():
    print("entered upload data")
    temperature = float(os.getenv("TEMPERATURE"))
    # Define your upload logic here
    if 'fileInput' not in request.files:
        vector_db_path = request.form.get("vectordb")
        temperature = get_config_variable("TEMPERATURE")
        chat_history_dropdown = [f for f in os.listdir(chat_history_folder)]
        vector_dbs = ["General Chat"]
        vector_dbs += [f for f in os.listdir(vector_storage_folder) if f.endswith('.index')]
        return render_template('index.html', 
                           chat_history_dropdown=chat_history_dropdown, 
                           vector_dbs=vector_dbs, 
                           messages=chat_builder.messages[1:],
                           default_db = vector_db_path,
                           temperature = temperature)
    files = request.files.getlist('fileInput')
    doc_name = files[0].filename
    if not files or files[0].filename == '':
        vector_dbs = ["General Chat"]
        vector_dbs += [f for f in os.listdir(vector_storage_folder) if f.endswith('.index')]
        vector_db_path = request.form.get("vectordb")
        temperature = get_config_variable("TEMPERATURE")
        chat_history_dropdown = [f for f in os.listdir(chat_history_folder)]
        return render_template('index.html', 
                           chat_history_dropdown=chat_history_dropdown, 
                           vector_dbs=vector_dbs, 
                           messages=chat_builder.messages[1:],
                           default_db = vector_db_path,
                           temperature = temperature)
    docs = []
    for file in files:
        filename = file.filename
        if allowed_file(filename):
            file_path = os.path.join(app.config['TEMPORARY_FOLDER'], filename)
            file.save(file_path)
            docs.append(file_path)
        else:
            print('invalid file type')
    
    print('checkpoint 3')
    set_vectordb(docs, doc_name)
    print('checkpoint 4')

    for file in os.listdir(app.config['TEMPORARY_FOLDER']):
        file_path = os.path.join(app.config['TEMPORARY_FOLDER'], file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            return f"Error occurred while deleting files: {e}", 500
    vector_storage_folder = "./vector_storage"
    vector_dbs = ["General Chat"]
    vector_dbs += [f for f in os.listdir(vector_storage_folder) if f.endswith('.index')]
    vector_db_path = str(doc_name) + "_cosine.index"
    print(vector_db_path)
    temperature = get_config_variable("TEMPERATURE")
    chat_history_dropdown = [f for f in os.listdir(chat_history_folder)]
    return render_template('index.html', 
                           chat_history_dropdown=chat_history_dropdown, 
                           vector_dbs=vector_dbs, 
                           messages=chat_builder.messages[1:],
                           default_db = vector_db_path,
                           temperature = temperature)


@app.route('/', methods=['GET', 'POST'])
def chatbot():
    temperature = float(os.getenv("TEMPERATURE"))
    print("start")
    messages = []

    if request.method == 'POST':
        vector_db_path = request.form.get("vectordb")
        print("vector_db_path: " + vector_db_path)
        user_input = request.form.get('userInput')
        print("user_input: ", user_input)
        similarity = None
        rag_flag = False
        messages = []
        if vector_db_path != "General Chat":
            print('Not general chat')
            rag_flag = True
            if vector_db_path.endswith('l2.index'):
                print("inside l2")
                similarity = 'euclidean'
                vector_db = vector_db_path.split("_l2")[0]
            else:
                print("inside cosine")
                similarity = "cosine"
                print(vector_db_path.split("_cosine"))
                vector_db = vector_db_path.split("_cosine")[0]
        
        
        if len(chat_builder.messages) > 21:
            print('enter prune')
            chat_builder.keep_last_10()
        # General chat or RAG logic
        if rag_flag:
            print('enter rag')
            #do rag stuff
            question = user_input
            context = ask_question(question, vector_db, similarity)
            list_pattern = r'\d+:\s.*?(?=\s\d+:|$)'
            if context == "":
                chat_builder.set_user(question)
            else:
                context = chat_builder.format_list(context, list_pattern) 
                m_rag = f"# Context:\n{context}\n\n <br><br># Question:\n{question}\n"
                chat_builder.set_user(m_rag)
        else:
            print('enter general chat')
            #do normal chat
            chat_builder.set_user(user_input)
            
        # assistant_response = chat_builder.chat_completion()
        get_latest_sys()
        chat_builder.chat_completion()
    temperature = get_config_variable("TEMPERATURE")
    vector_dbs = ["General Chat"]
    vector_dbs += [f for f in os.listdir(vector_storage_folder) if f.endswith('.index')]
    vector_db_path = request.form.get("vectordb")
    print("vectordb: ", vector_db_path, type(vector_db_path))
    print(vector_dbs[0], type[vector_dbs[0]])
    chat_history_dropdown = [f for f in os.listdir(chat_history_folder)]
    print("chat_builder.messages: ", chat_builder.messages)
    # if sys_message_cookie exist:
        # sys_message = get_config_cookie("SYS_MESSAGE")
        # chat_builder.messages[0] = sys_message
    return render_template('index.html', 
                           chat_history_dropdown=chat_history_dropdown, 
                           vector_dbs=vector_dbs, 
                           messages=chat_builder.messages[1:],
                           default_db = vector_db_path,
                           temperature = temperature)

if __name__ == '__main__':
    # if not os.path.exists(UPLOAD_FOLDER):
    #     os.makedirs(UPLOAD_FOLDER)
    chat_history_dropdown = [f for f in os.listdir(chat_history_folder)]
    app.run(host='127.0.0.1', port=8001, debug=True)
