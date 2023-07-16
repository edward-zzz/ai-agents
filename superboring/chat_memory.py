from pydantic import BaseModel
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage


class ChatMemory(BaseModel):
    messages: list[BaseMessage] = []

    class Config:
        arbitrary_types_allowed = True

    def add_message(self, message):
        self.messages.append(message)

    def add_user_message(self, message):
        return self.add_message(HumanMessage(content=message))

    def add_ai_message(self, message):
        return self.add_message(AIMessage(content=message))

    def add_system_message(self, message):
        return self.add_message(SystemMessage(content=message))
