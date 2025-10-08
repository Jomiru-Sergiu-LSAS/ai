import os
import random
import streamlit as st
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_chroma import Chroma

from operator import itemgetter

st.set_page_config(page_title="UMABot (Support)", page_icon="🌐")

st.markdown(
    """
<style>

div.stButton > button, button[kind="primary"], button[kind="secondary"], .stFormSubmitButton > button {
    background-color: #4a90e2 !important;
    background: #4a90e2 !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3) !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover, button[kind="primary"]:hover, button[kind="secondary"]:hover, .stFormSubmitButton > button:hover {
    background-color: #3a7bc8 !important;
    background: #3a7bc8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4) !important;
}

header {visibility: hidden !important;}
.streamlit-footer {display: none !important;}
.st-emotion-cache-uf99v8 {display: none !important;}

/* Hide Streamlit branding and toolbar - all variations */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important; display: none !important;}
.stApp > header {display: none !important;}
footer {visibility: hidden !important;}
footer::after {display: none !important;}
.stDeployButton {display: none !important;}
.viewerBadge_container__1QSob {display: none !important;}
.styles_viewerBadge__1yB5_ {display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
[data-testid="manage-app"] {display: none !important;}
[data-testid="stHeader"] {display: none !important;}
.css-18e3th9 {padding-top: 0 !important;}
.css-1d391kg {padding-top: 0 !important;}
.st-emotion-cache-18ni7ap {display: none !important;}
.st-emotion-cache-vk3wp9 {display: none !important;}

/* Hide "Made with Streamlit" and similar badges */
a[href*="streamlit.io"] {display: none !important;}
[class*="viewerBadge"] {display: none !important;}
[class*="ViewerBadge"] {display: none !important;}
div[data-testid="stBottom"] {display: none !important;}
.stApp > footer {display: none !important;}
.stApp [data-testid="stBottomBlockContainer"] {display: none !important;}

/* Remove any white frames/borders */
.main .block-container {
    padding-top: 1rem !important;
}
section[data-testid="stSidebar"] {display: none !important;}

/* Add spacer at bottom to prevent content scrolling under overlay */
.main .block-container::after {
    content: "";
    display: block;
    height: 60px;
    width: 100%;
}

/* Textarea styling to match background */
textarea {
    background-color: #2a2b30 !important;
    color: #fff !important;
    border: 0.5px solid #4a4a4a !important;
}

textarea:focus {
    background-color: #2a2b30 !important;
    border-color: #6bb6ff !important;
}

.stTextArea textarea {
    background-color: #2a2b30 !important;
    color: #fff !important;
}

</style>

<script>
// Force remove Streamlit branding after page load
window.addEventListener('load', function() {
    setTimeout(function() {
        // Remove all header elements
        document.querySelectorAll('header').forEach(el => el.remove());
        document.querySelectorAll('[data-testid="stHeader"]').forEach(el => el.remove());

        // Remove all footer elements
        document.querySelectorAll('footer').forEach(el => el.remove());

        // Remove viewer badge
        document.querySelectorAll('[class*="viewerBadge"]').forEach(el => el.remove());
        document.querySelectorAll('[class*="ViewerBadge"]').forEach(el => el.remove());

        // Remove links to streamlit.io
        document.querySelectorAll('a[href*="streamlit.io"]').forEach(el => el.remove());

        // Remove toolbar
        document.querySelectorAll('[data-testid="stToolbar"]').forEach(el => el.remove());
        document.querySelectorAll('[data-testid="stDecoration"]').forEach(el => el.remove());
        document.querySelectorAll('[data-testid="stStatusWidget"]').forEach(el => el.remove());
        document.querySelectorAll('[data-testid="manage-app"]').forEach(el => el.remove());
        document.querySelectorAll('[data-testid="stBottom"]').forEach(el => el.remove());
        document.querySelectorAll('#MainMenu').forEach(el => el.remove());
    }, 100);
});
</script>

<style>
.st-emotion-cache-e1lln2w80 {
    border: 0.5px solid #4a4a4a;
    background-color: #2a2b30;
    color: #FFF
}
.st-emotion-cache-ktz07o {
    border: 0.5px solid #4a4a4a;
    background-color: #2a2b30;
    color: #FFF
}
.stApp {
    color: #fff;
    background-color: #2a2b30;
}
.st-bc {
    border: 0.5px solid #4a4a4a;
    background-color: #2a2b30;
    color: #FFF
}
.st-bb {
    border: 0.5px solid #4a4a4a;
    background-color: #2a2b30;
    color: #FFF
}
.st-at {
    border: 0.5px solid #4a4a4a;
    background-color: #2a2b30;
    color: #FFF
}
.row-widget stButton {
    border: 1px solid #4a4a4a;
    background-color: #2a2b30;
    color: #FFF
}
.reportview-container .main footer, .reportview-container .main footer a {
    color: #0c0080;
    background-color: #2a2b30;
}
.st {
    background-color: #2a2b30;
background-image: none;
color: #ffffff
}

body {

    background-color: #2a2b30;
}

</style>
""",
    unsafe_allow_html=True,
)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]

def generate_embeddings():
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    pcstore = Chroma(persist_directory="./support-content-db-new", embedding_function=embeddings)
    return pcstore.as_retriever(search_kwargs={"k":20})

def setup_chain():
    model = ChatOpenAI(temperature=0 , openai_api_key=OPENAI_API_KEY, model="gpt-4o", streaming=True)
    parser = StrOutputParser()
    support_prompt_template = """
                              You are an AI-powered customer support bot for the Systems Tool Kit (STK) software. Your primary goal is to assist users with their STK-related questions, issues, and concerns based on the provided context.

                              When a user presents a query, follow these steps:

                              1. Carefully analyze the user's question or issue in the context of the provided information.

                              2. Provide clear, concise, and relevant answers to the user's questions, drawing upon the given context.

                              3. If the user's query cannot be adequately answered using the provided context, ask for clarification or additional details to better understand their needs.

                              4. When appropriate and supported by the context, guide the user through step-by-step instructions to resolve their issues or achieve their desired outcomes within STK.

                              5. If the user's query is beyond the scope of the provided context or requires further assistance, inform them that additional information or support may be necessary.

                              Remember to rely solely on the provided context to offer accurate and helpful responses. If the context is insufficient to address the user's query, communicate this clearly and politely.

                              Context: {context}

                              Query: {question}
                              """
    
    prompt = ChatPromptTemplate.from_template(support_prompt_template)
    retriever = generate_embeddings()
    setup = RunnableParallel(context=retriever, question=RunnablePassthrough())
    chain = setup | prompt | model | parser
    
    return chain, setup

st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px; margin-top: -86px;">
        <div style="display: flex; justify-content: center; margin-bottom: 16px;">
            <svg width="48" height="48" fill="#6bb6ff" viewBox="0 0 24 24">
                <path d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5M12,4.15L6.04,7.5L12,10.85L17.96,7.5L12,4.15M5,15.91L11,19.29V12.58L5,9.21V15.91M19,15.91V9.21L13,12.58V19.29L19,15.91Z"/>
            </svg>
        </div>
        <h2 style="margin: 0; color: #f3f3f7; font-size: 1.8em; font-weight: 600;">LSAS AI Help Agent</h2>
    </div>
    """,
    unsafe_allow_html=True
)

random_text = random.choice([
    "How do I create a new scenario in STK?",
    "What are the steps to add a satellite to my scenario?",
    "How can I visualize the orbit of a satellite in STK?",
    "How do I set the time period for my scenario?",
    "What is the process to add a ground station in STK?",
    "How can I generate a simple access report between a satellite and a ground station?",
    "How do I save and load scenarios in STK?",
    "What are the basic visualization tools available in STK?",
    "How can I add terrain data to my scenario?",
    "How do I use the 3D Object Editing capability in STK?",
    "How do I use the Coverage tool to analyze satellite coverage?",
    "What are the steps to create a chain of satellites in STK?",
    "How can I model a satellite constellation in STK?",
    "How do I use the Analyzer tool for trade studies?",
    "How can I simulate a satellite maneuver in STK?",
    "What is the process to import external data into STK?",
    "How do I use the Volumetrics tool to visualize RF coverage?",
    "How can I create a custom report in STK?",
    "How do I use the Globe Manager to manage terrain and imagery data?",
    "How can I model a communication link between two satellites?",
    "How do I use the Astrogator tool for advanced satellite maneuver planning?",
    "What are the steps to perform a conjunction analysis in STK?",
    "How can I use the Radar tool to model radar systems?",
    "How do I use the EOIR tool to simulate electro-optical and infrared sensors?",
    "How can I perform a detailed mission analysis using the Mission Planning tool?",
    "How do I use the Scheduler tool to solve scheduling problems?",
    "How can I model a hypersonic vehicle in STK?",
    "How do I use the SEET tool for space environment effects analysis?",
    "How can I integrate STK with external software using Connect commands?",
    "How do I use the Spectrum Analyzer tool for electromagnetic spectrum analysis?",
    "How do I use the SatPro tool for satellite design?",
    "What are the steps to create a large satellite constellation in STK?",
    "How can I perform a coverage analysis for a global network of satellites?",
    "How do I use the Optimizer tool for satellite constellation optimization?",
    "How can I model the power generation of solar panels on a satellite?",
    "How do I use the Constellation Design tool for advanced satellite constellation planning?",
    "How can I perform a detailed analysis of satellite communication links?",
    "How do I use the Volumetrics tool for RF coverage visualization in space?",
    "How can I model satellite maneuvers using the Astrogator tool?",
    "How do I use the Analyzer tool for satellite constellation trade studies?",
    "How do I use the Aviator tool for aircraft mission planning?",
    "What are the steps to model an aircraft refueling mission in STK?",
    "How can I simulate a helicopter test flight in mountainous terrain?",
    "How do I use the Terrain Following tool for aircraft missions?",
    "How can I model the effect of atmospheric phenomena on an airborne mission?",
    "How do I use the Radar tool to model radar tracking of an aircraft?",
    "How can I perform a detailed analysis of aircraft communication links?",
    "How do I use the EOIR tool to simulate aircraft sensors?",
    "How can I model a UAV test to determine radar tracking and jamming?",
    "How do I use the Analyzer tool for aircraft mission trade studies?",
    "How do I create a basic satellite design using SatPro?",
    "What are the steps to model a satellite constellation using SatPro?",
    "How can I perform a coverage analysis for a satellite constellation?",
    "How do I use the Constellation Design tool in SatPro?",
    "How can I model satellite maneuvers using SatPro?",
    "How do I use the Optimizer tool for satellite constellation optimization in SatPro?",
    "How can I perform a detailed analysis of satellite communication links using SatPro?",
    "How do I use the Volumetrics tool for RF coverage visualization in SatPro?",
    "How can I model the power generation of solar panels on a satellite using SatPro?",
    "How do I use the Analyzer tool for satellite constellation trade studies in SatPro?",
    "How do I access the Getting Started with Scheduler tutorial in STK?",
    "What are the steps to solve a scheduling problem using Scheduler?",
    "How can I use the deconfliction algorithms in Scheduler?",
    "How do I use the optimization algorithms in Scheduler?",
    "How can I integrate Scheduler with other STK tools?",
    "How do I create a custom scheduling problem in Scheduler?",
    "How can I visualize the results of a scheduling problem in STK?",
    "How do I use Scheduler for satellite mission planning?",
    "How can I model aircraft mission schedules using Scheduler?",
    "How do I use Scheduler for ground station scheduling?",
    "How do I model a radar system in STK?",
    "What are the steps to perform a radar tracking analysis?",
    "How can I simulate radar jamming in STK?",
    "How do I use the Radar tool for detailed radar system analysis?",
    "How can I model the effect of terrain on radar performance?",
    "How do I use the Analyzer tool for radar system trade studies?",
    "How can I integrate radar data with other STK tools?",
    "How do I use the Volumetrics tool for radar coverage visualization?",
    "How can I model a UAV test to determine radar tracking and jamming?",
    "How do I use the Spectrum Analyzer tool for radar system analysis?",
    "How do I add and manage components in STK?",
    "What are the steps to create a custom component in STK?",
    "How can I integrate components with other STK tools?",
    "How do I use the Analyzer tool for component trade studies?",
    "How can I model the performance of a component in STK?",
    "How do I use the Volumetrics tool for component analysis?",
    "How can I visualize the results of a component analysis in STK?",
    "How do I use the Spectrum Analyzer tool for component analysis?",
    "How can I model the effect of a component on a satellite mission?",
    "How do I use the Constellation Design tool for component analysis?",
    "How do I use the Analysis Workbench in STK?",
    "What are the steps to create a custom analysis in the Workbench?",
    "How can I integrate the Workbench with other STK tools?",
    "How do I use the Analyzer tool for Workbench trade studies?",
    "How can I model the performance of a system using the Workbench?",
    "How do I use the Volumetrics tool for Workbench analysis?",
    "How can I visualize the results of a Workbench analysis in STK?",
    "How do I use the Spectrum Analyzer tool for Workbench analysis?",
    "How can I model the effect of a system on a mission using the Workbench?",
    "How do I use the Constellation Design tool for Workbench analysis?",
    "How do I model a missile trajectory in STK?",
    "What are the steps to perform a missile launch analysis?",
    "How can I simulate missile tracking in STK?",
    "How do I use the Radar tool for missile tracking analysis?",
    "How can I model the effect of terrain on missile performance?",
    "How do I use the Analyzer tool for missile system trade studies?",
    "How can I integrate missile data with other STK tools?",
    "How do I use the Volumetrics tool for missile coverage visualization?",
    "How can I model a missile test to determine tracking and jamming?",
    "How do I use the Spectrum Analyzer tool for missile system analysis?",
    "How do I use the Astrogator tool for satellite maneuver planning?",
    "What are the steps to identify an appropriate launch window for a satellite?",
    "How can I model the circularization of a satellite's orbit using Astrogator?",
    "How do I use the Analyzer tool for Astrogator trade studies?",
    "How can I integrate Astrogator with other STK tools?",
    "How do I use the Volumetrics tool for Astrogator analysis?",
    "How can I visualize the results of an Astrogator analysis in STK?",
    "How do I use the Spectrum Analyzer tool for Astrogator analysis?",
    "How can I model the effect of a satellite maneuver on a mission using Astrogator?",
    "How do I use the Constellation Design tool for Astrogator analysis?",
    "How do I use the Aviator tool for aircraft mission planning?",
    "What are the steps to model an aircraft refueling mission in STK?",
    "How can I simulate a helicopter test flight in mountainous terrain?",
    "How do I use the Terrain Following tool for aircraft missions?",
    "How can I model the effect of atmospheric phenomena on an airborne mission?",
    "How do I use the Radar tool to model radar tracking of an aircraft?",
    "How can I perform a detailed analysis of aircraft communication links?",
    "How do I use the EOIR tool to simulate aircraft sensors?",
    "How can I model a UAV test to determine radar tracking and jamming?",
    "How do I use the Analyzer tool for aircraft mission trade studies?",
    "How do I use the Deck Access tool in STK?",
    "What are the steps to create a custom deck access analysis?",
    "How can I integrate Deck Access with other STK tools?",
    "How do I use the Analyzer tool for Deck Access trade studies?",
    "How can I model the performance of a system using Deck Access?",
    "How do I use the Volumetrics tool for Deck Access analysis?",
    "How can I visualize the results of a Deck Access analysis in STK?",
    "How do I use the Spectrum Analyzer tool for Deck Access analysis?",
    "How can I model the effect of a system on a mission using Deck Access?",
    "How do I use the Constellation Design tool for Deck Access analysis?",
    "How do I use the EOIR tool to simulate electro-optical and infrared sensors?",
    "What are the steps to model an EOIR sensor on a satellite?",
    "How can I perform a detailed analysis of EOIR sensor performance?",
    "How do I use the Analyzer tool for EOIR trade studies?",
    "How can I integrate EOIR with other STK tools?",
    "How do I use the Volumetrics tool for EOIR analysis?",
    "How can I visualize the results of an EOIR analysis in STK?",
    "How do I use the Spectrum Analyzer tool for EOIR analysis?",
    "How can I model the effect of an EOIR sensor on a mission?",
    "How do I use the Constellation Design tool for EOIR analysis?",
    "How do I use the Communications tool to model communication links?",
    "What are the steps to perform a communication link analysis?",
    "How can I simulate RF environmental effects on communication links?",
    "How do I use the Analyzer tool for communication link trade studies?",
    "How can I integrate Communications with other STK tools?",
    "How do I use the Volumetrics tool for communication link analysis?",
    "How can I visualize the results of a communication link analysis in STK?",
    "How do I use the Spectrum Analyzer tool for communication link analysis?",
    "How can I model the effect of terrain on communication links?",
    "How do I use the Constellation Design tool for communication link analysis?",
    "How do I generate a custom report in STK?",
    "What are the steps to create a detailed access report?",
    "How can I use the Report tool to analyze communication links?",
    "How do I generate a coverage report for a satellite constellation?",
    "How can I create a custom report template in STK?",
    "How do I use the Analyzer tool for report generation?",
    "How can I integrate report data with other STK tools?",
    "How do I use the Volumetrics tool for report analysis?",
    "How can I visualize the results of a report in STK?",
    "How do I use the Spectrum Analyzer tool for report generation?",
    "How do I use the Mission Planning tool in STK?",
    "What are the steps to create a detailed mission plan?",
    "How can I integrate Mission Planning with other STK tools?",
    "How do I use the Analyzer tool for mission planning trade studies?",
    "How can I model the performance of a system using Mission Planning?",
    "How do I use the Volumetrics tool for mission planning analysis?",
    "How can I visualize the results of a mission plan in STK?",
    "How do I use the Spectrum Analyzer tool for mission planning analysis?",
    "How can I model the effect of a mission plan on a satellite constellation?",
    "How do I use the Constellation Design tool for mission planning analysis?",
    "How do I use the Solis tool in STK?",
    "What are the steps to create a custom Solis analysis?",
    "How can I integrate Solis with other STK tools?",
    "How do I use the Analyzer tool for Solis trade studies?",
    "How can I model the performance of a system using Solis?",
    "How do I use the Volumetrics tool for Solis analysis?",
    "How can I visualize the results of a Solis analysis in STK?",
    "How do I use the Spectrum Analyzer tool for Solis analysis?",
    "How can I model the effect of a system on a mission using Solis?",
    "How do I use the Constellation Design tool for Solis analysis?",
    "How do I use the SEET tool for space environment effects analysis?",
    "What are the steps to model the effect of space weather on a satellite?",
    "How can I perform a detailed analysis of space environment effects?",
    "How do I use the Analyzer tool for SEET trade studies?",
    "How can I integrate SEET with other STK tools?",
    "How do I use the Volumetrics tool for SEET analysis?",
    "How can I visualize the results of a SEET analysis in STK?",
    "How do I use the Spectrum Analyzer tool for SEET analysis?",
    "How can I model the effect of space environment on a mission?",
    "How do I use the Constellation Design tool for SEET analysis?"
])

with st.form('my_form'):

    # Create the text area first, but don't set the default text yet
    query = st.text_area('Enter question:', 'Type here...')
    
    # Create two columns for the buttons
    col1, col2, _ = st.columns([2, 4, 3])

    with col1:
        submitted = st.form_submit_button('Submit question')
    with col2:
        random_button = st.form_submit_button("Generate random sample question")

    # If random_button is clicked, update the query with random_text
    if random_button:
        query = random_text
        st.info(random_text)
    
    # If either button is clicked, process the query
    if random_button or submitted:
        chain, setup = setup_chain()
        output = st.write_stream(chain.stream(query))
        context_list = setup.invoke(query)['context']
        sources = st.container(border=True)
        st.info("Sources")
        with st.container(border=True):
            for context in context_list:
                metadata = context.metadata
                source = f"[{metadata['url']}](https://{metadata['url']})"
                st.markdown(source, unsafe_allow_html=True)