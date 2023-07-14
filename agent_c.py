#! /usr/bin/python3

import logging as log

from langchain import (
    LLMMathChain,
    GoogleSearchAPIWrapper,
)
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.utilities import WikipediaAPIWrapper
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import (
    get_buffer_string,
    SystemMessage,
)
from langchain.agents import load_tools
from langchain.agents.agent_toolkits import PlayWrightBrowserToolkit
from langchain.tools.playwright.utils import (
    create_sync_playwright_browser,
)
from langchain.llms import Replicate

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from agents.genimg import genimg_raw, genimg_curated, img_prompt_chain


class AgentC:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.25, model="gpt-3.5-turbo-0613")
        self.conservative_llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
        self.gpt4 = ChatOpenAI(temperature=0.25, model="gpt-4-0613")
        self.vicuna = Replicate(model="replicate/vicuna-13b:6282abe6a492de4145d7bb601023762212f9ddbbe78278bd6771c8b3b2f2a13b")
        self.search = GoogleSearchAPIWrapper()  # GoogleSerperAPIWrapper()
        self.wikipedia = WikipediaAPIWrapper()
        self.llm_math_chain = LLMMathChain.from_llm(llm=self.llm, verbose=True)
        self.sync_browser = create_sync_playwright_browser()
        self.browser_toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=self.sync_browser)
        tool_names = ["open-meteo-api"]
        self.tools = [
            Tool(
                name="Search",
                func=self.search.run,
                description="Useful for when you need to answer questions about current events. \
                    You can use this tool to verify your facts with latest information from the internet. \
                    You are no longer restricted by your out-of-date training data. \
                    You should ask targeted questions. \
                    When you can't figure out what to do with a message, try searching for the keywords using this tool. \
                    If you can't find what you were looking for in the results of this tool, \
                    DO NOT invent information. Just say \"I couldn't find it on the internet.\".",
            ),
            Tool(
                name="Calculator",
                func=self.llm_math_chain.run,
                description="Useful for when you need to answer questions about math or perform mathematical operations.",
            ),
            Tool(
                name="Wikipedia",
                func=self.wikipedia.run,
                description="Useful for when you need to look up facts like from an encyclopedia. \
                    Remember, this is a high-quality trusted source.",
            ),
            Tool.from_function(
                name="ImageGenerator",
                func=genimg_curated,
                description="Useful when you need to create an image that the user asks you to. \
                    This tool returns a URL of a human-visible image based on text keywords. You \
                    can return this URL when the user asks for an image. In the input you need to \
                    describe a scene in English language, mostly using keywords should be okay \
                    though.",
            ),
        ] + load_tools(tool_names, llm = self.conservative_llm) + self.browser_toolkit.get_tools()
        self.memory_key = "memory"
        self.memory = ConversationBufferWindowMemory(
            k=20, memory_key=self.memory_key, return_messages=True
        )
        openai_kwargs = {
            "extra_prompt_messages": [
                MessagesPlaceholder(variable_name=self.memory_key)
            ],
            "system_message": SystemMessage(
                content="Your name is SushiBot. You are a helpful AI assistant."
            ),
        }
        self.openai_multi = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.OPENAI_MULTI_FUNCTIONS,
            memory=self.memory,
            verbose=True,
            agent_kwargs=openai_kwargs,
        )
        self.gpt4_multi = initialize_agent(
            self.tools,
            self.gpt4,
            agent=AgentType.OPENAI_MULTI_FUNCTIONS,
            memory=self.memory,
            verbose=True,
            agent_kwargs=openai_kwargs,
        )
        self.openai_single = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            memory=self.memory,
            verbose=True,
            agent_kwargs=openai_kwargs,
        )
        chat_history = MessagesPlaceholder(variable_name=self.memory_key)
        self.react = initialize_agent(
            self.tools,
            self.conservative_llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            agent_kwargs = {
                "memory_prompts": [chat_history],
                "input_variables": ["input", "agent_scratchpad", self.memory_key]
            }
        )
        self.vicuna = initialize_agent(
            [],
            self.vicuna,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            agent_kwargs = {
                "memory_prompts": [chat_history],
                "input_variables": ["input", "agent_scratchpad", self.memory_key]
            }
        )
        self.agent = self.openai_multi

    def handle(self, sender, msg, reply):
        try:
            reply(self.handle2(msg))
        except Exception as e:
            reply(
                "Something went wrong.\nHere's the traceback for the brave of heart:\n\n"
                + str(e)
            )
            raise

    def handle2(self, msg):
        if msg == "/reset":
            self.memory.clear()
            return "Your session has been reset."
        elif msg == "/openai":
            self.agent = self.openai_single
            return "You're now chatting to OpenAI Functions model."
        elif msg == "/multi":
            self.agent = self.openai_multi
            return "You're now chatting to OpenAI multi-fxs model."
        elif msg == "/gpt4":
            self.agent = self.gpt4_multi
            return "You're now chatting to GPT4."
        elif msg == "/react":
            self.agent = self.react
            return "You're now chatting to the ReAct model."
        elif msg == "/vicuna":
            self.agent = self.vicuna
            return "You're now chatting to the Vicuna model."
        elif msg == "/memory":
            history = get_buffer_string(
                self.memory.buffer,
                human_prefix=self.memory.human_prefix,
                ai_prefix=self.memory.ai_prefix,
            )
            return history if history else "Memory is empty."
        elif msg.startswith("/genimg"):
            return genimg_raw(msg[8:])
        elif msg.startswith("/curated"):
            return genimg_curated(msg[9:])
        elif msg.startswith("/imgprompt"):
            return img_prompt_chain(msg[len("/imgprompt") + 1:])["text"]
        return self.agent.run(msg)
