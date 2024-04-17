# Importing necessary libraries

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import StrOutputParser
import streamlit as st
import os
import PyPDF2


# This function creates a prompt template for generating quizzes.
def create_the_quiz_prompt_template():
    # This defines a template string that includes placeholders for the text, number of questions, and quiz type.
    # While making the prompt template, it was necessary to be clear and give examples for accurate results.
    template = """
    Text: {text}
    You are an expert quiz maker. Let's think step by step and create a quiz with {number} {quiz_type} questions about the Text.

    The format of the quiz could be one of the following:
    - Multiple-choice: 
        - Questions:
            <Question1>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
            <Question2>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
            ....
        - Answers:
            <Answer1>: <a|b|c|d>
            <Answer2>: <a|b|c|d>
            ....
            Example:
            - Questions:
            - 1. What is the time complexity of a binary search tree?
                a. O(n)
                b. O(log n)
                c. O(n^2)
                d. O(1)
            - Answers: 
                1. b
    - True-false:
        - Questions:
            <Question1>: <True|False>
            <Question2>: <True|False>
            .....
        - Answers:
            <Answer1>: <True|False>
            <Answer2>: <True|False>
            .....
        Example:
        - Questions:
            - 1. What is a binary search tree?
            - 2. How are binary search trees implemented?
        - Answers:
            - 1. True
            - 2. False
    - One-word:
        - Questions:
            <Question1>: 
            <Question2>:
        - Answers:    
            <Answer1>:
            <Answer2>:
        Example:
            Questions:
            - 1. Example of a linear data structure?
            - 2. What does SQL stand for?

            - Answers: 
                1. Array
                2. Structured Query Language
    """

    # Creating a ChatPromptTemplate object from the template with langchain.prompts.ChatPromptTemplate()
    prompt = ChatPromptTemplate.from_template(template)
    prompt.format(quiz_type="multiple-choice", number=3, text="World War III")
    return prompt


# This function creates a chain for the quiz app using the provided prompt template, language model (llm) (`Which
# will be provided in the main function`). I explicitly used StrOutputParser to split my responses using ".split" for
# displaying questions and answers separately.
def create_quiz_chain(prompt_template, llm, openai_api_key):
    return prompt_template | llm | StrOutputParser()


# This function splits the questions and answers from the quiz response string and returns them separately.
def split_questions_answers(quiz_response):
    questions = quiz_response.split("Answers:")[0]
    answers = quiz_response.split("Answers:")[1]
    return questions, answers


# This function parses the uploaded file (file) and extracts text from it. It uses PyPDF2 to extract text from pdf.
def parse_file(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# main function
def main():

    # Loading the openai_api_key from the .env which is required for creating quiz chain
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    prompt_template = create_the_quiz_prompt_template()
    if openai_api_key != "":
        st.secrets["OPENAI_API_KEY"] = openai_api_key
    else:
        st.error("OpenAI API key error.")

    # Defining the llm and creating chain.
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
    chain = create_quiz_chain(prompt_template, llm, openai_api_key)

    # streamlit UI
    st.title("Quiz Web-App")
    st.write("This app generates a quiz based on the input PDF")
    uploaded_file = st.file_uploader("Upload a pdf file (keep it under 5 pages)", type="pdf")
    number = st.number_input("Enter the number of questions", min_value=1, max_value=10, value=3)
    quiz_type = st.selectbox("Select the quiz type", ["multiple-choice", "true-false", "One-word"])

    # For Generating quiz parsing the pdf file into text and invoking the chain. Splitting the questions and answers
    # thereby returning questions.
    if st.button("Generate Quiz"):
        text = parse_file(uploaded_file)
        quiz_response = chain.invoke({"quiz_type": quiz_type, "number": number, "text": text})
        st.write("Quiz Generated!")
        questions, answers = split_questions_answers(quiz_response)
        st.session_state.answers = answers
        st.session_state.questions = questions
        st.write(questions)

    # Returning the answer split earlier if the "Show Answers" button is pressed .
    if st.button("Show Answers"):
        st.markdown(st.session_state.questions)
        st.write("----")
        st.markdown(st.session_state.answers)


# Main function called.
if __name__ == "__main__":
    main()
