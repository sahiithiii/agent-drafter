Drafter – AI Writing Assistant

Drafter is an AI-powered writing assistant built using Streamlit and LangGraph. It enables users to create, modify, and export documents through a structured conversational interface.


Overview:
The application combines a clean user interface with a tool-augmented language model to provide real-time document editing capabilities. Users interact with the system via chat, and the assistant updates or saves the document based on the intent of the input.

Features:
AI-assisted document generation and editing
Real-time document updates through conversational input
Export functionality with support for .txt files
Structured agent workflow using LangGraph
Persistent session-based state management
Minimal and distraction-free user interface

**Architecture**
The system is built around a tool-enabled agent workflow:
-The agent node processes user input and determines the appropriate response
-The tool node executes actions such as updating or saving the document
-Conditional edges control whether tools are invoked or execution terminates
