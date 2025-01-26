import streamlit as st
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.orchestrator import Orchestrator
from src.config import settings

st.set_page_config(
    page_title="Multi-Reasoning Code Processor",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'api_status' not in st.session_state:
    st.session_state.api_status = "Not Tested"
if 'last_input' not in st.session_state:
    st.session_state.last_input = ""
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Test API key validity on startup
@st.cache_resource
def init_orchestrator():
    try:
        orchestrator = Orchestrator()
        st.session_state.api_status = "API Key Valid"
        return orchestrator
    except Exception as e:
        st.session_state.api_status = f"API Key Error: {str(e)}"
        return None

# Initialize orchestrator
orchestrator = init_orchestrator()

st.title("Multi-Reasoning Code Processor")

# Enhanced debug information
with st.expander("Debug Info"):
    st.write("API Key Status:", "Set" if settings.OPENROUTER_API_KEY else "Not Set")
    st.write("API Validation Status:", st.session_state.get('api_status', 'Not Tested'))
    st.write("Available Models:", settings.MODELS)
    st.write("OpenRouter Base URL:", settings.OPENROUTER_BASE_URL)
st.markdown("""
Enter your code or problem below. The system will process it using multiple AI models 
and provide a consistent, summarized response.
""")

# Create main containers
input_container = st.container()
output_container = st.container()

with input_container:
    # Initialize input state if not present
    if 'problem_input' not in st.session_state:
        st.session_state.problem_input = ""
    
    # Input area with direct session state binding
    st.session_state.problem_input = st.text_area(
        "Enter your code or problem here:",
        value=st.session_state.problem_input,
        height=200,
        placeholder="Enter your code or problem here...",
        key="problem_input_area"
    )
    
    # Button container with spacing
    button_cols = st.columns([1, 5, 6])
    
    # Reset button
    with button_cols[0]:
        if st.button("🔄", key="reset", help="Reset form", use_container_width=True):
            st.session_state.processing = False
            st.session_state.last_input = ""
            st.session_state.problem_input = ""
            st.rerun()
    
    # Process button
    with button_cols[2]:
        process = st.button(
            "🚀 Process",
            type="primary",
            disabled=st.session_state.processing or not st.session_state.problem_input.strip(),
            key="process_button",
            use_container_width=True
        )

# Handle processing
if process and st.session_state.problem_input.strip():
    # Input validation
    if orchestrator is None:
        st.error("❌ System not properly initialized. Please check API configuration.")
    elif st.session_state.problem_input.strip() == st.session_state.last_input:
        st.warning("⚠️ This is the same as your last input. Try a different problem!")
    else:
        # Update state
        st.session_state.processing = True
        st.session_state.last_input = st.session_state.problem_input.strip()
        
        with st.status("🔄 Processing...", expanded=True) as status:
            try:
                # Create a new event loop for async operations
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                status.write("🤖 Initializing models...")
                
                # Set up async task
                task = orchestrator.solve_problem(st.session_state.problem_input)
                
                # Run the task with progress updates
                result = loop.run_until_complete(task)
                    
                # Show model responses
                if "agent_responses" in result:
                    status.write(f"✓ Received {len(result['agent_responses'])} responses")
                    try:
                        for response in result["agent_responses"]:
                            st.write(f"\n🤖 Response from {response['model']}:")
                            st.code(response["raw_response"], language="markdown")
                    except Exception as e:
                        st.error(f"Error displaying responses: {str(e)}")
                        st.write("Raw responses:", result["agent_responses"])
                
                status.update(label="✅ Processing complete!", state="complete")
            except Exception as e:
                error_msg = str(e)
                st.error("Error Details:")
                st.error(f"Type: {type(e).__name__}")
                st.error(f"Message: {error_msg}")
                
                if "402 Payment Required" in error_msg:
                    st.error("""
                    OpenRouter API payment required. Please check:
                    1. Account balance at https://openrouter.ai/account
                    2. API key validity
                    3. Account billing status
                    """)
                elif "401" in error_msg:
                    st.error("""
                    Authentication failed. Please check:
                    1. API key format (should start with 'sk-')
                    2. API key validity
                    3. API key permissions
                    """)
                elif "429" in error_msg:
                    st.error("Rate limit exceeded. Please wait a moment and try again.")
                st.stop()  # Stop execution here
            finally:
                try:
                    loop.close()
                except Exception as e:
                    st.error(f"Error closing loop: {str(e)}")
            
            # Enhanced result debugging
            st.subheader("📝 Debug Information")
            st.write("Raw API Response:", result)
            if isinstance(result, dict):
                st.write("Response Type: Dictionary")
                st.write("Keys:", list(result.keys()))
                if "agent_responses" in result:
                    st.write("Number of Agent Responses:", len(result["agent_responses"]))
                    for i, response in enumerate(result["agent_responses"]):
                        st.markdown(f"**Response {i+1} from {response['model']}:**")
                        st.write("Raw Response:", response["raw_response"])
                        st.write("Processing Time:", response.get("processing_time", "N/A"))
                        st.write("Tokens Used:", response.get("tokens_used", "N/A"))
            else:
                st.write("Response Type:", type(result).__name__)
                
            if "summary" in result:
                st.markdown("**Summary Details:**")
                st.write("Summary Type:", type(result["summary"]).__name__)
                if isinstance(result["summary"], dict):
                    st.write("Summary Keys:", list(result["summary"].keys()))
                    st.write("Best Answer:", result["summary"].get("best_answer", "N/A"))
                    st.write("Confidence:", result["summary"].get("confidence", "N/A"))
                    st.write("Reasoning:", result["summary"].get("reasoning", "N/A"))
            
            # Display results in a clean format
            st.markdown("### 📊 Results")
            
            # Display summary
            if isinstance(result["summary"], dict):
                status = result["summary"].get("status", "")
                if status == "error":
                    st.error("❌ " + result["summary"]["message"])
                    st.session_state.processing = False
                elif status == "timeout":
                    st.warning("⚠️ " + result["summary"]["message"])
                    st.info("💡 Best available answer: " + result["summary"]["best_answer"])
                    st.session_state.processing = False
                else:
                    st.success("✅ Analysis complete")
                    
                    # Create columns for the answer display
                    answer_col1, answer_col2 = st.columns([3, 1])
                    
                    with answer_col1:
                        # Display the best answer prominently
                        st.markdown("""
                        <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin: 1rem 0;'>
                            <h4 style='margin: 0; color: #0e1117;'>Best Answer:</h4>
                            <p style='margin: 0.5rem 0 0 0; color: #0e1117; font-size: 1.1rem;'>{}</p>
                        </div>
                        """.format(result["summary"]["best_answer"]), unsafe_allow_html=True)
                    
                    with answer_col2:
                        st.markdown(f"""
                        **Confidence**: {result["summary"]["confidence"]}  
                        **Source**: {result["summary"]["selected_from"]}
                        """)
                    
                    # Display analysis details without nesting expanders
                    st.markdown("#### 🔍 Analysis Details")
                    st.markdown(f"""
                    **Reasoning**:  
                    {result["summary"]["reasoning"]}
                    
                    **All model answers**:
                    """)
                    for model, answer in result["summary"]["all_answers"].items():
                        st.markdown(f"- **{model}**: {answer}")
                    
                    # Reset processing state
                    st.session_state.processing = False
            else:
                st.markdown(str(result["summary"]))
                st.session_state.processing = False
