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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# TOOL FUNCTIONS (Direct implementations)
# =========================

async def get_conference_schedule_tool(
    speaker_name: Optional[str] = None,
    topic: Optional[str] = None,
    conference_room_name: Optional[str] = None,
    track_name: Optional[str] = None,
    conference_date: Optional[str] = None
) -> str:
    """Get conference schedule information based on various filters."""
    try:
        # Convert date string to date object if provided
        parsed_date = None
        if conference_date:
            try:
                parsed_date = datetime.strptime(conference_date, "%Y-%m-%d").date()
            except ValueError:
                return f"Invalid date format: {conference_date}. Please use YYYY-MM-DD format."

        # Get schedule from database
        schedule = await db_client.get_conference_schedule(
            speaker_name=speaker_name,
            topic=topic,
            conference_room_name=conference_room_name,
            track_name=track_name,
            conference_date=parsed_date
        )

        if not schedule:
            filters = []
            if speaker_name: filters.append(f"speaker '{speaker_name}'")
            if topic: filters.append(f"topic '{topic}'")
            if conference_room_name: filters.append(f"room '{conference_room_name}'")
            if track_name: filters.append(f"track '{track_name}'")
            if conference_date: filters.append(f"date '{conference_date}'")
            
            filter_text = " and ".join(filters) if filters else "your criteria"
            return f"No conference sessions found for {filter_text}."

        # Format the schedule information
        result = f"Found {len(schedule)} conference session(s):\n\n"
        
        for session in schedule:
            start_time = session.get('start_time', 'TBD')
            end_time = session.get('end_time', 'TBD')
            
            # Format datetime strings if they exist
            if isinstance(start_time, str) and 'T' in start_time:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00')).strftime('%I:%M %p')
            if isinstance(end_time, str) and 'T' in end_time:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00')).strftime('%I:%M %p')
            
            result += f"**{session.get('topic', 'Unknown Topic')}**\n"
            result += f"Speaker: {session.get('speaker_name', 'TBD')}\n"
            result += f"Time: {start_time} - {end_time}\n"
            result += f"Room: {session.get('conference_room_name', 'TBD')}\n"
            result += f"Track: {session.get('track_name', 'TBD')}\n"
            result += f"Date: {session.get('conference_date', 'TBD')}\n"
            
            if session.get('description'):
                result += f"Description: {session.get('description')}\n"
            
            result += "\n"

        return result

    except Exception as e:
        logger.error(f"Error in get_conference_schedule_tool: {e}")
        return f"Error retrieving conference schedule: {str(e)}"

async def search_attendees_tool(
    name: Optional[str] = None,
    limit: int = 10
) -> str:
    """Search for conference attendees by name or get all attendees."""
    try:
        if name:
            # Search by name
            attendees = await db_client.get_user_details_by_name(name)
        else:
            # Get all attendees
            attendees = await db_client.get_all_attendees(limit=limit)

        if not attendees:
            search_text = f"named '{name}'" if name else "in the conference"
            return f"No attendees found {search_text}."

        # Format attendee information
        result = f"Found {len(attendees)} attendee(s):\n\n"
        
        for attendee in attendees:
            details = attendee.get('details', {})
            user_name = details.get('user_name') or f"{details.get('firstName', '')} {details.get('lastName', '')}".strip()
            
            result += f"**{user_name}**\n"
            
            if details.get('company'):
                result += f"Company: {details.get('company')}\n"
            if details.get('location'):
                result += f"Location: {details.get('location')}\n"
            if details.get('primary_stream'):
                result += f"Primary Stream: {details.get('primary_stream')}\n"
            if details.get('secondary_stream'):
                result += f"Secondary Stream: {details.get('secondary_stream')}\n"
            if details.get('conference_package'):
                result += f"Conference Package: {details.get('conference_package')}\n"
            
            result += "\n"

        return result

    except Exception as e:
        logger.error(f"Error in search_attendees_tool: {e}")
        return f"Error searching attendees: {str(e)}"

async def search_businesses_tool(
    query: Optional[str] = None,
    sector: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """Search for businesses by various criteria."""
    try:
        businesses = await db_client.search_businesses(
            query=query,
            sector=sector,
            location=location
        )

        if not businesses:
            filters = []
            if query: filters.append(f"query '{query}'")
            if sector: filters.append(f"sector '{sector}'")
            if location: filters.append(f"location '{location}'")
            
            filter_text = " and ".join(filters) if filters else "your criteria"
            return f"No businesses found for {filter_text}."

        # Format business information
        result = f"Found {len(businesses)} business(es):\n\n"
        
        for business in businesses:
            details = business.get('details', {})
            
            result += f"**{details.get('companyName', 'Unknown Company')}**\n"
            
            if details.get('industrySector'):
                result += f"Industry: {details.get('industrySector')}\n"
            if details.get('subSector'):
                result += f"Sub-sector: {details.get('subSector')}\n"
            if details.get('location'):
                result += f"Location: {details.get('location')}\n"
            if details.get('briefDescription'):
                result += f"Description: {details.get('briefDescription')}\n"
            if details.get('productsOrServices'):
                result += f"Products/Services: {details.get('productsOrServices')}\n"
            if details.get('web'):
                result += f"Website: {details.get('web')}\n"
            
            result += "\n"

        return result

    except Exception as e:
        logger.error(f"Error in search_businesses_tool: {e}")
        return f"Error searching businesses: {str(e)}"

async def get_user_businesses_tool(
    user_id: str,
    user_name: Optional[str] = None
) -> str:
    """Get all businesses for a specific user."""
    try:
        # If no user_name provided, use current user
        if not user_name:
            if not user_id:
                return "No user specified and no current user context available."
        else:
            # Search for user by name first
            users = await db_client.get_user_details_by_name(user_name)
            if not users:
                return f"No user found with name '{user_name}'."
            user_id = users[0].get('id')

        businesses = await db_client.get_user_businesses(user_id)

        if not businesses:
            user_text = user_name or "the current user"
            return f"No businesses found for {user_text}."

        # Format business information
        result = f"Found {len(businesses)} business(es) for {user_name or 'the current user'}:\n\n"
        
        for business in businesses:
            details = business.get('details', {})
            
            result += f"**{details.get('companyName', 'Unknown Company')}**\n"
            
            if details.get('industrySector'):
                result += f"Industry: {details.get('industrySector')}\n"
            if details.get('subSector'):
                result += f"Sub-sector: {details.get('subSector')}\n"
            if details.get('location'):
                result += f"Location: {details.get('location')}\n"
            if details.get('positionTitle'):
                result += f"Position: {details.get('positionTitle')}\n"
            if details.get('briefDescription'):
                result += f"Description: {details.get('briefDescription')}\n"
            if details.get('web'):
                result += f"Website: {details.get('web')}\n"
            
            result += "\n"

        return result

    except Exception as e:
        logger.error(f"Error in get_user_businesses_tool: {e}")
        return f"Error retrieving user businesses: {str(e)}"

async def add_business_tool(
    user_id: str,
    company_name: str,
    industry_sector: str,
    sub_sector: str,
    location: str,
    position_title: str,
    legal_structure: str,
    establishment_year: str,
    products_or_services: str,
    brief_description: str,
    website: Optional[str] = None
) -> str:
    """Add a new business for the current user."""
    try:
        if not user_id:
            return "Unable to add business: No user context available."

        # Prepare business details
        business_details = {
            "companyName": company_name,
            "industrySector": industry_sector,
            "subSector": sub_sector,
            "location": location,
            "positionTitle": position_title,
            "legalStructure": legal_structure,
            "establishmentYear": establishment_year,
            "productsOrServices": products_or_services,
            "briefDescription": brief_description
        }
        
        if website:
            business_details["web"] = website

        # Add business to database
        success = await db_client.add_business(user_id, business_details)

        if success:
            return f"Successfully added business '{company_name}' to your profile. The business is now listed in the business directory and available for networking."
        else:
            return f"Failed to add business '{company_name}'. Please try again or contact support."

    except Exception as e:
        logger.error(f"Error in add_business_tool: {e}")
        return f"Error adding business: {str(e)}"

async def get_organization_info_tool(
    organization_id: Optional[str] = None
) -> str:
    """Get organization information."""
    try:
        if not organization_id:
            return "No organization specified."

        organization = await db_client.get_organization_details(organization_id)

        if not organization:
            return f"No organization found with ID '{organization_id}'."

        # Format organization information
        result = f"**Organization Information**\n\n"
        result += f"Name: {organization.get('name', 'Unknown')}\n"
        
        details = organization.get('details', {})
        if details:
            for key, value in details.items():
                if value:
                    result += f"{key.replace('_', ' ').title()}: {value}\n"

        return result

    except Exception as e:
        logger.error(f"Error in get_organization_info_tool: {e}")
        return f"Error retrieving organization information: {str(e)}"

# =========================
# AGENT EXECUTION FUNCTIONS
# =========================

async def execute_schedule_agent(message: str, context: Dict[str, Any]) -> str:
    """Execute schedule agent logic."""
    try:
        message_lower = message.lower()
        
        # Extract parameters from message
        speaker_name = None
        topic = None
        room_name = None
        track_name = None
        date_str = None
        
        # Simple keyword extraction
        if "alice" in message_lower:
            speaker_name = "Alice Wonderland"
        elif "bob" in message_lower:
            speaker_name = "Bob The Builder"
        elif "charlie" in message_lower:
            speaker_name = "Charlie Chaplin"
        
        if "ai" in message_lower or "ml" in message_lower:
            track_name = "AI & ML"
        elif "cloud" in message_lower:
            track_name = "Cloud Computing"
        elif "data" in message_lower:
            track_name = "Data Science"
        elif "web" in message_lower:
            track_name = "Web Development"
        elif "cyber" in message_lower:
            track_name = "Cybersecurity"
        elif "product" in message_lower:
            track_name = "Product Management"
        elif "startup" in message_lower:
            track_name = "Startup & Entrepreneurship"
        
        if "grand ballroom" in message_lower:
            room_name = "Grand Ballroom"
        elif "executive suite" in message_lower:
            room_name = "Executive Suite 1"
        elif "breakout room a" in message_lower:
            room_name = "Breakout Room A"
        elif "breakout room b" in message_lower:
            room_name = "Breakout Room B"
        elif "innovation hub" in message_lower:
            room_name = "Innovation Hub"
        elif "networking lounge" in message_lower:
            room_name = "Networking Lounge"
        
        if "july 15" in message_lower or "2025-07-15" in message_lower:
            date_str = "2025-07-15"
        elif "july 16" in message_lower or "2025-07-16" in message_lower:
            date_str = "2025-07-16"
        
        # Extract topic keywords
        if "future of ai" in message_lower:
            topic = "The Future of AI in Travel"
        elif "cloud infrastructure" in message_lower:
            topic = "Scaling Cloud Infrastructure for Airlines"
        
        # Call the tool function
        result = await get_conference_schedule_tool(
            speaker_name=speaker_name,
            topic=topic,
            conference_room_name=room_name,
            track_name=track_name,
            conference_date=date_str
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in execute_schedule_agent: {e}")
        return "I'm having trouble accessing the conference schedule. Please try again or contact support."

async def execute_networking_agent(message: str, context: Dict[str, Any]) -> str:
    """Execute networking agent logic."""
    try:
        message_lower = message.lower()
        
        # Handle business form request
        if "add" in message_lower and "business" in message_lower:
            return "DISPLAY_BUSINESS_FORM"
        
        # Handle attendee search
        if "attendee" in message_lower or "show attendees" in message_lower or "find attendees" in message_lower:
            if "from" in message_lower:
                # Extract location
                words = message.split()
                location_idx = -1
                for i, word in enumerate(words):
                    if word.lower() == "from":
                        location_idx = i
                        break
                
                if location_idx != -1 and location_idx + 1 < len(words):
                    location = words[location_idx + 1]
                    # Search by location (this would need to be implemented in the database function)
                    return await search_attendees_tool()
                else:
                    return await search_attendees_tool()
            else:
                return await search_attendees_tool()
        
        # Handle business search
        if "business" in message_lower or "company" in message_lower:
            if "healthcare" in message_lower:
                return await search_businesses_tool(sector="Healthcare")
            elif "it" in message_lower:
                return await search_businesses_tool(sector="IT")
            elif "mumbai" in message_lower:
                return await search_businesses_tool(location="Mumbai")
            elif "chennai" in message_lower:
                return await search_businesses_tool(location="Chennai")
            else:
                return await search_businesses_tool()
        
        # Handle user business lookup
        if "my business" in message_lower and context.get('customer_id'):
            return await get_user_businesses_tool(context['customer_id'])
        
        # Default networking response
        return "I can help you with networking and business connections. You can ask me to:\n\n• **Find attendees** - \"Find attendees from Chennai\" or \"Show me all attendees\"\n• **Search businesses** - \"Find healthcare businesses\" or \"Show me IT companies\"\n• **Add your business** - \"I want to add my business\"\n• **Get business info** - \"Show me businesses in Mumbai\"\n\nWhat networking assistance do you need?"
        
    except Exception as e:
        logger.error(f"Error in execute_networking_agent: {e}")
        return "I'm having trouble accessing the networking information. Please try again or contact support."

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
    'conversations',
    'get_or_create_conversation',
    'load_user_context',
    'execute_schedule_agent',
    'execute_networking_agent',
    'get_conference_schedule_tool',
    'search_attendees_tool',
    'search_businesses_tool',
    'get_user_businesses_tool',
    'add_business_tool',
    'get_organization_info_tool'
]