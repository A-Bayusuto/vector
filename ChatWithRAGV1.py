from ChatBuilder import *
from RAG_Azure import *
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

# Load environment variables
load_dotenv(override=True)
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Azure embedding configuration
azure_embed_config = {
    "openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "embedding_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    "embedding_name": os.getenv("AZURE_OPENAI_EMBEDDING_NAME"),
    "api_key": os.getenv("AZURE_OPENAI_API_KEY")
}

# Azure LLM configuration
azure_llm_config = {
    "openai_api_version": os.getenv("OPENAI_API_VERSION"),
    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.getenv("AZURE_OPENAI_API_KEY")
}

def ask_for_files():
    # Initialize the GUI window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.lift()
    root.attributes("-topmost", True)
    
    # Ask the user to select multiple files
    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        # filetypes=[("PDF Files", "*.pdf")]  # make sure its pdf
        filetypes = [("All Files", "*.*"), 
                    ("Text Files", "*.txt"), 
                    ("PDF Files", "*.pdf"), 
                    ("CSV Files", "*.csv")]
        )

    if file_paths:
        print("Selected Files:")
        for file_path in file_paths:
            print(file_path)
    else:
        print("No files selected.")
    return list(file_paths)


# documents is list [], vectordb is str local db name
def set_vectordb(documents, vectordb="vector"):
    print('vectordb: ', vectordb)
    rag = RAG(azure_embed_config, azure_llm_config)
    rag.document_processor(documents)
    print("post doc processor")
    rag.set_vector(vectordb)
    print(rag.df)
    rag.generate_vectordb()

def ask_question(question, vectordb="vector", vtype="cosine"):
    rag = RAG(azure_embed_config, azure_llm_config)
    rag.set_vector(vectordb)
    question = question
    if vtype == "euclidean": 
        output = rag.search_vector_faiss(question)
    else:
        output = rag.search_vector_faiss_cosine(question)
    return output

### Uncomment below to see try flow. Need to add test.pdf to give contextual info
# # flow example from RAG class
# rag = RAG(azure_embed_config, azure_llm_config)
# documents = [r"C:\Users\LENOVO\Documents\ABM\AG\test.pdf"]
# documents = [r"C:\Users\LENOVO\Documents\ABM\AG\test.pdf", r"C:\Users\LENOVO\Documents\ABM\Mar-Timesheet_Alexander Bayusuto.xlsx"]
# rag.document_processor(documents)
# rag.set_vector("test3")
# rag.generate_vectordb()
# question = "who was the last South Korean PM impeached?"
# context1 = rag.search_docs(question)
# context2 = rag.search_vector_faiss(question)
# context3 = rag.search_vector_faiss_cosine(question)

### Uncomment below to see try flow. Need to add test.pdf to give contextual info
# # flow example to limit Azure API calls for embedding
# rag = RAG(azure_embed_config, azure_llm_config)
# documents = [r"C:\Users\LENOVO\Documents\ABM\AG\test.pdf"]
# set_vectordb(documents, vectordb="vector_test")
# # at this point vectordb named vector(default name) is created, no need to keep calling Azure embed part
# question = "who was the last South Korean PM impeached?"
# ask_question(question, vectordb="vector_test", vtype="euclidean")

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

chat_builder.set_deployment(deployment)
chat_builder.set_temperature(temperature)
chat_builder.set_system(system_role)
chat_builder.messages.append(chat_builder.sys_content)

vector_db_path = os.getenv("VECTOR_DB")
