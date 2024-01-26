from langchain.agents import initialize_agent, AgentType
# used to create the memory
from langchain.memory import ConversationBufferMemory

from langchain import HuggingFaceHub
from langchain.prompts import MessagesPlaceholder
from langchain.chains import RetrievalQA
from langchain.document_loaders import DirectoryLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# used to create the retrieval tool
from langchain.tools import Tool
import env
import os
import shutil
import glob
from langchain.chains import LLMMathChain
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


class OwnAIChat:
    module_cleanup_required = True
    os.environ["SERPAPI_API_KEY"] = env.SERPAPI_APIKEY
    os.environ['HUGGINGFACEHUB_API_TOKEN'] = env.HUGGINGFACEHUB_API_KEY
    author_file_destination = "data/author_data.txt"
    author_file_source = "author_data/author_data.txt"
    memory_key = "history"
    memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }

    llm = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                         model_kwargs={"temperature": 1,
                                       "min_length": 1024})

    def __init__(self):
        # print("Entered OwnAIChat-> module_cleanup_required: ")
        pass

    def module_cleanup(self):
        if self.module_cleanup_required:
            print("entered: module_cleanup: ", self.module_cleanup_required)
            files_list = glob.glob('/data/*')
            for f in files_list:
                os.remove(f)
            shutil.copyfile(self.author_file_source, self.author_file_destination)
        self.module_cleanup_required = False

    def set_personal_data_tool(self):

        if not os.path.isfile(self.author_file_destination):
            shutil.copyfile(self.author_file_source, self.author_file_destination)

        loader_dic = DirectoryLoader("data/")
        data = loader_dic.load()

        model_name = "sentence-transformers/all-mpnet-base-v2"
        embeddings = HuggingFaceEmbeddings(model_name=model_name)

        # Split
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=10)
        splits = text_splitter.split_documents(data)
        vector_db = Chroma.from_documents(
            documents=splits, embedding=embeddings, collection_name="personal-data"
        )
        # Create embeddings and store in vector_db
        # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # vector_db = DocArrayInMemorySearch.from_documents(splits, embeddings)

        # Define retriever
        # retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 4})
        personal_data = RetrievalQA.from_chain_type(
            llm=self.llm, chain_type="stuff", retriever=vector_db.as_retriever()
        )

        personal_data_tool = Tool(
            name="personal_data",
            func=personal_data.run,
            description='''Always use this tool first to answer, Your top  priority tool, useful for when you need to 
            answer questions about user uploaded content which might be personal data
            Input should be a fully formed question.''',
        )
        return personal_data_tool

    def set_up_agent(self):
        print("Entered : setupAgent")
        personal_data_tool = self.set_personal_data_tool()
        duckduckgo_search = DuckDuckGoSearchAPIWrapper()
        wikipedia = WikipediaAPIWrapper()
        llm_math_chain = LLMMathChain.from_llm(llm=self.llm, verbose=False)

        tools = [
            personal_data_tool,
            Tool(
                name="Search",
                func=duckduckgo_search.run,
                description='''useful for when you need to answer questions about current events. 
                You should ask targeted questions'''
            ),
            Tool(
                name="Calculator",
                func=llm_math_chain.run,
                description="useful for when you need to answer questions about math"
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
                                 memory=self.memory,
                                 verbose=True,
                                 handle_parsing_errors=True)
        return agent


def __del__():
    print(" object destroyed")
