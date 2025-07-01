# python-backend/main.py

from __future__ import annotations as _annotations

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Import shared context type from shared_types.py
from shared_types import AirlineAgentContext
from database import db_client

# Import agents framework
from agents import Agent, RunContextWrapper, function_tool, handoff
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# Import conference agents
from conference_agents.conference_agents_definitions import (
    schedule_agent,
    networking_agent,
    on_schedule_handoff,
    on_networking_handoff,
    get_conference_schedule_tool,
    search_attendees_tool,
    search_businesses_tool,
    get_user_businesses_tool,
    display_business_form_tool,
    add_business_tool,
    get_organization_info_tool
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# GUARDRAILS
# =========================

@function_tool
async def relevance_guardrail(input_text: str) -> Dict[str, Any]:
    """Check if the input is relevant to conference assistance."""
    conference_keywords = [
        'conference', 'schedule', 'session', 'speaker', 'networking', 'business',
        'attendee', 'meeting', 'presentation', 'workshop', 'track', 'room',
        'registration', 'event', 'agenda', 'program', 'participant', 'hello',
        'hi', 'help', 'what', 'how', 'when', 'where', 'who', 'can you'
    ]
    
    input_lower = input_text.lower()
    is_relevant = any(keyword in input_lower for keyword in conference_keywords)
    
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
@handoff
async def transfer_back_to_triage(
    context: RunContextWrapper[AirlineAgentContext]
) -> Agent[AirlineAgentContext]:
    """Transfer back to the main conference assistant."""
    return triage_agent

schedule_agent.handoffs = [transfer_back_to_triage]
networking_agent.handoffs = [transfer_back_to_triage]

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

async def load_user_context(conversation: Dict[str, Any], account_number: str) -> bool:
    """Load user context from database."""
    try:
        # First try to get user by registration_id
        user = await db_client.get_user_by_registration_id(account_number)
        
        # If not found, try by QR code (user ID)
        if not user:
            user = await db_client.get_user_by_qr_code(account_number)
        
        if user:
            # Update context with user information
            conversation["context"].passenger_name = user.get("name")
            conversation["context"].customer_id = user.get("id")
            conversation["context"].account_number = user.get("account_number")
            conversation["context"].customer_email = user.get("email")
            conversation["context"].is_conference_attendee = user.get("is_conference_attendee", True)
            conversation["context"].conference_name = user.get("conference_name", "Business Conference 2025")
            
            # Add additional user details
            conversation["context"].user_company_name = user.get("company")
            conversation["context"].user_location = user.get("location")
            conversation["context"].user_registration_id = user.get("registration_id")
            conversation["context"].user_conference_package = user.get("conference_package")
            conversation["context"].user_primary_stream = user.get("primary_stream")
            conversation["context"].user_secondary_stream = user.get("secondary_stream")
            
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error loading user context: {e}")
        return False

# Export the main components for use in api.py
__all__ = [
    'triage_agent',
    'schedule_agent', 
    'networking_agent',
    'conversations',
    'get_or_create_conversation',
    'load_user_context',
    'relevance_guardrail',
    'jailbreak_guardrail'
]