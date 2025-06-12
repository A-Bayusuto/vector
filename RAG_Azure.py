import os
import re
import requests
import sys
from num2words import num2words
import json
import pandas as pd
import numpy as np
import tiktoken
from openai import AzureOpenAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import faiss
from app import app


class RAG:
    chunk_size = int(os.getenv("CHUNK_SIZE"))
    csv_delimiter = os.getenv("CSV_DELIMITER")
    distance_threshold = float(os.getenv("DISTANCE_THRESHOLD"))

    def __init__(self, azure_embed_config, azure_llm_config):
        self.azure_embed_config = azure_embed_config
        self.azure_llm_config = azure_llm_config
        self.client = AzureOpenAI(
            api_key = self.azure_embed_config["api_key"],  
            api_version = self.azure_embed_config['openai_api_version'],
            azure_endpoint = self.azure_embed_config['azure_endpoint'] 
            )
        self.df = None
        self.metadata = None
        self.vector = "vectordb"

    def set_vector(self, db_name):
        self.vector = db_name

    def load_metadata(self):
        # Load metadata from file
        print("load meta: ", self.vector)
        with open(os.path.join("vector_storage", f"{self.vector}_metadata.json"), "r", encoding="utf-8") as f:
            import json
            self.metadata = json.load(f)


    def normalize_text(self, s, sep_token = " \n "):
        pd.options.mode.chained_assignment = None
        s = re.sub(r'\s+',  ' ', s).strip()
        s = re.sub(r". ,","",s)
        # remove all instances of multiple spaces
        s = s.replace("..",".")
        s = s.replace(". .",".")
        s = s.replace("\n", "\n\n")
        # s = s.replace("\n", sep_token) # Replace newline with sep_token
        s = s.strip()
        return s
    
    def generate_embeddings(self, text, model): # model = "deployment_name"
        return self.client.embeddings.create(input = [text], model=model).data[0].embedding
    
    def detect_delimiter(self, doc):
        with open(doc, 'r', encoding='utf-8') as file:
            first_line = file.readline()

        semicolon_count = first_line.count(';')
        comma_count = first_line.count(',')

        delimiter = ';' if semicolon_count > comma_count else ','
        return delimiter

    def document_processor(self, documents):
        all_chunks = []
        for doc in documents:
            if doc.endswith('.pdf'):
                try:
                    reader = PdfReader(doc)
                    for page in reader.pages:
                        text = page.extract_text()
                        print("TEXT:")
                        print(text)
                        if text:
                            chunks = text.split("\n\n")  # Split by double newlines
                            all_chunks.extend(chunks)
                            
                            # chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
                            # all_chunks.extend(chunks)
                except Exception as e:
                    print(f"Error processing PDF file {doc}: {e}")
                    continue

            elif doc.endswith('.csv'):
                delimiter = self.detect_delimiter(doc)
                print("delimiter: ", delimiter)
                try:
                    csv_df = pd.read_csv(doc, delimiter=delimiter)
                except Exception as e:
                    print(f"Error processing CSV file {doc} with {delimiter} delimiter: {e}")
                
                print(csv_df.head())
                column_names = list(csv_df.columns)
                print(column_names)
                print('55555555555555555555555555555555555555')

                for index, row in csv_df.iterrows():
                    curr_row = f"Row {index} - "
                    for i in range(len(column_names)):
                        print("column_names: ", column_names[i])
                        print("row value: ", row[column_names[i]])
                        if i < len(column_names) - 1:
                            curr_row += f"{column_names[i]}: {row[column_names[i]]} "
                        else:
                            curr_row += f"{column_names[i]}: {row[column_names[i]]} | \n <br>"
                    all_chunks.append(curr_row)
    
        df = pd.DataFrame(all_chunks, columns=["chunks"])
        # print(df)
        df['text']= df["chunks"].apply(lambda x : self.normalize_text(str(x)))
        tokenizer = tiktoken.get_encoding("cl100k_base")
        df['n_tokens'] = df["text"].apply(lambda x: len(tokenizer.encode(x)))
        df = df[df["n_tokens"]<8192]
        self.df = df

    def generate_vectordb(self):
        self.metadata = self.df["text"].tolist()

        # Generate embeddings for all text in the DataFrame
        self.df['ada_v2'] = self.df["text"].apply(lambda x: self.generate_embeddings(x, model=self.azure_embed_config['embedding_deployment']))
        embeddings_array = np.vstack(self.df["ada_v2"].values)
        embedding_dim = embeddings_array.shape[1]

        # Create and save the L2 index
        l2_index = faiss.IndexFlatL2(embedding_dim)  # L2 (Euclidean distance)
        l2_index.add(embeddings_array)
        os.makedirs("vector_storage", exist_ok=True)
        faiss.write_index(l2_index, os.path.join(app.config['UPLOAD_FOLDER'], f"{self.vector}_l2.index"))  # Save the L2 index

        # Normalize embeddings for Cosine Similarity
        normalized_embeddings_array = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)

        # Create and save the Cosine Similarity index
        cosine_index = faiss.IndexFlatIP(embedding_dim)  # Inner Product (approximates Cosine Similarity)
        cosine_index.add(normalized_embeddings_array)
        faiss.write_index(cosine_index, os.path.join(app.config['UPLOAD_FOLDER'], f"{self.vector}_cosine.index"))  # Save the Cosine Similarity index

        with open(os.path.join(app.config['UPLOAD_FOLDER'], f"{self.vector}_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(self.metadata, f)

        # print(f"Generated and saved indices: {self.vector}_l2.index (L2), {self.vector}_cosine.index (Cosine Similarity)")

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def search_docs(self, user_query, top_n=4, to_print=True):
        embedding = self.generate_embeddings(user_query, model= self.azure_embed_config['embedding_deployment']) # model should be set to the deployment name you chose when you deployed the text-embedding-ada-002 (Version 2) model
        # print('=========================')
        # print(self.df)
        # print(embedding)
        self.df["similarities"] = self.df["ada_v2"].apply(lambda x: self.cosine_similarity(x, embedding))

        res = (
            self.df.sort_values("similarities", ascending=False)
            .head(top_n)
        )
        # if to_print:
        #     print(res)
        context = ""
        index = 1
        for text in res["chunks"]:
            context += f"{index}:  {text} \n"
            index += 1
        return context

    def search_vector_faiss(self, question, top_n=10, distance_threshold=distance_threshold):
        index = faiss.read_index(os.path.join(app.config['UPLOAD_FOLDER'], f"{self.vector}_l2.index"))
        self.load_metadata()
        user_embedding = np.array(self.generate_embeddings(question, model=self.azure_embed_config['embedding_deployment'])).reshape(1, -1)
        distances, indices = index.search(user_embedding, top_n)
        context = ""
        # print("Top Results:")
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if distance > distance_threshold:
                text = self.metadata[idx]  # Access text using index from metadata list
                # print(f"{i+1}: (Distance: {distance}) - {text}")
                context += f"{i+1}: (Similarity: {distance}) - {text} \n"
        return context
    
    def search_vector_faiss_cosine(self, question, top_n=10, distance_threshold=distance_threshold):
        index = faiss.read_index(os.path.join(app.config['UPLOAD_FOLDER'], f"{self.vector}_cosine.index"))
        self.load_metadata()
        user_embedding = np.array(self.generate_embeddings(question, model=self.azure_embed_config['embedding_deployment'])).reshape(1, -1)
        normalized_user_embedding = user_embedding / np.linalg.norm(user_embedding, axis=1, keepdims=True)
        distances, indices = index.search(normalized_user_embedding, top_n)
        context = ""
        # print("Top Results:")
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if distance > distance_threshold:
                text = self.metadata[idx]  # Access text using index from metadata list
                # print(f"{i+1}: (Cosine Similarity: {distance}) - {text}")
                context += f"{i+1}: (Similarity: {distance}) - {text} \n"
        return context




        


    


