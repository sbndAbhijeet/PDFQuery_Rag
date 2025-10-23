import streamlit as st
import os
from vector_db import delete_vector_db, create_vector_db
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import os, json
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient

load_dotenv()

if "messages" not in st.session_state:
        st.session_state.messages = []


# Custom CSS to set background
def set_background_image(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background_image("https://media.istockphoto.com/id/1434278254/vector/blue-and-pink-light-panoramic-defocused-blurred-motion-gradient-abstract-background-vector.jpg?s=612x612&w=0&k=20&c=_KXodNw25trgE0xDe0zFnzNiofFgV50aajKpcI9x_8I=")


st.header("PDFQuery 🗣️ (Talk with your pdf)")

with st.sidebar:
    st.header("🔐 Gemini API Configuration")
    st.write(f"If you don't have create one its free: ")
    st.link_button("click here","https://aistudio.google.com/app/apikey")
    api_key_input = st.text_input("Enter Gemini API Key", type="password")

    connect = st.button("Connect")


api_key = ''
if connect:
    if api_key_input:
        st.session_state["gemini_api_key"] = api_key_input
        api_key = api_key_input
        st.success("✅ API key saved in session.")
    else:
        st.error("❌ Please enter a valid API key.")


col1, col2 = st.columns(2)

# To upload and save to uploaded_pdfs
with col1:
    uploaded_file = st.file_uploader("Upload a PDF filie", type='pdf')
    saved_file = ''

    if uploaded_file is not None:
        target_folder = "uploaded_pdfs"
        os.makedirs(target_folder, exist_ok=True)
        save_path = os.path.join(target_folder, uploaded_file.name)
        saved_file = save_path

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File saved to {save_path}")

if uploaded_file is not None:
    with col2:
        # To Delete a pdf after use
        st.write("If you are done with chatting and want to continue with other, it would be good to delete the existing file")
        st.write("If you already uploaded file before and forget to delete then no need to Process again")
        if st.button("Delete PDF"):
            if os.path.exists(saved_file):
                os.remove(saved_file)
                st.success(f"{saved_file} deleted successfully.")
            else:
                st.warning(f"{saved_file} not found.")

            delete_vector_db(uploaded_file.name)

        st.write(f"For Processing your file... ⚙️")
        if st.button("Process"):
            created = create_vector_db(saved_file, uploaded_file)

            if created == True:
                st.success("File has been processed, Now talk with your pdf 😎")
            else:
                st.warning(f"Something went wrong 🤕")

    st.sidebar.header("History")
    st.sidebar.subheader("User Queries:")
    if st.sidebar.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


    if "gemini_api_key" in st.session_state:
        try:
            client = OpenAI(
                api_key=st.session_state["gemini_api_key"],
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

            embedding_model = GoogleGenerativeAIEmbeddings(
                google_api_key=st.session_state["gemini_api_key"],
                model="models/embedding-001"
            )
            st.success("🎉 Gemini client initialized successfully!")
        except Exception as e:
            st.error(f"🚨 Failed to initialize Gemini client: {e}")
    else:
        st.warning("🔑 Please enter your Gemini API key in the sidebar.")


    clientQ = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    collections = clientQ.get_collections().collections
    collection_names = [col.name for col in collections]

    if uploaded_file.name in collection_names:
        vector_db = QdrantVectorStore.from_existing_collection(
            url=qdrant_url,
            collection_name=uploaded_file.name,
            embedding=embedding_model,
            api_key=os.getenv("QDRANT_API_KEY")
        )


    def server_response(user_input):
        search_results = vector_db.similarity_search(query=user_input)

        context = "\n\n\n".join([
            f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results
        ])

        # to be changed
        SYSTEM_PROMPT = """
            You are a helpful assistant that gives detailed, accurate answers based only on the provided document context.

            If you find relevant information in the context, answer the question clearly and concisely.
            If not, say: "I couldn’t find the answer in the provided documents."
            

            Always mention page numbers where relevant information was found.
        """
        USER_MESSAGE = f"""
            Use the following context to answer the question.

            Context:
            {context}

            Question: {user_input}
        """

        messages = st.session_state.messages
        if messages == []:#empty
            messages.append(
                {'role': 'system', 'content': SYSTEM_PROMPT},
            )

        messages.append({"role": "user", "content": USER_MESSAGE})
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=messages
        )

        result = response.choices[0].message.content
        messages.append({"role":"assistant", "content": result})
        st.session_state.messages = messages

        return result


    if uploaded_file is not None:
        st.write("Before chatting please Process Your File")
        
        user_input = st.text_input("Ask Your Doubts")

        if st.button("Submit"):
            if user_input is not None:
                res = server_response(user_input)
                st.write(f"Response\n\n{res}")

                start_index = 1 if st.session_state.messages and st.session_state.messages[0]['role'] == 'system' else 0

                for i in range(start_index, len(st.session_state.messages), 2):

                    try:
                        user_msg = st.session_state.messages[i]
                        bot_msg = st.session_state.messages[i + 1]

                        if user_msg["role"] == "user" and bot_msg["role"] == "assistant":
                            with st.sidebar.expander(f"💭 {user_msg['content'][:40]}{'...' if len(user_msg['content']) > 40 else ''}"):
                                st.markdown(f"**🤖 Answer:**\n\n{bot_msg['content']}")
                    except (IndexError, KeyError, TypeError):
                        continue

            else:
                st.write("No request sent")
