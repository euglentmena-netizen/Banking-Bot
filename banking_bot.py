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
        layout="wide"
    )
    
    # Professional banking color scheme with Tiffany Blue CSS
    st.markdown("""
    <style>
    :root {
        --primary-navy: #1a3a52;
        --primary-blue: #003366;
        --tiffany-blue: #0ABAB5;
        --accent-gold: #D4AF37;
        --light-gray: #F5F7FA;
        --dark-gray: #2C3E50;
        --text-dark: #1a1a1a;
    }
    
    .main {
        background-color: #F5F7FA;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #003366 0%, #1a3a52 100%);
        padding: 20px;
        border-radius: 0;
    }
    
    .sidebar-logo {
        text-align: center;
        padding: 20px 0;
        border-bottom: 3px solid #0ABAB5;
        margin-bottom: 20px;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #0ABAB5 0%, #00897B 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .agent-name {
        font-size: 1.3em;
        font-weight: 700;
        margin: 15px 0 10px 0;
        color: white;
    }
    
    .rating {
        font-size: 1.8em;
        margin: 10px 0;
        letter-spacing: 2px;
    }
    
    .rating-label {
        font-size: 0.9em;
        opacity: 0.9;
        margin-bottom: 10px;
    }
    
    .stMarkdown h1 {
        color: #003366 !important;
        font-weight: 700;
    }
    
    .stMarkdown h2 {
        color: #1a3a52 !important;
        font-weight: 600;
    }
    
    .stMarkdown p {
        color: #2C3E50 !important;
    }
    
    .stButton > button {
        background-color: #0ABAB5 !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #D4AF37 !important;
        color: #003366 !important;
        font-weight: 600 !important;
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #0ABAB5 !important;
        border-radius: 8px !important;
    }
    
    .stExpander {
        border: 2px solid #0ABAB5 !important;
        border-radius: 8px !important;
    }
    
    .stExpander > div:first-child {
        background-color: #0ABAB5 !important;
        color: white !important;
    }
    
    .stDivider {
        border-top: 3px solid #0ABAB5 !important;
    }
    
    .main-content {
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create sidebar with agent info and branding
    with st.sidebar:
        # Professional Banking Logo
        st.markdown("""
        <div style='background: linear-gradient(135deg, #0ABAB5 0%, #008B7F 100%); padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 15px;'>
            <div style='font-size: 3.5em;'>🏛️</div>
            <h2 style='color: white; margin: 10px 0 0 0; font-size: 1.3em;'>HBDB</h2>
            <p style='color: white; margin: 5px 0 0 0; font-size: 0.85em;'>Banking Excellence</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Agent Information Card
        st.markdown("""
        <div style='background: linear-gradient(135deg, #0ABAB5 0%, #00A099 100%); padding: 20px; border-radius: 12px; text-align: center; color: white;'>
            <div style='font-size: 3em; margin-bottom: 10px;'>👨‍💼</div>
            <h3 style='margin: 10px 0; color: white; font-size: 1.3em;'>Mr Euglent Mena</h3>
            <p style='margin: 5px 0; font-size: 0.95em; opacity: 0.95;'>Senior Banking Assistant</p>
            
            <div style='background: rgba(255,255,255,0.25); padding: 15px; border-radius: 8px; margin: 15px 0;'>
                <p style='font-size: 0.9em; opacity: 0.95; margin-bottom: 10px; font-weight: 600;'>Client Satisfaction</p>
                <div style='font-size: 2em; margin: 10px 0; letter-spacing: 2px;'>⭐⭐⭐⭐⭐</div>
                <p style='font-size: 0.9em; margin: 10px 0; font-weight: bold;'>5.0 / 5.0 Rating</p>
            </div>
            
            <div style='font-size: 0.85em; margin-top: 15px; opacity: 0.9;'>
                <p style='margin: 5px 0;'>✓ 24/7 Available</p>
                <p style='margin: 5px 0;'>✓ Expert Support</p>
                <p style='margin: 5px 0;'>✓ Secure & Trusted</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Links
        st.markdown("""
        <p style='color: #0ABAB5; font-weight: 600; font-size: 0.95em; margin-bottom: 10px;'>Quick Navigation</p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Home", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("❓ FAQ", use_container_width=True):
                st.info("Sample Questions section in main panel")
        
        st.markdown("---")
        
        st.markdown("""
        <p style='color: #666; font-size: 0.8em; text-align: center; margin-top: 30px; opacity: 0.8;'>
            © 2026 HBDB Banking<br>
            Powered by Mistral AI
        </p>
        """, unsafe_allow_html=True)
    
    # Main content area
    st.markdown("""
    <div class='main-content'>
    """, unsafe_allow_html=True)
    
    # Title and header with professional styling and Tiffany blue accent
    st.markdown("""
    <div style='background: linear-gradient(135deg, #003366 0%, #1a3a52 50%, #0ABAB5 100%); padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 30px; box-shadow: 0 6px 15px rgba(0,0,0,0.15);'>
        <h1 style='color: white; margin: 0; font-size: 2.8em; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>🏦 HBDB Banking Bot</h1>
        <p style='color: #D4AF37; margin: 15px 0 0 0; font-size: 1.2em; font-weight: 600;'>Your Professional Banking Assistant</p>
        <p style='color: #E8F4F8; margin: 10px 0 0 0; font-size: 0.95em; opacity: 0.95;'>Assisted by Mr Euglent Mena ⭐ 5.0 Rating</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Display sample questions with professional styling
    with st.expander("📋 Sample Banking Questions"):
        st.markdown("""
        <div style='color: #2C3E50;'>
        
        **Accounts & Services**
        - How do I open a savings account?
        - What is HBDB Premier?
        - What banking services do you offer?
        
        **Account Management**
        - How do I reset my password?
        - What are your account fees?
        
        **Products & Rates**
        - What are the current mortgage rates?
        - What are your savings account rates?
        
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display conversation history with professional styling
    st.markdown("<h2 style='color: #0ABAB5; display: flex; align-items: center;'>💬 Chat History</h2>", unsafe_allow_html=True)
    
    # Create a container for chat messages
    chat_container = st.container()
    
    with chat_container:
        if len(st.session_state.conversation_history) == 0:
            st.info("👋 Start a conversation by asking a banking question below!")
        else:
            for message in st.session_state.conversation_history:
                if message["role"] == "user":
                    st.chat_message("user", avatar="👤").write(message["content"])
                else:
                    st.chat_message("assistant", avatar="🏦").write(message["content"])
    
    
    st.markdown("---")
    
    # Input section with professional styling
    st.markdown("<h2 style='color: #003366;'>Ask a Question</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Your question:",
            key="user_input",
            placeholder="Type your banking question here..."
        )
    
    with col2:
        send_button = st.button("💬 Send", use_container_width=True)
    
    # Process user input
    if send_button and user_input.strip():
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get bot response
        with st.spinner("🤔 Processing your request..."):
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
    
    st.markdown("---")
    
    # Footer with professional styling and Tiffany blue accent
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a3a52 0%, #003366 50%, #0ABAB5 100%); padding: 25px; border-radius: 12px; text-align: center; margin-top: 30px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
        <p style='color: white; margin: 0; font-size: 0.95em; font-weight: 600;'>
            🏦 <strong>HBDB Banking Bot</strong> - Powered by Mistral AI<br>
            <span style='color: #D4AF37; display: block; margin-top: 10px;'>Assisted by Mr Euglent Mena ⭐ 5.0 / 5.0</span>
        </p>
        <p style='color: white; margin: 10px 0 0 0; font-size: 0.8em; opacity: 0.85;'>
            For assistance, contact HBDB Customer Service
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
