import warnings
warnings.filterwarnings(action='ignore')
from time import sleep
import tiktoken
from langchain.text_splitter import TokenTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import LlamaCppEmbeddings
from llama_cpp import Llama
import fitz
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.document import Document
from rich.console import Console
from langchain_huggingface import HuggingFaceEmbeddings

class ChatWithDocs:
    def __init__(self, emb_path, model_paths, console_width=90):
        self.console = Console(width=console_width)
        self.encoding = tiktoken.get_encoding("r50k_base")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.models = {
            'qwen05b': Llama(
                model_path=model_paths['qwen05b'],
                n_gpu_layers=0,
                temperature=1.1,
                top_p = 0.5,
                n_ctx=8192,
                max_tokens=600,
                repeat_penalty=1.7,
                stop=["<|im_end|>","Instruction:","### Instruction:","###<user>","</user>"],
                verbose=True,
            )
        }

    def load_pdf(self, file_path):
        pdf_document = fitz.open(file_path)
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text

    def process_text(self, text):
        document = Document(page_content=text)
        text_splitter = TokenTextSplitter(chunk_size=250, chunk_overlap=50)
        documents = text_splitter.split_documents([document])
        return documents

    def create_vector_store(self, texts):
        vectorstore = FAISS.from_documents(texts, self.embeddings)
        return vectorstore

    def request_model(self, question, vectorstore, hits, maxtokens, model_name):
        model = self.models[model_name]
        retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": hits})
        docs = retriever.invoke(question)
        context = ''.join([doc.page_content for doc in docs])
        contesto = context.replace('\n\n', '')
        query = question

        template = f"""Responda la pregunta basándose únicamente en el siguiente contexto:
        [contexto]
        {contesto}
        [fin del contexto]
        Question: {query}
        """

        messages = [
            {"role": "system", "content": "Eres un modelo de lenguaje capacitado para responder preguntas basadas únicamente en el texto proporcionado."},
            {"role": "user", "content": template},
        ]

        with self.console.status("...", spinner="dots12"):
            output = model.create_chat_completion(
                messages=messages,
                max_tokens=maxtokens,
                stop=["</s>","[/INST]","/INST",'<|eot_id|>','<|end|>'],
                temperature = 0.2,
                repeat_penalty = 1.1)

        response = output["choices"][0]["message"]["content"]
        return response
