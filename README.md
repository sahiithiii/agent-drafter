**Drafter – AI Writing Assistant**

Drafter is an AI-powered writing assistant built using Streamlit and LangGraph. It enables users to create, modify, and export documents through a structured conversational interface.


**Overview** <br>
The application combines a clean user interface with a tool-augmented language model to provide real-time document editing capabilities. Users interact with the system via chat, and the assistant updates or saves the document based on the intent of the input. <br><br>

**Features** <br>
-AI-assisted document generation and editing. <br>
-Real-time document updates through conversational input. <br>
-Export functionality with support for .txt files. <br>
-Structured agent workflow using LangGraph. <br>
-Persistent session-based state management. <br>
-Minimal and distraction-free user interface. <br><br>

**Architecture**<br>
The system is built around a tool-enabled agent workflow:<br>
-The agent node processes user input and determines the appropriate response.<br>
-The tool node executes actions such as updating or saving the document.<br>
-Conditional edges control whether tools are invoked or execution terminates.<br>
<br>
**Technology Stack**<br>
Frontend: Streamlit<br>
Language Model: Groq  <br>
Agent Framework: LangGraph <br>
Tool Integration: LangChain Tools <br>
State Management: Streamlit Session Stat <br>
