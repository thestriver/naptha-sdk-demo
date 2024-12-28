# Naptha SDK Demo

A Streamlit application demonstrating the capabilities of the Naptha SDK.

## Setup

1. Clone the repository
2. Create a virtual environment:   
```bash
   python -m venv venv
   source venv/bin/activate  
   # On Windows: venv\Scripts\activate   
```
3. Install dependencies:   
```bash
   pip install -r requirements.txt   
```
4. Create a `.env` file with your credentials:   
```
   HUB_USER=your_username
   HUB_PASS=your_password   
```
5. Run the application:   
```bash
   streamlit run app.py   
```

## Features

- View available Nodes and Agents
- Test agents in the Agent Playground
- Run Chat & Inference operations

## Environment Variables

- `HUB_USER`: Your Naptha Hub username
- `HUB_PASS`: Your Naptha Hub password
- `OPENAI_API_KEY`: OpenAI API Key
