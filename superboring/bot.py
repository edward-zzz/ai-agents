import json
import traceback

from typing import Dict

from pydantic import Extra, BaseModel

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage

from .prompts import SYSTEM_PROMPT
from .chat_memory import ChatMemory
from .console import BotConsole
from .agent import BaseAgent, ChangeTimezoneAgent, SendEmailAgent


class Bot(BaseModel):
    bot_name: str = "SuperBoringBot"
    memory: ChatMemory = ChatMemory()
    agents: Dict[str, BaseAgent] = {}
    # prompt: PromptTemplate = PromptTemplate(
    #     template="You are a chatbot",
    #     input_variables=[],
    # )
    llm: ChatOpenAI = ChatOpenAI(model="gpt-3.5-turbo")
    output_key: str = "text"

    @classmethod
    def init(cls, bot_name):
        memory = ChatMemory()
        bot = Bot(memory=memory, bot_name=bot_name)
        bot.add_agent(ChangeTimezoneAgent())
        bot.add_agent(SendEmailAgent())
        return bot

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def console(self):
        return BotConsole(name=self.bot_name)

    @property
    def system_message(self):
        content = SYSTEM_PROMPT.format(
            bot_name=self.bot_name,
        )
        return SystemMessage(content=content)

    def add_agent(self, agent):
        self.agents[agent.name] = agent

    def predict(self, message):
        self.memory.add_user_message(message)
        messages = [self.system_message] + self.memory.messages
        response = self.llm.predict_messages(
            messages,
            functions=self.get_function_specs(),
        )
        function_call = response.additional_kwargs.get("function_call", None)
        content = response.content
        if function_call:
            content = self.handle_function_call(function_call)

        self.console.ai_print(content)
        return self.memory.add_ai_message(content)

    def handle_function_call(self, params):
        try:
            name, args = self.parse_function_call(params)
            self.validate_arguments(name, args)
            agent = self.agents[name]
            return agent.run(args)
        except Exception:
            self.console.print(traceback.format_exc())

    def validate_arguments(self, name, args):
        agent = self.agents[name]
        if not agent:
            raise ValueError(f"invalid arguments: {name} {args}")

        invalid_args = self.find_invalid_argument(name, args)
        if invalid_args:
            args_desc = invalid_args["properties"]["description"]
            msg = f"Great! In order to continue, you need to provide: {args_desc}"
            self.memory.add_ai_message(msg)
            raise ValueError(f"invalid arguments: {name} {args}")

    def find_invalid_argument(self, name, arguments):
        agent = self.agents[name]
        func_properties = agent.function_specs["parameters"]["properties"]
        for key in arguments:
            value = arguments[key]
            if self.is_argument_valid(value, func_properties[key]["type"]):
                continue
            return {"name": key, "properties": func_properties[key]}
        return {}

    def parse_function_call(self, params):
        name = params.get("name") or ""
        _args = params.get("arguments") or "{}"
        args = self.safe_parse_arguments(_args)
        if self.agents[name]:
            return name, args
        raise ValueError(f"invalid function: name={name} params={params}")

    def safe_parse_arguments(self, args_str):
        try:
            return json.loads(args_str)
        except Exception as e:
            raise ValueError(f"invalid function_call arguments: {args_str}") from e

    def is_argument_valid(self, value, value_type):
        if value_type == "string":
            return value != "" and value != "any" and value is not None
        if value_type == "integer":
            return value > 0
        if value_type == "boolean":
            return True
        return False

    def get_function_specs(self):
        return [self.agents[name].function_specs for name in self.agents]
    
    def run_interactively(self):
        first_question = "Hello! How can I assist you today?"
        self.console.ai_print(first_question)
        self.memory.add_ai_message(first_question)
        while True:
            try:
                user_input = self.console.get_user_input()
                if user_input in ["quit", "q"]:
                    break
                self.predict(user_input)
            except KeyboardInterrupt:
                break
