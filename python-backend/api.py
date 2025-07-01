import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import database client
from database import db_client

# Import agents and context
from shared_types import AirlineAgentContext
from agents import Agent, RunContextWrapper, function_tool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# Import conference agents
from conference_agents.conference_agents_definitions import (
    schedule_agent,
    networking_agent,
    on_schedule_handoff,
    on_networking_handoff,
    add_business_tool
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Conference Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# PYDANTIC MODELS
# =========================

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    account_number: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    current_agent: str
    messages: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    context: Dict[str, Any]
    agents: List[Dict[str, Any]]
    guardrails: List[Dict[str, Any]]
    customer_info: Optional[Dict[str, Any]] = None

# =========================
# GUARDRAILS
# =========================

@function_tool
async def relevance_guardrail(input_text: str) -> Dict[str, Any]:
    """Check if the input is relevant to conference assistance."""
    conference_keywords = [
        'conference', 'schedule', 'session', 'speaker', 'networking', 'business',
        'attendee', 'meeting', 'presentation', 'workshop', 'track', 'room',
        'registration', 'event', 'agenda', 'program', 'participant'
    ]
    
    input_lower = input_text.lower()
    is_relevant = any(keyword in input_lower for keyword in conference_keywords)
    
    # Also allow greetings and basic questions
    greetings = ['hello', 'hi', 'help', 'what', 'how', 'when', 'where', 'who', 'can you']
    if any(greeting in input_lower for greeting in greetings):
        is_relevant = True
    
    return {
        "reasoning": f"Input contains conference-related keywords: {is_relevant}",
        "is_relevant": is_relevant
    }

@function_tool
async def jailbreak_guardrail(input_text: str) -> Dict[str, Any]:
    """Check for jailbreak attempts."""
    jailbreak_patterns = [
        'ignore', 'forget', 'system', 'prompt', 'instruction', 'override',
        'bypass', 'pretend', 'roleplay', 'act as', 'you are now'
    ]
    
    input_lower = input_text.lower()
    is_safe = not any(pattern in input_lower for pattern in jailbreak_patterns)
    
    return {
        "reasoning": f"No jailbreak patterns detected: {is_safe}",
        "is_safe": is_safe
    }

# =========================
# MAIN TRIAGE AGENT
# =========================

def triage_instructions(
    run_context: RunContextWrapper[AirlineAgentContext], agent: Agent[AirlineAgentContext]
) -> str:
    ctx = run_context.context
    user_name = ctx.passenger_name or "Attendee"
    conference_name = ctx.conference_name or "Business Conference 2025"
    
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}\n"
        f"You are a Conference Assistant for {conference_name}. Welcome {user_name}!\n\n"
        "You help conference attendees with:\n"
        "1. **Conference Schedule**: Finding sessions, speakers, timings, rooms, and tracks\n"
        "2. **Networking**: Connecting with other attendees and exploring business opportunities\n"
        "3. **General Information**: Basic conference details and assistance\n\n"
        "**Handoff Guidelines:**\n"
        "- For schedule-related questions (sessions, speakers, timings, rooms, tracks) → Transfer to Schedule Agent\n"
        "- For networking questions (finding attendees, businesses, adding business) → Transfer to Networking Agent\n"
        "- For general greetings and basic info → Handle directly\n\n"
        "**Important**: Always be helpful and conference-focused. If users ask about non-conference topics, politely redirect them back to conference-related assistance.\n\n"
        "Keep responses concise and friendly. **Do not describe tool usage or agent transfers in your responses.**"
    )

# Create handoff functions
from agents import handoff

@handoff
async def transfer_to_schedule_agent(
    context: RunContextWrapper[AirlineAgentContext]
) -> Agent[AirlineAgentContext]:
    """Transfer to the Schedule Agent for conference schedule inquiries."""
    await on_schedule_handoff(context)
    return schedule_agent

@handoff
async def transfer_to_networking_agent(
    context: RunContextWrapper[AirlineAgentContext]
) -> Agent[AirlineAgentContext]:
    """Transfer to the Networking Agent for networking and business inquiries."""
    await on_networking_handoff(context)
    return networking_agent

# Create the triage agent
triage_agent = Agent[AirlineAgentContext](
    name="Triage Agent",
    model="groq/llama3-8b-8192",
    handoff_description="Main conference assistant that routes requests to specialized agents.",
    instructions=triage_instructions,
    tools=[],
    handoffs=[transfer_to_schedule_agent, transfer_to_networking_agent],
    input_guardrails=[relevance_guardrail, jailbreak_guardrail]
)

# Update other agents to include handoff back to triage
schedule_agent.handoffs = [
    handoff(lambda context: triage_agent, description="Transfer back to main conference assistant")
]
networking_agent.handoffs = [
    handoff(lambda context: triage_agent, description="Transfer back to main conference assistant")
]

# =========================
# CONVERSATION MANAGEMENT
# =========================

# In-memory storage for conversations (in production, use a proper database)
conversations: Dict[str, Dict[str, Any]] = {}

def get_or_create_conversation(conversation_id: Optional[str], account_number: Optional[str]) -> Dict[str, Any]:
    """Get existing conversation or create a new one."""
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    if conversation_id not in conversations:
        conversations[conversation_id] = {
            "id": conversation_id,
            "context": AirlineAgentContext(),
            "current_agent": "Triage Agent",
            "messages": [],
            "events": [],
            "account_number": account_number
        }
    
    return conversations[conversation_id]

# =========================
# API ENDPOINTS
# =========================

@app.get("/user/{identifier}")
async def get_user_info(identifier: str):
    """Get user information by registration ID or QR code (user ID)."""
    try:
        # First try to get user by registration_id
        user = await db_client.get_user_by_registration_id(identifier)
        
        # If not found, try by QR code (user ID)
        if not user:
            user = await db_client.get_user_by_qr_code(identifier)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except Exception as e:
        logger.error(f"Error fetching user info for {identifier}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for conference assistant."""
    try:
        # Get or create conversation
        conversation = get_or_create_conversation(request.conversation_id, request.account_number)
        
        # Load user context if account_number is provided
        if request.account_number and not conversation["context"].customer_id:
            user = await db_client.get_user_by_registration_id(request.account_number)
            if not user:
                user = await db_client.get_user_by_qr_code(request.account_number)
            
            if user:
                # Update context with user information
                conversation["context"].passenger_name = user.get("name")
                conversation["context"].customer_id = user.get("id")
                conversation["context"].account_number = user.get("account_number")
                conversation["context"].customer_email = user.get("email")
                conversation["context"].is_conference_attendee = user.get("is_conference_attendee", True)
                conversation["context"].conference_name = user.get("conference_name", "Business Conference 2025")
        
        # Handle business form submission
        if "I want to add my business with the following details:" in request.message:
            # Parse business details from message
            lines = request.message.split('\n')
            business_data = {}
            
            for line in lines[1:]:  # Skip first line
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Map display names to database field names
                    field_mapping = {
                        "Company Name": "companyName",
                        "Industry Sector": "industrySector", 
                        "Sub-Sector": "subSector",
                        "Location": "location",
                        "Position Title": "positionTitle",
                        "Legal Structure": "legalStructure",
                        "Establishment Year": "establishmentYear",
                        "Products/Services": "productsOrServices",
                        "Brief Description": "briefDescription",
                        "Website": "web"
                    }
                    
                    if key in field_mapping:
                        business_data[field_mapping[key]] = value
            
            # Add business using the tool
            if business_data and conversation["context"].customer_id:
                try:
                    success = await db_client.add_business(
                        conversation["context"].customer_id,
                        business_data
                    )
                    
                    if success:
                        response_message = f"Successfully added your business '{business_data.get('companyName', 'Unknown')}' to the business directory! Other attendees can now find and connect with your business for networking opportunities."
                    else:
                        response_message = "I encountered an issue adding your business. Please try again or contact support."
                        
                except Exception as e:
                    response_message = f"Error adding business: {str(e)}"
            else:
                response_message = "I couldn't process your business information. Please make sure all required fields are filled out."
            
            # Add messages to conversation
            conversation["messages"].append({
                "content": request.message,
                "agent": "User"
            })
            conversation["messages"].append({
                "content": response_message,
                "agent": "Networking Agent"
            })
            
            # Update current agent
            conversation["current_agent"] = "Networking Agent"
        
        else:
            # Regular message processing would go here
            # For now, we'll simulate a simple response
            conversation["messages"].append({
                "content": request.message,
                "agent": "User"
            })
            
            # Simple routing logic
            message_lower = request.message.lower()
            
            if any(word in message_lower for word in ['schedule', 'session', 'speaker', 'time', 'room', 'track', 'when']):
                agent_name = "Schedule Agent"
                response = "I can help you find conference schedule information. What specific session, speaker, or time are you looking for?"
            elif any(word in message_lower for word in ['network', 'business', 'attendee', 'connect', 'company', 'find people']):
                agent_name = "Networking Agent"
                response = "I can help you connect with other attendees and explore business opportunities. Are you looking for specific people, companies, or would you like to add your own business?"
            else:
                agent_name = "Triage Agent"
                response = f"Hello! I'm your conference assistant. I can help you with:\n\n• **Conference Schedule** - Find sessions, speakers, and timings\n• **Networking** - Connect with attendees and businesses\n\nWhat would you like to know about the conference?"
            
            conversation["messages"].append({
                "content": response,
                "agent": agent_name
            })
            
            conversation["current_agent"] = agent_name
        
        # Prepare customer info
        customer_info = None
        if conversation["context"].customer_id:
            customer_info = {
                "customer": {
                    "name": conversation["context"].passenger_name,
                    "account_number": conversation["context"].account_number,
                    "email": conversation["context"].customer_email,
                    "is_conference_attendee": conversation["context"].is_conference_attendee,
                    "conference_name": conversation["context"].conference_name
                },
                "bookings": []
            }
        
        # Prepare response
        response = ChatResponse(
            conversation_id=conversation["id"],
            current_agent=conversation["current_agent"],
            messages=conversation["messages"][-2:] if len(conversation["messages"]) >= 2 else conversation["messages"],
            events=conversation.get("events", []),
            context=conversation["context"].model_dump(),
            agents=[
                {
                    "name": "Triage Agent",
                    "description": "Main conference assistant",
                    "handoffs": ["Schedule Agent", "Networking Agent"],
                    "tools": [],
                    "input_guardrails": ["relevance_guardrail", "jailbreak_guardrail"]
                },
                {
                    "name": "Schedule Agent", 
                    "description": "Conference schedule information",
                    "handoffs": ["Triage Agent"],
                    "tools": ["get_conference_schedule"],
                    "input_guardrails": []
                },
                {
                    "name": "Networking Agent",
                    "description": "Networking and business connections", 
                    "handoffs": ["Triage Agent"],
                    "tools": ["search_attendees", "search_businesses", "add_business"],
                    "input_guardrails": []
                }
            ],
            guardrails=[],
            customer_info=customer_info
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Conference Assistant API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)