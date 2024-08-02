#### Generating Prompt templates Efficiently ####
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import streamlit as st


st.title("Language Translation Tool Using LLMs")


query = st.text_input(" Ask query to translate in your preferred language")
if st.button('Submit'):
    prompt = PromptTemplate(
    template=""""\You are a Language translation tool which can translate the given {question} into targeted languag as a response.""",
    input_variables=["question"])

    # format the prompt to add variable values
    prompt_formatted_str: str = prompt.format(
    question=query)

    # instantiate the OpenAI intance
    llm = Ollama(model='llama3',temperature=0.6)

    # make a prediction
    prediction = llm.invoke(query)

    # print the prediction
    st.write(prediction)