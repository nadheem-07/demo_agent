# import os
# from supabase import create_client, Client
# from typing import Optional, Dict, Any, List
# import logging
# from datetime import datetime, date

# logger = logging.getLogger(__name__)

# class SupabaseClient:
#     def __init__(self):
#         url = os.getenv("SUPABASE_URL")
#         key = os.getenv("SUPABASE_ANON_KEY")
        
#         if not url or not key:
#             raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables.")
        
#         self.supabase: Client = create_client(url, key)
#         logger.info("Supabase client initialized.")
    
#     async def get_user_by_registration_id(self, registration_id: str) -> Optional[Dict[str, Any]]:
#         """Get user details by registration_id from the details column."""
#         try:
#             logger.debug(f"Querying users table for registration_id: '{registration_id}'")
            
#             # Query users table where details->>'registration_id' matches the input
#             response = self.supabase.table("users").select("*").eq("details->>registration_id", registration_id).execute()
#             logger.debug(f"Supabase response data: {response.data}")
            
#             if response.data:
#                 user = response.data[0]
#                 logger.debug(f"Found user for registration_id: {registration_id}")
                
#                 # Extract details from the JSONB column
#                 details = user.get("details", {})
                
#                 # Create a normalized user object for the context
#                 normalized_user = {
#                     "id": user.get("id"),
#                     "name": details.get("user_name") or f"{details.get('firstName', '')} {details.get('lastName', '')}".strip(),
#                     "account_number": registration_id,  # Use registration_id as account_number for compatibility
#                     "email": details.get("registered_email") or details.get("email"),
#                     "is_conference_attendee": True,  # All users in this table are conference attendees
#                     "conference_name": "Business Conference 2025",  # Default conference name
#                     "registration_id": details.get("registration_id"),
#                     "mobile": details.get("mobile"),
#                     "whatsapp_number": details.get("whatsapp_number"),
#                     "company": details.get("company"),
#                     "location": details.get("location"),
#                     "address": details.get("address"),
#                     "conference_package": details.get("conference_package"),
#                     "membership_type": details.get("membership_type"),
#                     "primary_stream": details.get("primary_stream"),
#                     "secondary_stream": details.get("secondary_stream"),
#                     "food_preference": details.get("food"),
#                     "room_preference": details.get("room"),
#                     "kovil": details.get("kovil"),
#                     "native": details.get("native"),
#                     "gender": details.get("gender"),
#                     "title": details.get("title"),
#                     "organization_id": user.get("organization_id"),
#                     "role_id": user.get("role_id"),
#                     "role_type": user.get("role_type"),
#                     "is_active": user.get("is_active", True),
#                     "created_at": user.get("created_at"),
#                     "updated_at": user.get("updated_at")
#                 }
                
#                 return normalized_user
            
#             logger.debug(f"No user found for registration_id: {registration_id}")
#             return None
#         except Exception as e:
#             logger.error(f"Error fetching user with registration_id {registration_id}: {e}", exc_info=True)
#             return None
    
#     async def get_user_by_qr_code(self, qr_code: str) -> Optional[Dict[str, Any]]:
#         """Get user details by QR code (which is the main user ID)."""
#         try:
#             logger.debug(f"Querying users table for QR code (ID): '{qr_code}'")
            
#             # Query users table by ID (assuming QR code contains the user ID)
#             response = self.supabase.table("users").select("*").eq("id", qr_code).execute()
#             logger.debug(f"Supabase response data: {response.data}")
            
#             if response.data:
#                 user = response.data[0]
#                 logger.debug(f"Found user for QR code: {qr_code}")
                
#                 # Extract details from the JSONB column
#                 details = user.get("details", {})
                
#                 # Create a normalized user object for the context
#                 normalized_user = {
#                     "id": user.get("id"),
#                     "name": details.get("user_name") or f"{details.get('firstName', '')} {details.get('lastName', '')}".strip(),
#                     "account_number": str(details.get("registration_id", qr_code)),  # Use registration_id or fallback to QR code
#                     "email": details.get("registered_email") or details.get("email"),
#                     "is_conference_attendee": True,  # All users in this table are conference attendees
#                     "conference_name": "Business Conference 2025",  # Default conference name
#                     "registration_id": details.get("registration_id"),
#                     "mobile": details.get("mobile"),
#                     "whatsapp_number": details.get("whatsapp_number"),
#                     "company": details.get("company"),
#                     "location": details.get("location"),
#                     "address": details.get("address"),
#                     "conference_package": details.get("conference_package"),
#                     "membership_type": details.get("membership_type"),
#                     "primary_stream": details.get("primary_stream"),
#                     "secondary_stream": details.get("secondary_stream"),
#                     "food_preference": details.get("food"),
#                     "room_preference": details.get("room"),
#                     "kovil": details.get("kovil"),
#                     "native": details.get("native"),
#                     "gender": details.get("gender"),
#                     "title": details.get("title"),
#                     "organization_id": user.get("organization_id"),
#                     "role_id": user.get("role_id"),
#                     "role_type": user.get("role_type"),
#                     "is_active": user.get("is_active", True),
#                     "created_at": user.get("created_at"),
#                     "updated_at": user.get("updated_at")
#                 }
                
#                 return normalized_user
            
#             logger.debug(f"No user found for QR code: {qr_code}")
#             return None
#         except Exception as e:
#             logger.error(f"Error fetching user with QR code {qr_code}: {e}", exc_info=True)
#             return None

#     # Keep the old customer method for backward compatibility (used by airline agents backup)
#     async def get_customer_by_account_number(self, account_number: str) -> Optional[Dict[str, Any]]:
#         """Get customer details by account number, including conference info."""
#         try:
#             logger.debug(f"Querying customers table for account_number: '{account_number}'")
#             # Select all fields, including new conference-related ones
#             response = self.supabase.table("customers").select("*").eq("account_number", account_number).execute()
#             logger.debug(f"Supabase response data: {response.data}")
            
#             if response.data:
#                 logger.debug(f"Found customer for account_number: {account_number}")
#                 return response.data[0]
#             logger.debug(f"No customer found for account_number: {account_number}")
#             return None
#         except Exception as e:
#             logger.error(f"Error fetching customer with account_number {account_number}: {e}", exc_info=True)
#             return None
    
#     async def get_user_profile_by_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
#         """
#         Fetches user profile details, including conference-specific information,
#         from the 'user_profiles' table (or your equivalent) by customer_id.
#         Adjust 'user_profiles' table name and column names as per your Supabase schema.
#         """
#         if not customer_id:
#             logger.warning("Attempted to fetch user profile with empty customer_id.")
#             return None
        
#         logger.debug(f"Fetching user profile for customer_id: {customer_id}")
#         try:
#             # IMPORTANT: Adjust "user_profiles" to your actual table name
#             # IMPORTANT: Adjust the selected columns to match your database schema
#             response = self.supabase.table("user_profiles").select(
#                 "customer_id, conference_role, job_title, company_name, bio, social_media_links, contact_info, registered_tracks, conference_interests, personal_schedule_events"
#             ).eq("customer_id", customer_id).limit(1).execute()
            
#             data = response.data
#             logger.debug(f"Supabase user profile response data: {data}")
#             if data:
#                 return data[0]
#             logger.debug(f"No user profile found for customer_id: {customer_id}")
#             return None
#         except Exception as e:
#             logger.error(f"Error fetching user profile by customer_id: {e}", exc_info=True)
#             return None
    
#     async def get_booking_by_confirmation(self, confirmation_number: str) -> Optional[Dict[str, Any]]:
#         """Get booking details with customer and flight info."""
#         try:
#             response = self.supabase.table("bookings").select("""
#                 *,
#                 customers:customer_id(*),
#                 flights:flight_id(*)
#             """).eq("confirmation_number", confirmation_number).execute()
            
#             if response.data:
#                 logger.debug(f"Found booking for confirmation_number: {confirmation_number}")
#                 return response.data[0]
#             logger.debug(f"No booking found for confirmation_number: {confirmation_number}")
#             return None
#         except Exception as e:
#             logger.error(f"Error fetching booking with confirmation_number {confirmation_number}: {e}", exc_info=True)
#             return None
    
#     async def get_flight_status(self, flight_number: str) -> Optional[Dict[str, Any]]:
#         """Get flight status information."""
#         try:
#             response = self.supabase.table("flights").select("*").eq("flight_number", flight_number).execute()
#             if response.data:
#                 logger.debug(f"Found flight status for flight_number: {flight_number}")
#                 return response.data[0]
#             logger.debug(f"No flight status found for flight_number: {flight_number}")
#             return None
#         except Exception as e:
#             logger.error(f"Error fetching flight status for flight_number {flight_number}: {e}", exc_info=True)
#             return None
    
#     async def update_seat_number(self, confirmation_number: str, new_seat: str) -> bool:
#         """Update seat number for a booking."""
#         try:
#             response = self.supabase.table("bookings").update({
#                 "seat_number": new_seat
#             }).eq("confirmation_number", confirmation_number).execute()
            
#             updated = len(response.data) > 0
#             if updated:
#                 logger.info(f"Successfully updated seat to {new_seat} for confirmation {confirmation_number}.")
#             else:
#                 logger.warning(f"Failed to update seat for confirmation {confirmation_number}: no matching booking found or no change.")
#             return updated
#         except Exception as e:
#             logger.error(f"Error updating seat for confirmation {confirmation_number}: {e}", exc_info=True)
#             return False
    
#     async def cancel_booking(self, confirmation_number: str) -> bool:
#         """Cancel a booking by setting its status to 'Cancelled'."""
#         try:
#             response = self.supabase.table("bookings").update({
#                 "booking_status": "Cancelled"
#             }).eq("confirmation_number", confirmation_number).execute()
            
#             cancelled = len(response.data) > 0
#             if cancelled:
#                 logger.info(f"Successfully cancelled booking with confirmation {confirmation_number}.")
#             else:
#                 logger.warning(f"Failed to cancel booking for confirmation {confirmation_number}: no matching booking found or already cancelled.")
#             return cancelled
#         except Exception as e:
#             logger.error(f"Error cancelling booking for confirmation {confirmation_number}: {e}", exc_info=True)
#             return False
    
#     async def get_bookings_by_customer_id(self, customer_id: str) -> List[Dict[str, Any]]:
#         """Get all bookings for a customer by their customer_id."""
#         try:
#             response = self.supabase.table("bookings").select("""
#                 *,
#                 flights:flight_id(*)
#             """).eq("customer_id", customer_id).execute() 

#             if response.data:
#                 logger.debug(f"Found {len(response.data)} bookings for customer_id: {customer_id}")
#             else:
#                 logger.debug(f"No bookings found for customer_id: {customer_id}")
#             return response.data or []
#         except Exception as e:
#             logger.error(f"Error fetching bookings for customer ID {customer_id}: {e}", exc_info=True)
#             return []

#     async def get_conference_schedule(
#         self,
#         speaker_name: Optional[str] = None,
#         topic: Optional[str] = None,
#         conference_room_name: Optional[str] = None,
#         track_name: Optional[str] = None,
#         conference_date: Optional[date] = None,
#         time_range_start: Optional[datetime] = None,
#         time_range_end: Optional[datetime] = None
#     ) -> List[Dict[str, Any]]:
#         """
#         Fetches conference schedule based on various filters.
#         Converts date objects to ISO format strings for Supabase query.
#         """
#         try:
#             query = self.supabase.table("conference_schedules").select("*")

#             if speaker_name:
#                 query = query.ilike("speaker_name", f"%{speaker_name}%")
#             if topic:
#                 query = query.ilike("topic", f"%{topic}%")
#             if conference_room_name:
#                 query = query.ilike("conference_room_name", f"%{conference_room_name}%")
#             if track_name:
#                 query = query.ilike("track_name", f"%{track_name}%")
#             if conference_date:
#                 query = query.eq("conference_date", conference_date.isoformat()) # Convert date to ISO string
#             if time_range_start:
#                 query = query.gte("start_time", time_range_start.isoformat()) # Convert datetime to ISO string
#             if time_range_end:
#                 query = query.lte("end_time", time_range_end.isoformat()) # Convert datetime to ISO string

#             response = query.order("start_time").execute() # Order by time for better readability
            
#             if response.data:
#                 logger.debug(f"Found {len(response.data)} conference sessions.")
#             else:
#                 logger.debug("No conference sessions found for the given criteria.")
#             return response.data or []
#         except Exception as e:
#             logger.error(f"Error fetching conference schedule: {e}", exc_info=True)
#             return []

#     async def get_customer_bookings(self, account_number: str) -> List[Dict[str, Any]]:
#         """
#         [NOTE: This method might not be correctly configured for Supabase RLS policies
#         or table relationships if 'customers.account_number' is not directly queryable
#         through the 'bookings' table for security reasons. 
#         'get_bookings_by_customer_id' is generally more robust.]

#         Get all bookings for a customer by their account number.
#         """
#         try:
#             # This query assumes a direct join or RLS setup that allows filtering
#             # bookings by a customer's account_number through a foreign key relationship.
#             response = self.supabase.table("bookings").select("""
#                 *,
#                 flights:flight_id(*)
#             """).eq("customers.account_number", account_number).execute()
#             if response.data:
#                 logger.debug(f"Found {len(response.data)} bookings for account_number: {account_number}")
#             else:
#                 logger.debug(f"No bookings found for account_number: {account_number}")
#             return response.data or []
#         except Exception as e:
#             logger.error(f"Error fetching customer bookings for account {account_number}: {e}", exc_info=True)
#             return []
    
#     async def save_conversation(self, session_id: str, history: List[Dict], context: Dict, current_agent: str) -> bool:
#         """Save or update conversation state to the 'conversations' table."""
#         try:
#             data = {
#                 "session_id": session_id,
#                 "history": history,
#                 "context": context,
#                 "current_agent": current_agent,
#                 "last_updated": "now()"
#             }
            
#             response = self.supabase.table("conversations").upsert(data).execute()
            
#             upserted = len(response.data) > 0
#             if upserted:
#                 logger.debug(f"Conversation {session_id} successfully saved/updated.")
#             else:
#                 logger.warning(f"Failed to upsert conversation {session_id}.")
#             return upserted
#         except Exception as e:
#             logger.error(f"Error saving conversation {session_id}: {e}", exc_info=True)
#             return False
    
#     async def load_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
#         """Load conversation state from the 'conversations' table."""
#         try:
#             response = self.supabase.table("conversations").select("*").eq("session_id", session_id).execute()
#             if response.data:
#                 logger.debug(f"Conversation {session_id} successfully loaded.")
#                 return response.data[0]
#             logger.debug(f"No conversation found for session_id: {session_id}.")
#             return None
#         except Exception as e:
#             logger.error(f"Error loading conversation {session_id}: {e}", exc_info=True)
#             return None

# # Global instance of SupabaseClient
# db_client = SupabaseClient()























import os
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables.")
        
        self.supabase: Client = create_client(url, key)
        logger.info("Supabase client initialized.")
    
    async def get_user_by_registration_id(self, registration_id: str) -> Optional[Dict[str, Any]]:
        """Get user details by registration_id from the details column."""
        try:
            logger.debug(f"Querying users table for registration_id: '{registration_id}'")
            
            # Query users table where details->>'registration_id' matches the input
            response = self.supabase.table("users").select("*").eq("details->>registration_id", registration_id).execute()
            logger.debug(f"Supabase response data: {response.data}")
            
            if response.data:
                user = response.data[0]
                logger.debug(f"Found user for registration_id: {registration_id}")
                
                # Extract details from the JSONB column
                details = user.get("details", {})
                
                # Create a normalized user object for the context
                normalized_user = {
                    "id": user.get("id"),
                    "name": details.get("user_name") or f"{details.get('firstName', '')} {details.get('lastName', '')}".strip(),
                    "account_number": registration_id,  # Use registration_id as account_number for compatibility
                    "email": details.get("registered_email") or details.get("email"),
                    "is_conference_attendee": True,  # All users in this table are conference attendees
                    "conference_name": "Business Conference 2025",  # Default conference name
                    "registration_id": details.get("registration_id"),
                    "mobile": details.get("mobile"),
                    "whatsapp_number": details.get("whatsapp_number"),
                    "company": details.get("company"),
                    "location": details.get("location"),
                    "address": details.get("address"),
                    "conference_package": details.get("conference_package"),
                    "membership_type": details.get("membership_type"),
                    "primary_stream": details.get("primary_stream"),
                    "secondary_stream": details.get("secondary_stream"),
                    "food_preference": details.get("food"),
                    "room_preference": details.get("room"),
                    "kovil": details.get("kovil"),
                    "native": details.get("native"),
                    "gender": details.get("gender"),
                    "title": details.get("title"),
                    "organization_id": user.get("organization_id"),
                    "role_id": user.get("role_id"),
                    "role_type": user.get("role_type"),
                    "is_active": user.get("is_active", True),
                    "created_at": user.get("created_at"),
                    "updated_at": user.get("updated_at")
                }
                
                return normalized_user
            
            logger.debug(f"No user found for registration_id: {registration_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user with registration_id {registration_id}: {e}", exc_info=True)
            return None
    
    async def get_user_by_qr_code(self, qr_code: str) -> Optional[Dict[str, Any]]:
        """Get user details by QR code (which is the main user ID)."""
        try:
            logger.debug(f"Querying users table for QR code (ID): '{qr_code}'")
            
            # Query users table by ID (assuming QR code contains the user ID)
            response = self.supabase.table("users").select("*").eq("id", qr_code).execute()
            logger.debug(f"Supabase response data: {response.data}")
            
            if response.data:
                user = response.data[0]
                logger.debug(f"Found user for QR code: {qr_code}")
                
                # Extract details from the JSONB column
                details = user.get("details", {})
                
                # Create a normalized user object for the context
                normalized_user = {
                    "id": user.get("id"),
                    "name": details.get("user_name") or f"{details.get('firstName', '')} {details.get('lastName', '')}".strip(),
                    "account_number": str(details.get("registration_id", qr_code)),  # Use registration_id or fallback to QR code
                    "email": details.get("registered_email") or details.get("email"),
                    "is_conference_attendee": True,  # All users in this table are conference attendees
                    "conference_name": "Business Conference 2025",  # Default conference name
                    "registration_id": details.get("registration_id"),
                    "mobile": details.get("mobile"),
                    "whatsapp_number": details.get("whatsapp_number"),
                    "company": details.get("company"),
                    "location": details.get("location"),
                    "address": details.get("address"),
                    "conference_package": details.get("conference_package"),
                    "membership_type": details.get("membership_type"),
                    "primary_stream": details.get("primary_stream"),
                    "secondary_stream": details.get("secondary_stream"),
                    "food_preference": details.get("food"),
                    "room_preference": details.get("room"),
                    "kovil": details.get("kovil"),
                    "native": details.get("native"),
                    "gender": details.get("gender"),
                    "title": details.get("title"),
                    "organization_id": user.get("organization_id"),
                    "role_id": user.get("role_id"),
                    "role_type": user.get("role_type"),
                    "is_active": user.get("is_active", True),
                    "created_at": user.get("created_at"),
                    "updated_at": user.get("updated_at")
                }
                
                return normalized_user
            
            logger.debug(f"No user found for QR code: {qr_code}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user with QR code {qr_code}: {e}", exc_info=True)
            return None

    # Keep the old customer method for backward compatibility (used by airline agents backup)
    async def get_customer_by_account_number(self, account_number: str) -> Optional[Dict[str, Any]]:
        """Get customer details by account number, including conference info."""
        try:
            logger.debug(f"Querying customers table for account_number: '{account_number}'")
            # Select all fields, including new conference-related ones
            response = self.supabase.table("customers").select("*").eq("account_number", account_number).execute()
            logger.debug(f"Supabase response data: {response.data}")
            
            if response.data:
                logger.debug(f"Found customer for account_number: {account_number}")
                return response.data[0]
            logger.debug(f"No customer found for account_number: {account_number}")
            return None
        except Exception as e:
            logger.error(f"Error fetching customer with account_number {account_number}: {e}", exc_info=True)
            return None
    
    async def get_user_profile_by_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches user profile details, including conference-specific information,
        from the 'user_profiles' table (or your equivalent) by customer_id.
        Adjust 'user_profiles' table name and column names as per your Supabase schema.
        """
        if not customer_id:
            logger.warning("Attempted to fetch user profile with empty customer_id.")
            return None
        
        logger.debug(f"Fetching user profile for customer_id: {customer_id}")
        try:
            # IMPORTANT: Adjust "user_profiles" to your actual table name
            # IMPORTANT: Adjust the selected columns to match your database schema
            response = self.supabase.table("user_profiles").select(
                "customer_id, conference_role, job_title, company_name, bio, social_media_links, contact_info, registered_tracks, conference_interests, personal_schedule_events"
            ).eq("customer_id", customer_id).limit(1).execute()
            
            data = response.data
            logger.debug(f"Supabase user profile response data: {data}")
            if data:
                return data[0]
            logger.debug(f"No user profile found for customer_id: {customer_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user profile by customer_id: {e}", exc_info=True)
            return None

    # New methods for networking agent
    async def get_user_details_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Get user details by name (fuzzy search)."""
        try:
            logger.debug(f"Searching for users with name: '{name}'")
            
            # Search in details->>'user_name' and also in firstName/lastName combinations
            response = self.supabase.table("users").select("*").or_(
                f"details->>user_name.ilike.%{name}%,"
                f"details->>firstName.ilike.%{name}%,"
                f"details->>lastName.ilike.%{name}%"
            ).execute()
            
            if response.data:
                logger.debug(f"Found {len(response.data)} users matching name: {name}")
                return response.data
            
            logger.debug(f"No users found matching name: {name}")
            return []
        except Exception as e:
            logger.error(f"Error searching users by name {name}: {e}", exc_info=True)
            return []

    async def get_all_attendees(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all conference attendees."""
        try:
            logger.debug(f"Fetching all attendees (limit: {limit})")
            
            response = self.supabase.table("users").select("*").eq("is_active", True).limit(limit).execute()
            
            if response.data:
                logger.debug(f"Found {len(response.data)} attendees")
                return response.data
            
            logger.debug("No attendees found")
            return []
        except Exception as e:
            logger.error(f"Error fetching attendees: {e}", exc_info=True)
            return []

    async def get_user_businesses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all businesses for a user."""
        try:
            logger.debug(f"Fetching businesses for user_id: {user_id}")
            
            response = self.supabase.table("ib_businesses").select("*").eq("user_id", user_id).eq("is_active", True).execute()
            
            if response.data:
                logger.debug(f"Found {len(response.data)} businesses for user: {user_id}")
                return response.data
            
            logger.debug(f"No businesses found for user: {user_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching businesses for user {user_id}: {e}", exc_info=True)
            return []

    async def search_businesses(self, query: str = None, sector: str = None, location: str = None) -> List[Dict[str, Any]]:
        """Search businesses by various criteria."""
        try:
            logger.debug(f"Searching businesses with query: '{query}', sector: '{sector}', location: '{location}'")
            
            query_builder = self.supabase.table("ib_businesses").select("*").eq("is_active", True)
            
            if query:
                query_builder = query_builder.or_(
                    f"details->>companyName.ilike.%{query}%,"
                    f"details->>briefDescription.ilike.%{query}%,"
                    f"details->>productsOrServices.ilike.%{query}%"
                )
            
            if sector:
                query_builder = query_builder.ilike("details->>industrySector", f"%{sector}%")
            
            if location:
                query_builder = query_builder.ilike("details->>location", f"%{location}%")
            
            response = query_builder.limit(50).execute()
            
            if response.data:
                logger.debug(f"Found {len(response.data)} businesses")
                return response.data
            
            logger.debug("No businesses found")
            return []
        except Exception as e:
            logger.error(f"Error searching businesses: {e}", exc_info=True)
            return []

    async def add_business(self, user_id: str, business_details: Dict[str, Any]) -> bool:
        """Add a new business for a user."""
        try:
            logger.debug(f"Adding business for user_id: {user_id}")
            
            data = {
                "user_id": user_id,
                "details": business_details,
                "is_active": True,
                "created_at": "now()"
            }
            
            response = self.supabase.table("ib_businesses").insert(data).execute()
            
            success = len(response.data) > 0
            if success:
                logger.info(f"Successfully added business for user: {user_id}")
            else:
                logger.warning(f"Failed to add business for user: {user_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error adding business for user {user_id}: {e}", exc_info=True)
            return False

    async def get_organization_details(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization details."""
        try:
            logger.debug(f"Fetching organization details for: {organization_id}")
            
            response = self.supabase.table("organizations").select("*").eq("id", organization_id).execute()
            
            if response.data:
                logger.debug(f"Found organization: {organization_id}")
                return response.data[0]
            
            logger.debug(f"No organization found: {organization_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching organization {organization_id}: {e}", exc_info=True)
            return None

    async def get_role_details(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Get role details."""
        try:
            logger.debug(f"Fetching role details for: {role_id}")
            
            response = self.supabase.table("roles").select("*").eq("id", role_id).execute()
            
            if response.data:
                logger.debug(f"Found role: {role_id}")
                return response.data[0]
            
            logger.debug(f"No role found: {role_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching role {role_id}: {e}", exc_info=True)
            return None
    
    async def get_booking_by_confirmation(self, confirmation_number: str) -> Optional[Dict[str, Any]]:
        """Get booking details with customer and flight info."""
        try:
            response = self.supabase.table("bookings").select("""
                *,
                customers:customer_id(*),
                flights:flight_id(*)
            """).eq("confirmation_number", confirmation_number).execute()
            
            if response.data:
                logger.debug(f"Found booking for confirmation_number: {confirmation_number}")
                return response.data[0]
            logger.debug(f"No booking found for confirmation_number: {confirmation_number}")
            return None
        except Exception as e:
            logger.error(f"Error fetching booking with confirmation_number {confirmation_number}: {e}", exc_info=True)
            return None
    
    async def get_flight_status(self, flight_number: str) -> Optional[Dict[str, Any]]:
        """Get flight status information."""
        try:
            response = self.supabase.table("flights").select("*").eq("flight_number", flight_number).execute()
            if response.data:
                logger.debug(f"Found flight status for flight_number: {flight_number}")
                return response.data[0]
            logger.debug(f"No flight status found for flight_number: {flight_number}")
            return None
        except Exception as e:
            logger.error(f"Error fetching flight status for flight_number {flight_number}: {e}", exc_info=True)
            return None
    
    async def update_seat_number(self, confirmation_number: str, new_seat: str) -> bool:
        """Update seat number for a booking."""
        try:
            response = self.supabase.table("bookings").update({
                "seat_number": new_seat
            }).eq("confirmation_number", confirmation_number).execute()
            
            updated = len(response.data) > 0
            if updated:
                logger.info(f"Successfully updated seat to {new_seat} for confirmation {confirmation_number}.")
            else:
                logger.warning(f"Failed to update seat for confirmation {confirmation_number}: no matching booking found or no change.")
            return updated
        except Exception as e:
            logger.error(f"Error updating seat for confirmation {confirmation_number}: {e}", exc_info=True)
            return False
    
    async def cancel_booking(self, confirmation_number: str) -> bool:
        """Cancel a booking by setting its status to 'Cancelled'."""
        try:
            response = self.supabase.table("bookings").update({
                "booking_status": "Cancelled"
            }).eq("confirmation_number", confirmation_number).execute()
            
            cancelled = len(response.data) > 0
            if cancelled:
                logger.info(f"Successfully cancelled booking with confirmation {confirmation_number}.")
            else:
                logger.warning(f"Failed to cancel booking for confirmation {confirmation_number}: no matching booking found or already cancelled.")
            return cancelled
        except Exception as e:
            logger.error(f"Error cancelling booking for confirmation {confirmation_number}: {e}", exc_info=True)
            return False
    
    async def get_bookings_by_customer_id(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a customer by their customer_id."""
        try:
            response = self.supabase.table("bookings").select("""
                *,
                flights:flight_id(*)
            """).eq("customer_id", customer_id).execute() 

            if response.data:
                logger.debug(f"Found {len(response.data)} bookings for customer_id: {customer_id}")
            else:
                logger.debug(f"No bookings found for customer_id: {customer_id}")
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching bookings for customer ID {customer_id}: {e}", exc_info=True)
            return []

    async def get_conference_schedule(
        self,
        speaker_name: Optional[str] = None,
        topic: Optional[str] = None,
        conference_room_name: Optional[str] = None,
        track_name: Optional[str] = None,
        conference_date: Optional[date] = None,
        time_range_start: Optional[datetime] = None,
        time_range_end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches conference schedule based on various filters.
        Converts date objects to ISO format strings for Supabase query.
        """
        try:
            query = self.supabase.table("conference_schedules").select("*")

            if speaker_name:
                query = query.ilike("speaker_name", f"%{speaker_name}%")
            if topic:
                query = query.ilike("topic", f"%{topic}%")
            if conference_room_name:
                query = query.ilike("conference_room_name", f"%{conference_room_name}%")
            if track_name:
                query = query.ilike("track_name", f"%{track_name}%")
            if conference_date:
                query = query.eq("conference_date", conference_date.isoformat()) # Convert date to ISO string
            if time_range_start:
                query = query.gte("start_time", time_range_start.isoformat()) # Convert datetime to ISO string
            if time_range_end:
                query = query.lte("end_time", time_range_end.isoformat()) # Convert datetime to ISO string

            response = query.order("start_time").execute() # Order by time for better readability
            
            if response.data:
                logger.debug(f"Found {len(response.data)} conference sessions.")
            else:
                logger.debug("No conference sessions found for the given criteria.")
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching conference schedule: {e}", exc_info=True)
            return []

    async def get_customer_bookings(self, account_number: str) -> List[Dict[str, Any]]:
        """
        [NOTE: This method might not be correctly configured for Supabase RLS policies
        or table relationships if 'customers.account_number' is not directly queryable
        through the 'bookings' table for security reasons. 
        'get_bookings_by_customer_id' is generally more robust.]

        Get all bookings for a customer by their account number.
        """
        try:
            # This query assumes a direct join or RLS setup that allows filtering
            # bookings by a customer's account_number through a foreign key relationship.
            response = self.supabase.table("bookings").select("""
                *,
                flights:flight_id(*)
            """).eq("customers.account_number", account_number).execute()
            if response.data:
                logger.debug(f"Found {len(response.data)} bookings for account_number: {account_number}")
            else:
                logger.debug(f"No bookings found for account_number: {account_number}")
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching customer bookings for account {account_number}: {e}", exc_info=True)
            return []
    
    async def save_conversation(self, session_id: str, history: List[Dict], context: Dict, current_agent: str) -> bool:
        """Save or update conversation state to the 'conversations' table."""
        try:
            data = {
                "session_id": session_id,
                "history": history,
                "context": context,
                "current_agent": current_agent,
                "last_updated": "now()"
            }
            
            response = self.supabase.table("conversations").upsert(data).execute()
            
            upserted = len(response.data) > 0
            if upserted:
                logger.debug(f"Conversation {session_id} successfully saved/updated.")
            else:
                logger.warning(f"Failed to upsert conversation {session_id}.")
            return upserted
        except Exception as e:
            logger.error(f"Error saving conversation {session_id}: {e}", exc_info=True)
            return False
    
    async def load_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation state from the 'conversations' table."""
        try:
            response = self.supabase.table("conversations").select("*").eq("session_id", session_id).execute()
            if response.data:
                logger.debug(f"Conversation {session_id} successfully loaded.")
                return response.data[0]
            logger.debug(f"No conversation found for session_id: {session_id}.")
            return None
        except Exception as e:
            logger.error(f"Error loading conversation {session_id}: {e}", exc_info=True)
            return None

# Global instance of SupabaseClient
db_client = SupabaseClient()