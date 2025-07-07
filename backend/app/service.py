import logging
import sys
import os
from langchain_google_community import GoogleDriveLoader
# from langchain_community.document_loaders import GoogleDriveLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from .config import GOOGLE_DRIVE_FOLDER_IDS, LLM_MODEL, LLM_TEMPERATURE

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.vector_store = None
        self.retrieval_chain = None

    def initialize(self):
        """
        LangChain RAG 파이프라인 초기화
        """
        try:
            logger.info("Google Drive에서 문서를 로드합니다.")
            folder_ids = [folder_id.strip() for folder_id in GOOGLE_DRIVE_FOLDER_IDS.split(',')]
            
            all_docs = []
            for folder_id in folder_ids:
                loader = GoogleDriveLoader(
                    folder_id=folder_id,
                    recursive=True,
                    scopes=["https://www.googleapis.com/auth/drive.readonly"]
                )
                try:
                    docs = loader.load()
                    all_docs.extend(docs)
                    logger.info(f"Folder '{folder_id}'에서 {len(docs)}개의 문서를 로드했습니다.")
                except Exception as e:
                    logger.error(f"Folder '{folder_id}'에서 문서를 로드하는 중 오류 발생: {e}", exc_info=True)

            if len(all_docs) == 0:
                logger.info(f"로드된 문서가 없습니다.")
                sys.exit(0)
            logger.info(f"{len(all_docs)}개의 문서를 로드했습니다.")

            logger.info("텍스트를 분할합니다.")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(all_docs)
            logger.info(f"텍스트를 {len(texts)}개의 청크로 분할했습니다.")

            logger.info("임베딩을 생성합니다.")
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

            logger.info("벡터 저장소를 생성합니다.")
            self.vector_store = FAISS.from_documents(texts, embeddings)
            logger.info("벡터 저장소를 성공적으로 생성했습니다.")

            logger.info("Retriever 및 체인을 설정합니다.")
            retriever = self.vector_store.as_retriever()
            prompt = ChatPromptTemplate.from_template("""
                Answer the user's questions based on the below context.
                If you don't know the answer, just say that you don't know.
                
                Context: {context}
                
                Question: {input}
                """)
            llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
            document_chain = create_stuff_documents_chain(llm, prompt)
            self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
            logger.info("Retriever 및 체인을 성공적으로 설정했습니다.")

        except Exception as e:
            logger.error(f"LangChain RAG 파이프라인 초기화 실패: {e}", exc_info=True)
            raise

    def ask(self, question: str) -> str:
        """
        답변 생성
        """
        if not self.retrieval_chain:
            logger.error("RAG 파이프라인이 준비되지 않아서 질문에 답변할 수 없습니다.")
            raise RuntimeError("RAG 파이프라인이 준비되지 않았습니다.")
        
        logger.info(f"질문 처리 시작: {question}")
        response = self.retrieval_chain.invoke({"input": question})
        logger.info("답변을 성공적으로 생성했습니다.")
        return response["answer"]

rag_service = RAGService()
