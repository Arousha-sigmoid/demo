import time
import streamlit as st
import json
import helper_functions
states = json.load(open("data/state_code.json", 'rb'))
qna = json.load(open("qna.json", 'rb'))
query_lis = [x['query'] for x in qna]


global count 
count= 0

def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.15)

def write_text(text, streaming):
    # Inject custom CSS to set the text color of st.write to black
    if streaming:
        for line in text.split("\n"):
            st.write_stream(response_generator(line.strip()))
            time.sleep(0.1)
    else:
        st.write(text)


def display_gpt_answers(response, user, streaming=True):
    global count
    if user == "assistant":
        with st.chat_message("assistant"):
            # Display any observations/responses
            if response['reformulated_question']!='':
                write_text(f"I understood your question as: '{response['reformulated_question']}'", streaming)
            # For DataFrames
            if len(response['query_result'])>0:
                global dataframe 
                dataframe = response['query_result'].copy()
                st.dataframe(globals()['dataframe'], key=count)
                count = count + 1
            write_text(response['text'], streaming)
            # For Plots
            if response['plot_code_final']!='':
                #print(response['plot_code_final'])
                try:
                    exec(response['plot_code_final'],globals())
                    st.plotly_chart(globals()['fig'], key=count)
                    count = count + 1
                except:
                    print('plot generation failed')
            # For Links
            if response['main_tab']!='':
                st.write(f"**The information is also available in the 'Sherlock' Dashboard, in the '{response['main_tab']} Tab'.**")
                st.write(f"Select these filters:\n{response['filters']}")
                st.link_button(label="Link To Dashboard", url = '')
    elif user=='user':
        with st.chat_message("user"):
            st.markdown(response)
    

def display_content(response, user, streaming = True):
    global count
    if user == "assistant":
        print(response)
        with st.chat_message("assistant"):
            # Display any observations/responses
            write_text(response['answer'], streaming)
            # For DataFrames
            if response.get('dataframe', ''):
                dataframe = response['dataframe']
                if dataframe != []:
                    for df in dataframe:
                        if df.get('text1', '') != '':
                            write_text(df['text1'],streaming)
                        if df.get('code_path', '') !='':
                            with open(df['code_path'], 'r') as f:
                                code = f.read()
                            exec(code, globals())
                            if streaming:
                                time.sleep(2)
                                st.dataframe(globals()['xx'], key=count)
                                count = count + 1
                            else:
                                st.dataframe(globals()['xx'], key=count)
                                count = count + 1
                        if df.get('text2','') != '':
                            #st.write_stream(response_generator(topic.get('text2')))
                            write_text(df['text2'],streaming)
            # For Plots
            if response.get('graphs',None):
                graphs = response['graphs']
                if graphs != []:
                    for topic in graphs:
                        if topic.get('text1','') != '':
                            write_text(topic['text1'],streaming)
                            time.sleep(0.1)
                        if topic.get('code_path','') != '':
                            with open(topic['code_path'],'r') as f:
                                code = f.read()
                            exec(code,globals())
                            time.sleep(0.3)
                            if streaming:
                                time.sleep(2)
                                st.plotly_chart(globals()['fig'], key=count)
                                count = count + 1
                            else:
                                st.plotly_chart(globals()['fig'], key=count)
                                count = count + 1
                        if topic.get('path','') != '':
                            st.image(topic['path'])
                            time.sleep(0.1)
                        if topic.get('text2','') != '':
                            #st.write_stream(response_generator(topic.get('text2')))
                            write_text(topic['text2'],streaming)
            # For Links
            if response.get('link','') != '':
                tab_name = response.get('tab_name', '')
                st.write(f"**The information is also available in the 'Sherlock' Dashboard, in the {tab_name}**")
                st.link_button(label="Link To Dashboard", url = response['link'])
    elif user=='user':
        with st.chat_message("user"):
            st.markdown(response)



def push_button(label, actual):
    for message in st.session_state.messages:
            try:
                if 'code_path' in message['content'].keys():
                    display_content(message["content"],message["role"], streaming=False)
                elif 'main_tab' in message['content'].keys():
                    display_gpt_answers(message["content"],message["role"], streaming=False)
                else:
                    display_content(message["content"],message["role"], streaming=False)
            except:
                display_content(message["content"],message["role"], streaming=False)
    # Display user message
    with st.chat_message("user"):
        st.markdown(label)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": label})
    # Getting Answers
    idx = query_lis.index(actual)
    response = qna[idx]['response']
    # Display Assistant Response
    display_content(response,"assistant")
    # Add response message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    #st.session_state.messages = []

def main_code(prompt):
    response = {}
    x = helper_functions.main(prompt)
    try:
        reformulated_question, sql_query, query_result, plot_code_final, main_tab, filts, text_answer = x
        response['reformulated_question'] = reformulated_question
        response['sql_query'] = sql_query
        response['query_result'] = query_result
        response['plot_code_final'] = plot_code_final
        response['main_tab'] = main_tab
        response['filters'] = filts
        response['text'] = text_answer
    except: 
        response = {}
    # print(reformulated_question, sql_query, query_result, plot_code_final, main_tab, filts, text_answer)
    return response

def sherlock():
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "disabled" not in st.session_state:
        st.session_state.disabled = False

    col1, col2, col3 = st.columns([2,13,3])
    with col1:
        #st.markdown('\n')
        st.image('images/hosp_2.png', use_column_width='auto')
    with col2:
        st.markdown('\n')
        st.markdown("# Sherlock Agent\nBuilt on top of the Sherlock Report & Gold Layer Tables")

    with col3:
        #st.markdown('\n')
        if st.button("New Chat", help="Click to start a new chat", type='primary'):
            if "messages" in st.session_state:
                st.session_state.messages = []
            st.rerun()

    prompt = st.chat_input("Enter Your Query Here...", disabled = st.session_state.disabled)
    if prompt:
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            try:
                if 'code_path' in message['content'].keys():
                    display_content(message["content"],message["role"], streaming=False)
                elif 'main_tab' in message['content'].keys():
                    display_gpt_answers(message["content"],message["role"], streaming=False)
                else:
                    display_content(message["content"],message["role"], streaming=False)
            except:
                display_content(message["content"],message["role"], streaming=False)


        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Getting Answers
        response = {}
        response = main_code(prompt)
        if response == {}:
            response["answer"] = "I don't have exposure to enough data to answer this question."
        # Display Assistant Response
        if 'answer' in response.keys():
            display_content(response, 'assistant')
        else:
            display_gpt_answers(response,"assistant")
        # Add response message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    st.sidebar.markdown('## Most Popular Questions this Week')

    que1 = 'Monthly rolling trend of hospital contracts won by MJN'
    if st.sidebar.button(que1):
        #st.session_state.messages = []
        prompt = 'Monthly rolling trend of hospital contracts won by MJN'
        push_button(que1, prompt)

    que2 = "How many births has MJN gained since 2022?"
    if st.sidebar.button(que2):
        #st.session_state.messages = []
        prompt = 'How many births has MJN gained since 2022?'
        push_button(que2, prompt)

    que3 = "State-wise hospital contract performance?"
    if st.sidebar.button(que3):
        #st.session_state.messages = []
        prompt = 'State-wise hospital contract performance?'
        push_button(que3, prompt)

    que4 = "Which retailers are having the best YOY growth for POS Sales?"
    if st.sidebar.button(que4):
        #st.session_state.messages = []
        prompt = 'Which retailers are having the best YOY growth for POS Sales?'
        push_button(que4, prompt)

    que5 = "Compare monthly sales trends across top brands"
    if st.sidebar.button(que5):
        #st.session_state.messages = []
        prompt = 'Compare monthly sales trends across top brands'
        push_button(que5, prompt)



    