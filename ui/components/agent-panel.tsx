"use client";

import { Bot, User, CalendarDays } from "lucide-react";
import type { Agent, AgentEvent, GuardrailCheck } from "@/lib/types";
import { AgentsList } from "./agents-list";
import { Guardrails } from "./guardrails";
import { ConversationContext } from "./conversation-context";
import { RunnerOutput } from "./runner-output";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface AgentPanelProps {
  agents: Agent[];
  currentAgent: string;
  events: AgentEvent[];
  guardrails: GuardrailCheck[];
  context: {
    passenger_name?: string; // This is now attendee name
    account_number?: string; // This is registration_id or QR code
    customer_email?: string;
    is_conference_attendee?: boolean;
    conference_name?: string;
    user_conference_role?: string;
    user_job_title?: string;
    user_company_name?: string;
    user_bio?: string;
    user_contact_info?: Record<string, any>;
    user_registered_tracks?: string[];
    user_conference_interests?: string[];
    user_personal_schedule_events?: Record<string, any>[];
    [key: string]: any;
  };
  customerInfo?: {
    customer?: {
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
    };
    bookings: {
      id: string;
      confirmation_number: string;
    }[];
  };
}

export function AgentPanel({
  agents,
  currentAgent,
  events,
  guardrails,
  context,
  customerInfo,
}: AgentPanelProps) {
  const activeAgent = agents.find((a) => a.name === currentAgent);
  const runnerEvents = events.filter((e) => e.type !== "message");

  return (
    <div className="w-3/5 h-full flex flex-col border-r border-gray-200 bg-white rounded-xl shadow-sm">
      <div className="bg-blue-600 text-white h-12 px-4 flex items-center gap-3 shadow-sm rounded-t-xl">
        <CalendarDays className="h-5 w-5" />
        <h1 className="font-semibold text-sm sm:text-base lg:text-lg">Conference Assistant</h1>
        <span className="ml-auto text-xs font-light tracking-wide opacity-80">
          Business&nbsp;Conference&nbsp;2025
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50">
        {/* User Info Section */}
        {customerInfo && (
          <div className="mb-6">
            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2 text-blue-800">
                  <User className="h-4 w-4" />
                  Conference Attendee Information
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {/* Name */}
                  {customerInfo.customer?.name && (
                    <div>
                      <span className="text-blue-600 font-medium">Name:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.name}</span>
                    </div>
                  )}
                  {/* Registration ID */}
                  {customerInfo.customer?.registration_id && (
                    <div>
                      <span className="text-blue-600 font-medium">Registration ID:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.registration_id}</span>
                    </div>
                  )}
                  {/* Email */}
                  {customerInfo.customer?.email && (
                    <div className="col-span-2">
                      <span className="text-blue-600 font-medium">Email:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.email}</span>
                    </div>
                  )}
                  {/* Company */}
                  {customerInfo.customer?.company && (
                    <div className="col-span-2">
                      <span className="text-blue-600 font-medium">Company:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.company}</span>
                    </div>
                  )}
                  {/* Location */}
                  {customerInfo.customer?.location && (
                    <div className="col-span-2">
                      <span className="text-blue-600 font-medium">Location:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.location}</span>
                    </div>
                  )}
                  {/* Conference Package */}
                  {customerInfo.customer?.conference_package && (
                    <div className="col-span-2">
                      <span className="text-blue-600 font-medium">Conference Package:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.conference_package}</span>
                    </div>
                  )}
                  {/* Membership Types */}
                  {customerInfo.customer?.membership_type && customerInfo.customer.membership_type.length > 0 && (
                    <div className="col-span-2">
                      <span className="text-blue-600 font-medium">Membership Types:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.membership_type.join(", ")}</span>
                    </div>
                  )}
                  {/* Business Streams */}
                  {customerInfo.customer?.primary_stream && (
                    <div className="col-span-2">
                      <span className="text-blue-600 font-medium">Primary Stream:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.primary_stream}</span>
                    </div>
                  )}
                  {customerInfo.customer?.secondary_stream && (
                    <div className="col-span-2">
                      <span className="text-blue-600 font-medium">Secondary Stream:</span>{" "}
                      <span className="text-gray-800">{customerInfo.customer.secondary_stream}</span>
                    </div>
                  )}
                  {/* Conference Status */}
                  <div className="col-span-2">
                    <span className="text-blue-600 font-medium">Conference Status:</span>{" "}
                    <span className="text-gray-800">
                      {customerInfo.customer?.is_conference_attendee ? "Registered Attendee" : "Not Registered"}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <AgentsList agents={agents} currentAgent={currentAgent} />
        <Guardrails
          guardrails={guardrails}
          inputGuardrails={activeAgent?.input_guardrails ?? []}
        />
        <ConversationContext context={context} />
        <RunnerOutput runnerEvents={runnerEvents} />
      </div>
    </div>
  );
}