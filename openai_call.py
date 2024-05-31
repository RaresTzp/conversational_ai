from langsmith import Client
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import chat_agent_executor
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import os
config = {"configurable": {"thread_id": "abc242"}}


def create_langchain_agent():
    client = Client()

    # Ensure the OpenAI API key is loaded
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
    
    # Initialize the LLM with the API key and enable streaming
    llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key, streaming=True)

    # Load documents
    file_name = "moonlander.docx"
    directory_path = "/Users/rarestapu/Desktop/Experiments/Rag"
    file_path = os.path.join(directory_path, file_name)
    loader = UnstructuredWordDocumentLoader(file_path)
    docs = loader.load()

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=50, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)

    # Create vector store and retriever
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})
    tool = create_retriever_tool(
        retriever,
        "moonlander_info_retriever",
        "Searches and returns excerpts from the Moonlander document.",
    )
    tools = [tool]

    # Create agent executor
    memory = SqliteSaver.from_conn_string(":memory:")
    agent_executor = chat_agent_executor.create_tool_calling_executor(
        llm, tools, checkpointer=memory
    ).with_config({"run_name": "Agent"})
    
  
    return agent_executor

async def query_langchain_agent(agent_executor, query):
    response = []
    for s in agent_executor.stream(
        {"messages": [HumanMessage(content=query)]}, config=config
    ):
        response.append(s)
    return response
