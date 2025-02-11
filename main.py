import plotly.graph_objects as go
import pandas as pd
import streamlit as st
pd.options.display.float_format = '{:.0f}'.format
import helper
from helper import sherlock
import time
import streamlit as st
import streamlit_authenticator as stauth
import json

config = json.load(open("creds.json",'rb'))
st.set_page_config(page_title="QueryBot", layout='wide')

# Authentication setup
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login interface
#col1, col2 = st.columns([1,13])
#with col1:
#    st.image('images/chat-xxl.png', use_column_width="auto")
#with col2:
#    st.markdown("<h1 style='text-align: left;'>Data Companion</h1>", unsafe_allow_html=True)
authenticator.login('main')

        
if st.session_state['authentication_status']:
    st.sidebar.title("\n")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.image("images/mead-johnson-logo.jpg", use_column_width=True)  # Replace with your image path

    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                width: 20% !important; # Set the width to your desired value
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    #st.markdown("""
    #        <style> 
    #        .st-emotion-cache-pgf13w {margin-top: -170px;}
    #        .st-emotion-cache-6dnr6u{margin-top: -115px;}
    #        .st-emotion-cache-1v0mbdj{margin-top:-140px;}
    #        .st-emotion-cache-bm2z3a{margin-left:-40px;}
    #        .st-emotion-cache-pgf13w h1 {margin-bottom: -10px;}
    #        .st-emotion-cache-1t8h08j h2 {margin-top: -10px;}
    #        .st-emotion-cache-m78myu {margin-top: -150px;}
    #        </style>
    #        """, unsafe_allow_html=True)

    st.markdown("""
            <style>
                    /* Apply color to all markdown text */
                    .stMarkdown p {
                        color: #00008B;
                    }
                    .stMarkdown h1 {
                        color: #00008B;
                    }
                    .stMarkdown li {
                        color: #00008B;
                    }
                    .st-emotion-cache-1rsyhoq h2 {
                        color: #00008B;
                    }
                    .st-emotion-cache-1ny7cjd p {
                        color: #00008Bt;
                        }
                    .stRadio p {
                    color: #00008B;
                    }
                    .st-emotion-cache-6nrhu6 {color: #00008B;}
                    .stLinkButton p {color: #00008B;}
            </style>
            """, unsafe_allow_html=True)


    st.markdown("""
                <style>
                button[kind="secondary"]
                {
                    margin-left:-5px;
                    margin-right:-5px;
                    background-color: white;
                }
                    button[kind="secondary"] p {
                    font-size: 14px;
                    color:  #00008B;
                }
                </style>
                """, unsafe_allow_html=True)

    st.markdown("""
                <style>
                button[kind="primary"]{
                    background-color: #00008B;
                }
                button[kind="primary"] p {
                    color:  white;
                }
                </style>
                """, unsafe_allow_html=True)

    # CSS for custom styling
    st.markdown("""
        <style> 
        .stChatInput{  
            border: 2px solid #00008B; !important;

        }  
        """, unsafe_allow_html=True
    )

    authenticator.logout('Logout', 'sidebar')  # Add logout button to the sidebar

    st.markdown(
        """<style>
        div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {font-size: 20px;
    }
        </style>
        """, unsafe_allow_html=True)
    sherlock()

# If login is unsuccessful
elif st.session_state['authentication_status'] == False:
    st.error('Username/password is incorrect')

# If no authentication action yet
elif st.session_state['authentication_status'] == None:
    st.warning('Please enter your username and password')
