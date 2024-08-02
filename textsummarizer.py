import streamlit as st
from langchain.text_splitter import CharacterTextSplitter # used for splitter the text into smalle chunks
from langchain.docstore.document import Document # convert the chunks in document format
from langchain.chains.summarize import load_summarize_chain # connect prompt and llm model
from langchain.prompts import PromptTemplate # for creating prompt 
from langchain_community.llms import Ollama 
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


# this function is responsible for splitting the data into smaller chunks and convert the data in document format
def chunks_and_document(txt):
    
    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(txt) # split the text into smaller chunks
    docs = [Document(page_content=t) for t in texts]
    
    return docs

# Loading the Llama 2's LLM
def load_llm():

    # loading the LLM model
    # Their are multiple models available just replace it in place of model and try it.
    llm = Ollama(
        model="llama2",
        temperature = 0.6)
        
    return llm

# this functions is used for applying the llm model with our document 
def chains_and_response(docs):
    
    llm = load_llm()
    chain = load_summarize_chain(llm,chain_type='map_reduce') 
    return chain.run(docs)

# Page title
st.set_page_config(page_title='🦜🔗 Text Summarization App')
st.title('🦜🔗 Text Summarization App')

# Text input
txt_input = st.text_area('Enter your text', '', height=200)

# Form to accept user's text input for summarization
result = []
with st.form('summarize_form', clear_on_submit=True):
    submitted = st.form_submit_button('Submit')
    if submitted:
        with st.spinner('Summarizing...'):
            docs = chunks_and_document(txt_input)
            response = chains_and_response(docs)
            result.append(response)

if len(result):
    st.title('📝 Summarization Result')
    st.info(response)