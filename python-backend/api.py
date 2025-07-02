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

# Import main components
from main import (
    conversations,
    get_or_create_conversation,
    load_user_context,
    execute_schedule_agent,
    execute_networking_agent
)

# Import shared types
from shared_types import AirlineAgentContext

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
        
        # Load user context if account_number is provided and not already loaded
        if request.account_number and not conversation["context"].customer_id:
            await load_user_context(conversation, request.account_number)
        
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
            
            # Add business using the database client
            if business_data and conversation["context"].customer_id:
                try:
                    success = await db_client.add_business(
                        conversation["context"].customer_id,
                        business_data
                    )
                    
                    if success:
                        response_message = f"✅ Successfully added your business '{business_data.get('companyName', 'Unknown')}' to the business directory!\n\nYour business is now visible to other conference attendees for networking opportunities. Other participants can find your business when searching by industry, location, or company name.\n\nIs there anything else I can help you with regarding networking or the conference?"
                    else:
                        response_message = "❌ I encountered an issue adding your business. Please try again or contact support for assistance."
                        
                except Exception as e:
                    logger.error(f"Error adding business: {e}")
                    response_message = f"❌ Error adding business: {str(e)}"
            else:
                response_message = "❌ I couldn't process your business information. Please make sure all required fields are filled out correctly."
            
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
            # Regular message processing
            conversation["messages"].append({
                "content": request.message,
                "agent": "User"
            })
            
            # Simple routing logic based on message content
            message_lower = request.message.lower()
            
            # Determine which agent to use
            if any(word in message_lower for word in ['schedule', 'session', 'speaker', 'time', 'room', 'track', 'when', 'agenda', 'program', 'july', 'date', 'events']):
                agent_name = "Schedule Agent"
                try:
                    # Convert context to dict for agent execution
                    context_dict = {
                        'customer_id': conversation["context"].customer_id,
                        'passenger_name': conversation["context"].passenger_name,
                        'account_number': conversation["context"].account_number,
                        'customer_email': conversation["context"].customer_email,
                        'is_conference_attendee': conversation["context"].is_conference_attendee,
                        'conference_name': conversation["context"].conference_name,
                        'user_company_name': conversation["context"].user_company_name,
                        'user_location': conversation["context"].user_location,
                        'user_registration_id': conversation["context"].user_registration_id,
                        'user_conference_package': conversation["context"].user_conference_package,
                        'user_primary_stream': conversation["context"].user_primary_stream,
                        'user_secondary_stream': conversation["context"].user_secondary_stream
                    }
                    response = await execute_schedule_agent(request.message, context_dict)
                except Exception as e:
                    logger.error(f"Error executing agent {agent_name}: {e}")
                    response = "I'm having trouble processing your request. Please try again or rephrase your question."
                    
            elif any(word in message_lower for word in ['network', 'business', 'attendee', 'connect', 'company', 'find people', 'add business', 'register business', 'show attendees']):
                agent_name = "Networking Agent"
                try:
                    # Convert context to dict for agent execution
                    context_dict = {
                        'customer_id': conversation["context"].customer_id,
                        'passenger_name': conversation["context"].passenger_name,
                        'account_number': conversation["context"].account_number,
                        'customer_email': conversation["context"].customer_email,
                        'is_conference_attendee': conversation["context"].is_conference_attendee,
                        'conference_name': conversation["context"].conference_name,
                        'user_company_name': conversation["context"].user_company_name,
                        'user_location': conversation["context"].user_location,
                        'user_registration_id': conversation["context"].user_registration_id,
                        'user_conference_package': conversation["context"].user_conference_package,
                        'user_primary_stream': conversation["context"].user_primary_stream,
                        'user_secondary_stream': conversation["context"].user_secondary_stream
                    }
                    response = await execute_networking_agent(request.message, context_dict)
                except Exception as e:
                    logger.error(f"Error executing agent {agent_name}: {e}")
                    response = "I'm having trouble processing your request. Please try again or rephrase your question."
                    
            else:
                agent_name = "Triage Agent"
                if 'hello' in message_lower or 'hi' in message_lower:
                    user_name = conversation["context"].passenger_name or "there"
                    response = f"Hello {user_name}! 👋 Welcome to Business Conference 2025!\n\nI'm your conference assistant and I'm here to help you with:\n\n🗓️ **Conference Schedule** - Find sessions, speakers, timings, and rooms\n🤝 **Networking** - Connect with attendees and explore business opportunities\n\nWhat would you like to know about the conference today?"
                else:
                    response = f"I'm your conference assistant for Business Conference 2025. I can help you with:\n\n🗓️ **Conference Schedule** - Find sessions, speakers, timings, and rooms\n🤝 **Networking** - Connect with attendees and explore business opportunities\n\nWhat would you like to know about the conference?"
            
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
                    "conference_name": conversation["context"].conference_name,
                    "registration_id": conversation["context"].user_registration_id,
                    "company": conversation["context"].user_company_name,
                    "location": conversation["context"].user_location,
                    "conference_package": conversation["context"].user_conference_package,
                    "primary_stream": conversation["context"].user_primary_stream,
                    "secondary_stream": conversation["context"].user_secondary_stream
                },
                "bookings": []
            }
        
        # Prepare response
        response = ChatResponse(
            conversation_id=conversation["id"],
            current_agent=conversation["current_agent"],
            messages=conversation["messages"][-2:] if len(conversation["messages"]) >= 2 else conversation["messages"],
            events=conversation.get("events", []),
            context=conversation["context"].model_dump() if hasattr(conversation["context"], 'model_dump') else conversation["context"].__dict__,
            agents=[
                {
                    "name": "Triage Agent",
                    "description": "Main conference assistant that routes requests",
                    "handoffs": ["Schedule Agent", "Networking Agent"],
                    "tools": [],
                    "input_guardrails": []
                },
                {
                    "name": "Schedule Agent", 
                    "description": "Conference schedule and session information",
                    "handoffs": ["Triage Agent"],
                    "tools": ["get_conference_schedule"],
                    "input_guardrails": []
                },
                {
                    "name": "Networking Agent",
                    "description": "Networking, attendees, and business connections", 
                    "handoffs": ["Triage Agent"],
                    "tools": ["search_attendees", "search_businesses", "add_business", "display_business_form"],
                    "input_guardrails": []
                }
            ],
            guardrails=[],
            customer_info=customer_info
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Conference Assistant API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)