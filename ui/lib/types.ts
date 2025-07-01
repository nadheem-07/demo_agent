export interface Message {
  id: string
  content: string
  role: "user" | "assistant"
  agent?: string
  timestamp: Date
}

export interface Agent {
  name: string
  description: string
  handoffs: string[]
  tools: string[]
  /** List of input guardrail identifiers for this agent */
  input_guardrails: string[]
}

export type EventType = "message" | "handoff" | "tool_call" | "tool_output" | "context_update" | "guardrail_refusal" | "info" | "hook_call" | "hook_output"

export interface AgentEvent {
  id: string
  type: EventType
  agent: string
  content: string
  timestamp: Date
  metadata?: {
    source_agent?: string
    target_agent?: string
    tool_name?: string
    tool_args?: Record<string, any>
    tool_result?: any
    context_key?: string
    context_value?: any
    changes?: Record<string, any>
    guardrail_name?: string;
  }
}

export interface GuardrailCheck {
  id: string
  name: string
  input: string
  reasoning: string
  passed: boolean
  timestamp: Date
}

// --- Updated interfaces for User Information (Conference-focused) ---

export interface CustomerDetails {
  name?: string;
  account_number?: string;
  email?: string;
  is_conference_attendee?: boolean;
  conference_name?: string;
  registration_id?: string;
  company?: string;
  location?: string;
  conference_package?: string;
  membership_type?: string[];
  primary_stream?: string;
  secondary_stream?: string;
}

export interface BookingDetails {
  id: string;
  confirmation_number: string;
}

export interface CustomerInfoResponse {
  customer?: CustomerDetails;
  bookings: BookingDetails[];
  current_booking?: {
    confirmation_number?: string;
    seat_number?: string;
    flight_number?: string;
  };
}

// --- Update ChatResponse to include customer_info ---

export interface ChatResponse {
  conversation_id: string;
  current_agent: string;
  messages: Array<{ content: string; agent: string }>;
  events: AgentEvent[];
  context: Record<string, any>;
  agents: Agent[];
  guardrails: GuardrailCheck[];
  customer_info?: CustomerInfoResponse;
}