from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.models.agent import ChatGPTAgentConfig
from typing import Optional, Dict, Any

class MedicalAppointmentAgentConfig(ChatGPTAgentConfig):
    pass

class MedicalAppointmentAgent(ChatGPTAgent):
    def __init__(self, agent_config: MedicalAppointmentAgentConfig):
        super().__init__(agent_config)
        self.patient_info: Dict[str, Any] = {}
        self.conversation_state = "greeting"

    async def respond(self, human_input: str, conversation_id: str, is_interrupt: bool = False) -> str:
        print(f"Agent responding. Current state: {self.conversation_state}")
        print(f"Human input: {human_input}")
        if self.conversation_state == "greeting":
            self.conversation_state = "name_dob"
            return "May I have your name and date of birth, please?"

        elif self.conversation_state == "name_dob":
            self.patient_info['name_dob'] = human_input
            self.conversation_state = "insurance"
            return "Thank you. Now, can you provide your insurance information, including the payer name and ID?"

        elif self.conversation_state == "insurance":
            self.patient_info['insurance'] = human_input
            self.conversation_state = "referral"
            return "Do you have a referral? If so, to which physician?"

        elif self.conversation_state == "referral":
            self.patient_info['referral'] = human_input
            self.conversation_state = "chief_complaint"
            return "What is the main reason for your visit today?"

        elif self.conversation_state == "chief_complaint":
            self.patient_info['chief_complaint'] = human_input
            self.conversation_state = "demographics"
            return "Could you please provide your address?"

        elif self.conversation_state == "demographics":
            self.patient_info['demographics'] = human_input
            self.conversation_state = "contact_info"
            return "What's the best phone number to reach you?"

        elif self.conversation_state == "contact_info":
            self.patient_info['contact_info'] = human_input
            self.conversation_state = "offer_appointment"
            return "Great. We have the following appointments available: Dr. Smith on Monday at 2 PM, or Dr. Johnson on Tuesday at 10 AM. Which would you prefer?"

        elif self.conversation_state == "offer_appointment":
            self.patient_info['appointment'] = human_input
            self.conversation_state = "confirm"
            return f"Perfect. I've scheduled your appointment for {human_input}. Is there anything else you need?"

        elif self.conversation_state == "confirm":
            self.conversation_state = "end"
            return "Thank you for scheduling with us. You'll receive a text confirmation shortly. Have a great day!"

        else:
            return "I'm sorry, I didn't understand that. Could you please repeat?"
        
        print(f"Agent response: {response}")
        return response
