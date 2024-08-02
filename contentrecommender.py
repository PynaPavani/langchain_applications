#### Generating Prompt templates Efficiently ####
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import streamlit as st


st.title("Content Recommendation Engine")


topic = st.text_input(" Ask the topic name to generate creative content")

if st.button('Submit'):
    prompt = PromptTemplate(
    template=""""\You are a Content Recommendation engine tool who can recommend and generate the content for the given {topic} in a creative way below 200 words in one paragraph.""",
    input_variables=["topic"])

    # format the prompt to add variable values
    prompt_formatted_str: str = prompt.format(
    topic=topic)

    # instantiate the OpenAI intance
    llm = Ollama(model='llama3',temperature=0.6)
    # make a prediction
    prediction = llm.invoke(topic)

    st.title('📝 Recommended Content')

    # print the prediction
    st.write(prediction)