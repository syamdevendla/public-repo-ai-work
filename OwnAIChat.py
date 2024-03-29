from langchain.agents import initialize_agent, AgentType
# used to create the memory
from langchain.memory import ConversationBufferMemory

from langchain import HuggingFaceHub

from langchain.prompts import MessagesPlaceholder
from langchain.chains import RetrievalQA
from langchain.document_loaders import DirectoryLoader, WebBaseLoader

from langchain.embeddings import HuggingFaceEmbeddings

from langchain.tools import Tool
import env
import os
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from langchain.indexes import VectorstoreIndexCreator


class OwnAIChat:
    module_cleanup_required = True
    os.environ["SERPAPI_API_KEY"] = env.SERPAPI_APIKEY
    os.environ['HUGGINGFACEHUB_API_TOKEN'] = env.HUGGINGFACEHUB_API_KEY
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    memory_key = "history"
    memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
     }

    llm = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                         model_kwargs={"temperature": 0.7,
                                       "max_new_tokens": 1024})

    def __init__(self):
        # print("Entered OwnAIChat-> module_cleanup_required: ")
        pass

    def set_personal_data_tool(self):

        model_name = "sentence-transformers/all-mpnet-base-v2"
        hfembeddings = HuggingFaceEmbeddings(model_name=model_name)

        loader_dic = DirectoryLoader("data/")
        more_data = [
            "https://aws.amazon.com/blogs/devops/using-generative-ai-amazon-bedrock-and-amazon-codeguru-to-improve-code-quality-and-security/"
        ]
        more_data.append("https://aws.amazon.com/blogs/compute/building-a-serverless-document-chat-with-aws-lambda-and-amazon-bedrock/")
        loader_web = WebBaseLoader(more_data) # Use this line if you want to load data from web

        #index = VectorstoreIndexCreator().from_loaders([loader_dic,loader_web])

        index = VectorstoreIndexCreator(embedding=hfembeddings).from_loaders([loader_dic])
        retriever = index.vectorstore.as_retriever(search_kwargs={"k": 2, "fetch_k": 4})

        personal_data = RetrievalQA.from_chain_type(
            llm=self.llm, chain_type="stuff", retriever=retriever
        )

        personal_data_tool = Tool(
            name="personal_data",
            func=personal_data.run,
            description='''useful when you need to answer questions about user uploaded content 
            which might be personal_data or any of his own interest topics.
            Input should be a fully formed question.''',
        )
        return personal_data_tool

    def set_up_agent(self):
        print("Entered : setupAgent")
        personal_data_tool = self.set_personal_data_tool()
        duckduckgo_search = DuckDuckGoSearchAPIWrapper()
        wikipedia = WikipediaAPIWrapper()

        tools = [
            personal_data_tool,
            Tool(
                name="Search",
                func=duckduckgo_search.run,
                description='''useful for when you need to answer questions about current events. 
                You should ask targeted questions'''
            ),
            Tool(
                name="Wikipedia",
                func=wikipedia.run,
                description='''useful when you need an answer about encyclopedic general knowledge 
                but as first priority check with personal_data'''
            )
        ]
        """
        our agent default prompt.
        """
        agent = initialize_agent(tools,
                                 self.llm,
                                 agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                 agent_kwargs=self.agent_kwargs,
                                 verbose=False,
                                 handle_parsing_errors=True)
        return agent


def __del__():
    print(" object destroyed")
