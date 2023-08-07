import streamlit as st
from components.selectors import agent_selection
from ApiClient import ApiClient
from components.learning import learning_page
from components.history import get_history
from components.docs import agixt_docs

st.set_page_config(
    page_title="Interact with Agents",
    page_icon=":speech_balloon:",
    layout="wide",
)

agixt_docs()

st.header("Interact with Agents")
# Create an instance of the API Client

# Fetch available prompts
prompts = ApiClient.get_prompts()

# Add a dropdown to select a mode
mode = st.selectbox("Select Mode", ["Prompt", "Chains", "Chat", "Instruct", "Learning"])

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = ""

agent_name = agent_selection() if mode != "Chains" else None

if mode != "Chains" and mode != "Learning":
    with st.container():
        if agent_name:
            st.session_state["conversation"] = st.selectbox(
                "Choose a conversation",
                ApiClient.get_conversations(agent_name=agent_name),
            )
            st.session_state["chat_history"] = get_history(
                agent_name=agent_name,
                conversation_name=st.session_state["conversation"],
            )


# If the user selects Prompt, then show the prompt functionality
if mode == "Prompt":
    st.markdown("### Choose an Agent and Prompt")
    # Add a dropdown to select a prompt
    # Get the prompt name, set the default prompt name to "Custom Input"
    try:
        custom_input_index = prompts.index("Custom Input")
    except:
        custom_input_index = 0
    prompt_name = st.selectbox("Choose a prompt", prompts, index=custom_input_index)
    # Fetch arguments for the selected prompt
    prompt_args = ApiClient.get_prompt_args(prompt_name=prompt_name)

    # Add input fields for prompt arguments
    st.markdown("### Prompt Variables")
    prompt_args_values = {}
    skip_args = ["command_list", "context", "COMMANDS", "date", "conversation_history"]
    for arg in prompt_args:
        if arg not in skip_args:
            prompt_args_values[arg] = st.text_area(arg)

    # Add a checkbox for websearch option
    browse_links = st.checkbox("Enable Browsing Links in the user input", value=False)
    websearch = st.checkbox("Enable websearch")
    websearch_depth = (
        3 if websearch else 0
    )  # Default depth is 3 if websearch is enabled

    # Add an input field for websearch depth if websearch is enabled
    if websearch:
        websearch_depth = st.number_input(
            "Websearch depth", min_value=1, value=3, key="websearch_depth"
        )
    advanced_options = st.checkbox("Show Advanced Options")
    if advanced_options:
        # Add an input field for shots
        shots = st.number_input(
            "Shots (How many times to ask the agent)", min_value=1, value=1, key="shots"
        )
        context_results = st.number_input(
            "How many memories to inject (Default is 5)",
            min_value=1,
            value=5,
            key="context_results",
        )
        disable_memory = st.checkbox("Disable Memory", value=False)
    else:
        shots = 1
        context_results = 5
        disable_memory = False

    if "user_input" in prompt_args and "context" in prompt_args:
        context_results = st.number_input("Context results", min_value=1, value=5)

    # Button to execute the prompt
    if st.button("Execute"):
        # Call the prompt_agent function
        prompt_args_values["websearch"] = websearch
        prompt_args_values["browse_links"] = browse_links
        prompt_args_values["websearch_depth"] = int(websearch_depth)
        prompt_args_values["context_results"] = int(context_results)
        prompt_args_values["disable_memory"] = disable_memory
        prompt_args_values["shots"] = int(shots)
        prompt_args_values["conversation_name"] = (
            st.session_state["conversation"]
            if "conversation" in st.session_state
            else f"{agent_name} History"
        )
        with st.spinner("Thinking, please wait..."):
            agent_prompt_resp = ApiClient.prompt_agent(
                agent_name=agent_name,
                prompt_name=prompt_name,
                prompt_args=prompt_args_values,
            )
            if agent_prompt_resp:
                st.experimental_rerun()

if mode == "Chat":
    st.markdown("### Choose an Agent to Chat With")
    shots = st.number_input(
        "Shots (How many times to ask the agent)", min_value=1, value=1, key="shots"
    )
    chat_prompt = st.text_area("Enter your message", key="chat_prompt")
    send_button = st.button("Send Message")

    if send_button:
        if agent_name and chat_prompt:
            with st.spinner("Thinking, please wait..."):
                response = ApiClient.prompt_agent(
                    agent_name=agent_name,
                    prompt_name="Chat",
                    prompt_args={
                        "user_input": chat_prompt,
                        "shots": int(shots),
                        "conversation_name": st.session_state["conversation"]
                        if "conversation" in st.session_state
                        else f"{agent_name} History",
                    },
                )
                if response:
                    st.experimental_rerun()


if mode == "Instruct":
    st.markdown("### Choose an Agent to Instruct")
    instruct_prompt = st.text_area("Enter your instruction", key="instruct_prompt")
    send_button = st.button("Send Message")

    if send_button:
        if agent_name and instruct_prompt:
            with st.spinner("Thinking, please wait..."):
                response = ApiClient.prompt_agent(
                    agent_name=agent_name,
                    prompt_name="instruct",
                    prompt_args={
                        "user_input": instruct_prompt,
                        "conversation_name": st.session_state["conversation"]
                        if "conversation" in st.session_state
                        else f"{agent_name} History",
                    },
                )
                if response:
                    st.experimental_rerun()

if mode == "Learning":
    if agent_name:
        learning_page(agent_name)

if mode == "Chains":
    st.markdown("### Chain to Run")
    chain_names = ApiClient.get_chains()
    chain_action = "Run Chain"
    chain_name = st.selectbox("Chains", chain_names)
    # Run single step check box
    user_input = st.text_area("User Input")
    # Need a checkbox for agent override
    agent_override = st.checkbox("Override Agent")
    if agent_override:
        agent_name = agent_selection()
    else:
        agent_name = ""
    single_step = st.checkbox("Run a Single Step")
    if single_step:
        from_step = st.number_input("Step Number to Run", min_value=1, value=1)
        all_responses = False
        if st.button("Run Chain Step"):
            if chain_name:
                if chain_action == "Run Chain":
                    responses = ApiClient.run_chain_step(
                        chain_name=chain_name,
                        user_input=user_input,
                        agent_name=agent_name,
                        step_number=from_step,
                    )
                    st.success(f"Chain '{chain_name}' executed.")
                    st.write(responses)
            else:
                st.error("Chain name is required.")
    else:
        from_step = st.number_input("Start from Step", min_value=1, value=1)
        all_responses = st.checkbox(
            "Show All Responses (If not checked, you will only be shown the last step's response in the chain when done.)"
        )
        if st.button("Run Chain"):
            if chain_name:
                if chain_action == "Run Chain":
                    responses = ApiClient.run_chain(
                        chain_name=chain_name,
                        user_input=user_input,
                        agent_name=agent_name,
                        all_responses=all_responses,
                        from_step=from_step,
                    )
                    st.success(f"Chain '{chain_name}' executed.")
                    st.write(responses)
            else:
                st.error("Chain name is required.")
