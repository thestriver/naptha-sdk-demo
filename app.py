import streamlit as st
import pandas as pd
import asyncio
from dotenv import load_dotenv
import os
from naptha_sdk.client.naptha import Naptha
from naptha_sdk.schemas import ChatCompletionRequest

# Load environment variables
load_dotenv()

# Check for required environment variables
if not os.getenv("HUB_USER") or not os.getenv("HUB_PASS"):
    st.error("Environment variables HUB_USER and/or HUB_PASS are not set!")
    hub_user = st.text_input("Enter Hub Username")
    hub_pass = st.text_input("Enter Hub Password", type="password")
    if st.button("Save Credentials"):
        with open(".env", "w") as f:
            f.write(f"HUB_USER={hub_user}\nHUB_PASS={hub_pass}")
        st.success("Credentials saved! Please restart the app.")
        st.stop()
else:
    st.success("Environment variables loaded successfully!")
    # Debug: Print env vars (masked for security)
    # st.write(f"HUB_USER: {os.getenv('HUB_USER')[:3]}{'*' * (len(os.getenv('HUB_USER')) - 3)}")
    # st.write(f"HUB_PASS: {'*' * len(os.getenv('HUB_PASS'))}")

# Add logo image to both sidebar and homepage
logo_url = "https://pbs.twimg.com/profile_images/1844091788589465600/_yY1wtJu_400x400.png"

def create_agents_table(agents):
    """Convert agents data for display"""
    if not agents:
        return

    # Extract relevant data into a list of dictionaries
    agents_data = [{
        'Name': agent.get('name', ''),
        'ID': agent.get('id', '')[:15] + '...',
        'Author': agent.get('author', '')[:15] + '...',
        'Description': agent.get('description', '')[:30] + '...' if len(agent.get('description', '')) > 30 else agent.get('description', '')
    } for agent in agents]

    # Display using Streamlit
    st.table(agents_data)

def create_nodes_table(nodes):
    """Convert nodes data for display"""
    if not nodes:
        return

    # Extract relevant data into a list of dictionaries
    nodes_data = [{
        'ID': node.get('id', '')[:15] + '...',
        'Type': node.get('node_type', ''),
        'Architecture': node.get('arch', ''),
        'OS': node.get('os', ''),
        'GPUs': node.get('num_gpus', 0),
        'Models': ', '.join(node.get('ollama_models', []))
    } for node in nodes]

    # Display using Streamlit
    st.table(nodes_data)

def create_personas_table(personas):
    """Convert personas data for display"""
    if not personas:
        return

    # Extract relevant data into a list of dictionaries
    personas_data = [{
        'Name': persona.get('name', ''),
        'ID': persona.get('id', '')[:15] + '...',
        'Description': persona.get('description', '')[:30] + '...' if len(persona.get('description', '')) > 30 else persona.get('description', '')
    } for persona in personas]

    # Display using Streamlit
    st.table(personas_data)

async def verify_credentials():
    """Verify credentials work"""
    try:
        async with Naptha() as naptha:
            await naptha.hub.signin(os.getenv("HUB_USER"), os.getenv("HUB_PASS"))
            return True
    except Exception as e:
        st.error(f"Credential verification failed: {str(e)}")
        return False

async def run_inference(model, messages):
    """Run inference with new client for each request"""
    try:
        async with Naptha() as naptha:
            await naptha.hub.signin(os.getenv("HUB_USER"), os.getenv("HUB_PASS"))
            req = ChatCompletionRequest(
                model=model,
                messages=messages
            )
            res = await naptha.node.run_inference(req)
            return res['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Inference failed: {str(e)}")
        return None

async def list_nodes():
    """List nodes with new client"""
    try:
        async with Naptha() as naptha:
            await naptha.hub.signin(os.getenv("HUB_USER"), os.getenv("HUB_PASS"))
            # return await naptha.hub.list_nodes()
            nodes = await naptha.hub.list_nodes()
            if nodes:
                create_nodes_table(nodes)
            return nodes
    except Exception as e:
        st.error(f"Failed to list nodes: {str(e)}")
        return None

async def list_agents():
    """List agents with new client"""
    try:
        async with Naptha() as naptha:
            await naptha.hub.signin(os.getenv("HUB_USER"), os.getenv("HUB_PASS"))
            # return await naptha.hub.list_agents()
            agents = await naptha.hub.list_agents()
            if agents:
                create_agents_table(agents)
            return agents
    except Exception as e:
        st.error(f"Failed to list agents: {str(e)}")
        return None

async def list_personas():
    """List personas with new client"""
    try:
        async with Naptha() as naptha:
            await naptha.hub.signin(os.getenv("HUB_USER"), os.getenv("HUB_PASS"))
            personas = await naptha.hub.list_personas()
            if personas:
                create_personas_table(personas)
            return personas
    except Exception as e:
        st.error(f"Failed to list personas: {str(e)}")
        return None

async def run_hello_world_agent(firstname, surname):
    """Run hello world agent with new client"""
    try:
        async with Naptha() as naptha:
            await naptha.hub.signin(os.getenv("HUB_USER"), os.getenv("HUB_PASS"))
            
            # Check/register user
            user = await naptha.node.check_user(user_input={"public_key": naptha.hub.public_key})
            if not user:
                user = await naptha.node.register_user(user_input={"public_key": naptha.hub.public_key})
            
            agent_run_input = {
                'consumer_id': user['id'],
                "inputs": {
                    'firstname': firstname,
                    'surname': surname
                },
                "agent_deployment": {
                    "name": "hello_world_agent",
                    "module": {
                        "name": "hello_world_agent"
                    },
                    "worker_node_url": "http://node.naptha.ai:7001"
                }
            }
            
            return await naptha.node.run_agent_and_poll(agent_run_input)
    except Exception as e:
        st.error(f"Failed to run agent: {str(e)}")
        return None

async def run_simple_chat_agent(question):
    """Run simple chat agent with new client"""
    try:
        async with Naptha() as naptha:
            await naptha.hub.signin(os.getenv("HUB_USER"), os.getenv("HUB_PASS"))
            
            # Check/register user
            user = await naptha.node.check_user(user_input={"public_key": naptha.hub.public_key})
            if not user:
                user = await naptha.node.register_user(user_input={"public_key": naptha.hub.public_key})
            
            agent_run_input = {
                'consumer_id': user['id'],
                "inputs": {
                    'tool_name': 'chat',
                    'tool_input_data': question
                },
                "agent_deployment": {
                    "name": "simple_chat_agent",
                    "module": {
                        "name": "simple_chat_agent"
                    },
                    "worker_node_url": "http://node.naptha.ai:7001"
                }
            }
            
            return await naptha.node.run_agent_and_poll(agent_run_input)
    except Exception as e:
        st.error(f"Failed to run agent: {str(e)}")
        return None

def main():
    st.title("Naptha SDK Demo")
    
    # Verify credentials on startup
    if asyncio.run(verify_credentials()):
        st.success("Successfully connected to Naptha!")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Select Page",
            ["Nodes & Agents", "Agent Playground", "Chat & Inference"]
        )
        
        if page == "Nodes & Agents":
            st.header("Available Nodes")
            if st.button("Refresh Nodes"):
                nodes = asyncio.run(list_nodes())
                if nodes:
                    st.write(nodes)
                
            st.header("Available Agents")
            if st.button("Refresh Agents"):
                agents = asyncio.run(list_agents())
                if agents:
                    st.write(agents)
                
            st.header("Available Personas")
            if st.button("Refresh Personas"):
                personas = asyncio.run(list_personas())
                if personas:
                    st.write(personas)
                
        elif page == "Agent Playground":
            st.header("Agent Playground")
            
            # Agent selection
            agent_type = st.selectbox(
                "Select Agent",
                ["Hello World Agent", "Simple Chat Agent"]
            )
            
            if agent_type == "Hello World Agent":
                st.subheader("Hello World Agent")
                firstname = st.text_input("First Name")
                surname = st.text_input("Last Name")
                
                if st.button("Run Hello World"):
                    result = asyncio.run(run_hello_world_agent(firstname, surname))
                    if result:
                        st.write("Agent Response:", result.results[0] if result.results else "No response")
                        
            elif agent_type == "Simple Chat Agent":
                st.subheader("Simple Chat Agent")
                question = st.text_area("Enter your question")
                
                if st.button("Run Chat Agent"):
                    result = asyncio.run(run_simple_chat_agent(question))
                    if result:
                        st.write("Agent Response:", result.results[0] if result.results else "No response")
                
        elif page == "Chat & Inference":
            st.header("Chat & Inference")
            
            model = st.selectbox("Select Model", ["gpt-4o-mini", "phi3:mini"])
            user_input = st.text_area("Enter your message")
            
            if st.button("Send"):
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ]
                response = asyncio.run(run_inference(model, messages))
                if response:
                    st.write("Response:", response)

    # Sidebar
    with st.sidebar:
        st.image(logo_url, width=100)

if __name__ == "__main__":
    main()