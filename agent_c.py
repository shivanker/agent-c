#!/usr/bin/env python3

import logging as log

from langchain import (
    LLMMathChain,
    GoogleSearchAPIWrapper,
)
from langchain.agents import initialize_agent, Tool
from langchain.tools import StructuredTool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.utilities import WikipediaAPIWrapper
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import (
    get_buffer_string,
    SystemMessage,
)

from tools.gnews import top_headlines, HeadlinesInput
from tools.ytsubs import yt_transcript
from tools.reader import ReaderTool
from agents.genimg import genimg_raw, genimg_curated, img_prompt_chain

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class AgentC:

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.25, model="gpt-3.5-turbo-16k-0613")
        self.conservative_llm = ChatOpenAI(
            temperature=0, model="gpt-3.5-turbo-16k-0613"
        )
        self.gpt4 = ChatOpenAI(temperature=0.2, model="gpt-4-0613")
        # self.llama_chat = Replicate(
        #     model="replicate/llama70b-v2-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1"
        # )
        self.search = GoogleSearchAPIWrapper()  # GoogleSerperAPIWrapper()
        self.wikipedia = WikipediaAPIWrapper()
        self.llm_math_chain = LLMMathChain.from_llm(
            llm=self.conservative_llm, verbose=True
        )
        self.basic_tools = [
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
            Tool(
                name="YoutubeTranscriptFetcher",
                func=yt_transcript,
                description="Useful for when you need to fetch the transcript of a YouTube video \
                    to understand it better, find something in it, or to explain it to the user.",
            ),
        ]
        self.tools = (
            self.basic_tools
            + [
                Tool.from_function(
                    name="ImageGenerator",
                    func=genimg_curated,
                    description="Useful when you need to create an image that the user asks you to. \
                    This tool returns a URL of a human-visible image based on text keywords. You \
                    can return this URL when the user asks for an image. In the input you need to \
                    describe a scene in English language, mostly using keywords should be okay \
                    though.",
                ),
                StructuredTool.from_function(
                    name="Headlines",
                    func=top_headlines,
                    description="Useful for when you need to fetch the top news headlines for a given category. \
                    The input should be the category of news you want as a string. This must be one of \
                    general, world, nation, business, technology, entertainment, sports, science or health. \
                    Returns the result in the form of a json string. \
                    If you want to dive deeper into a particular news item, you can browse to the specified URL.",
                    args_schema=HeadlinesInput,
                ),
                ReaderTool(),
            ]
            # + load_tools(["open-meteo-api"], llm=self.conservative_llm)
        )
        self.memory_key = "chat_history"
        self.memory = ConversationBufferWindowMemory(
            k=20, memory_key=self.memory_key, return_messages=True
        )  # return messages is always true in "Window" memory - it's designed for chat agents
        openai_kwargs = {
            "extra_prompt_messages": [
                MessagesPlaceholder(variable_name=self.memory_key)
            ],
            "system_message": SystemMessage(
                content="Your name is SushiBot. You are a helpful AI assistant. Keep the \
                conversation natuarl and flowing, don't respond with closing statements like \
                'Is there anything else?'. If you don't know something, look it up on the \
                internet. If Search results are not useful, try to navigate to known expert \
                websites to fetch real, up-to-date data, and then root your answers to those facts."
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
            self.gpt4,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            agent_kwargs={
                "memory_prompts": [chat_history],
                "input_variables": ["input", "agent_scratchpad", self.memory_key],
            },
        )
        # TODO: Configure temperature, tools
        # Next steps: must use chat model, base model needs very structured prompts, not ideal for signal
        # Need to implement a BaseChatModel::_generate on top of Replicate (which is only an LLM)
        # But also, replicate doesn't expose an api which takes message hisory or roles ....
        # so would probably have to craft a system prompt to make it chat-worthy
        # or look into LLama-API
        # self.llama = initialize_agent(
        #     [],
        #     self.llama_chat,
        #     agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        #     memory=self.memory,
        #     verbose=True,
        # )
        self.agent = self.gpt4_multi

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
        elif msg == "/llama":
            self.agent = self.llama
            return "You're now chatting to the LLama-v2-70B model."
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
            return img_prompt_chain(msg[len("/imgprompt") + 1 :])["text"]
        return self.agent.run(msg)
