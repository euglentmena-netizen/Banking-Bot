import csv
import os
import streamlit as st

# Import Mistral
from mistralai import Mistral

# Initialize Mistral client with API key from environment
API_KEY = os.getenv('MISTRAL_API_KEY', 'uZxN0pWyCAldrJweAW1G800rNoQbyy7G')

# Initialize client lazily to avoid startup errors
def get_client():
    """Get or create the Mistral client."""
    global _client
    if '_client' not in globals():
        try:
            _client = Mistral(api_key=API_KEY)
        except Exception as e:
            _client = None
    return _client

# Demo responses fallback
DEMO_RESPONSES = {
    "hello": "Hello! Welcome to HBDB Banking. How can I assist you today?",
    "hi": "Hi there! I'm your HBDB Banking Assistant. What can I help you with?",
    "account": "We offer several account types including Savings, Checking, and Premier accounts. Each has unique benefits. Which one interests you?",
    "rates": "Our current savings rates are competitive. For specific rates, please visit our website or contact our customer service team.",
    "mortgage": "We offer flexible mortgage options. I'd be happy to provide information about our mortgage products and rates.",
    "password": "To reset your password, please visit our login page and click 'Forgot Password'. Follow the instructions sent to your email.",
    "services": "HBDB offers a full range of banking services including savings accounts, checking accounts, loans, mortgages, and investment services.",
    "fees": "Our account fees are minimal. Different accounts have different fee structures. Would you like details on a specific account type?",
}

client = None  # Will be initialized on first use

# Load FAQ data from CSV
def load_faqs(csv_file):
    """Load FAQ data from CSV file into a dictionary."""
    faqs = {}
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                question = row['Question'].strip()
                answer = row['Answer'].strip()
                faqs[question] = answer
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    return faqs

# Create FAQ context for the model
def create_faq_context(faqs):
    """Create a formatted context string from FAQ data."""
    context = "Banking FAQ Database:\n\n"
    for i, (question, answer) in enumerate(faqs.items(), 1):
        context += f"Q{i}: {question}\nA{i}: {answer}\n\n"
    return context

# Initialize FAQ data
csv_file = "hbdb_banking_faqs (2) (1).csv"
faqs = load_faqs(csv_file)

if not faqs:
    # Create empty FAQ context as fallback
    faq_context = "No FAQ data available. Using general banking knowledge."
else:
    faq_context = create_faq_context(faqs)

def chat_with_bot(user_message, conversation_history):
    """Send a message to the banking bot and get a response."""
    
    try:
        # Try to use Mistral API first
        mistral_client = get_client()
        
        if mistral_client is not None:
            # System message with FAQ context
            system_message = f"""You are a helpful HBDB Banking Customer Service Bot. 
Your role is to assist customers with banking-related questions and provide accurate information about HBDB services.

Here is the knowledge base of frequently asked questions and answers:

{faq_context}

Instructions:
- Always try to answer questions using the provided FAQ database
- If a question is not covered in the FAQ, provide helpful general banking information
- Be polite, professional, and concise
- If you're unsure about something, ask the customer to contact HBDB customer service
- Always mention relevant account features or services when appropriate
- Never provide personal financial advice"""

            # Prepare messages
            messages = [{"role": "system", "content": system_message}] + conversation_history + [{"role": "user", "content": user_message}]
            
            # Call Mistral API
            response = mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            # Extract assistant response
            assistant_message = response.choices[0].message.content
            return assistant_message, conversation_history
        else:
            # Fallback to demo mode
            user_lower = user_message.lower()
            for keyword, response in DEMO_RESPONSES.items():
                if keyword in user_lower:
                    return response, conversation_history
            
            default_response = "Thank you for your question! I'm currently using sample responses. Please try keywords like 'account', 'rates', 'mortgage', 'password', or 'fees' for more helpful information."
            return default_response, conversation_history
        
    except Exception as e:
        # Fallback to demo mode on error
        user_lower = user_message.lower()
        for keyword, response in DEMO_RESPONSES.items():
            if keyword in user_lower:
                return response, conversation_history
        
        default_response = "Thank you for your question! I'm currently experiencing connectivity issues. Please try keywords like 'account', 'rates', 'mortgage', 'password', or 'fees'."
        return default_response, conversation_history

def main():
    """Main function to run the banking bot with Streamlit."""
    
    # Streamlit page configuration
    st.set_page_config(
        page_title="HBDB Banking Bot",
        page_icon="🏦",
        layout="centered"
    )
    
    # Title and header
    st.markdown("""
    <h1 style='text-align: center; color: #004b87;'>🏦 HBDB Banking Bot</h1>
    <p style='text-align: center; color: #666;'>Your Banking Assistant</p>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Initialize session state for conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Display sample questions
    with st.expander("📋 Sample Questions", expanded=False):
        st.markdown("""
        - How do I open a savings account?
        - What is HBDB Premier?
        - How do I reset my password?
        - What are the current mortgage rates?
        - What fees apply to my account?
        """)
    
    st.divider()
    
    # Display conversation history
    st.subheader("💬 Chat History")
    
    # Create a container for chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
    
    st.divider()
    
    # Input section
    st.subheader("Ask a Question")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Your question:",
            key="user_input",
            placeholder="Type your banking question here..."
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Process user input
    if send_button and user_input.strip():
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get bot response
        with st.spinner("🤔 Thinking..."):
            response, _ = chat_with_bot(
                user_input,
                st.session_state.conversation_history
            )
        
        # Add assistant response to history
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Rerun to display updated chat
        st.rerun()
    
    # Clear button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()
    
    st.divider()
    
    # Footer
    st.markdown("""
    <p style='text-align: center; color: #999; font-size: 0.8em;'>
    HBDB Banking Bot - Powered by Mistral AI<br>
    For assistance, contact HBDB Customer Service
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
