import os
import json
from django.conf import settings
from django.shortcuts import render
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Load environment variables from .env file
load_dotenv()

# Function to load and split text into chunks
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

# Function to create and save vectorstore from text chunks
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    rag_path = os.path.join(settings.BASE_DIR, 'chatbot/media/chatbot')
    vectorstore.save_local(rag_path)

# Function to get the conversational chain with memory and custom prompt
def get_conversation_chain():
    embeddings = OpenAIEmbeddings()
    rag_path = os.path.join(settings.BASE_DIR, 'chatbot/media/chatbot')
    vectorstore = FAISS.load_local(rag_path, embeddings=embeddings, allow_dangerous_deserialization=True)
    llm = ChatOpenAI()
    
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

    # Load prompt from file
    prompt_path = os.path.join(settings.BASE_DIR, 'chatbot/media/chatbot/prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            new_template = f.read()
        conversation_chain.combine_docs_chain.llm_chain.prompt.messages[0].prompt.template = new_template
    except Exception as e:
        print(f"Error loading prompt: {str(e)}")
    
    return conversation_chain

# Django view for handling chatbot interactions
def chatbot_view(request):
    if request.method == 'POST':
        user_question = request.POST.get('question', '')
        data_file_path = os.path.join(settings.BASE_DIR, 'chatbot/media/chatbot/dataRAG.txt')

        # Read the data file and create vectorstore
        try:
            with open(data_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            text_chunks = get_text_chunks(content)
            get_vectorstore(text_chunks)

            # Get the conversation chain and respond to the user's question
            conversation_chain = get_conversation_chain()
            response = conversation_chain.invoke({'question': user_question})

            # Parse the response
    # Parse the response if it's a JSON string
            parsed_response = json.loads(response['answer']) if isinstance(response['answer'], str) else {}
            
            # Destructure the response while omitting artist_details.name
            short_description = parsed_response.get('shortDescription', '')
            artwork_details = parsed_response.get('artworkDetails', {})
            
            # Fetch artist details
            artist_biography = artwork_details.get('artist', {}).get('biography', '')
            artist_nationality = artwork_details.get('artist', {}).get('nationality', '')
            
            # Fetch artworks from the 'otherArtworks' section
            artworks = parsed_response.get('otherArtworks', [])
            
            # Handle image URLs based on the artworks returned
            # if question == 'Tomb of the Diver in Paestrum, Italy':
            #     image_url = '12/images/c5c3c6e2-201c-41f8-bcce-d01365275fab.jpg'
            
            # Fetch the summary
            summary = parsed_response.get('summary', '')
        except json.JSONDecodeError as json_err:
                # Handle JSON decoding errors
            return render(request, 'chatbot/index.html', {
                    'answer': response['answer'],
                    'question': user_question,
                    'error': f"JSON Decode Error: {str(json_err)}"
                })

        # print("title======" , artworks[0]['title'])

        # print(artworks)

        # image_lst = []
        # for artwork in artworks:
        #     image_lst.append(artwork['image_url'])

        with open('chatbot/artists_with_artworks.json', 'r') as file:
            jsonData = json.load(file)

# Print the first element in the loaded JSON data
        # print(jsonData[0])

        # print(image_lst)
        img = []
        for item in jsonData:
            print("-->",item)
            for artsdt in item['artist_with_artworks']['artworks']:       
                for art in artworks:
                    if artsdt['title'] == art['title']:
                        print("1",item)
                        print("2" ,art)
                        img.append(artsdt['image_url'])

        print(img)


            # Render the data into the template with the structured response
        return render(request, 'chatbot/index.html', {
                'response': response,
                'short_description': short_description,
                'artist_biography': artist_biography,
                'artist_nationality': artist_nationality,
                'artworks': artworks,
                'summary': summary,
                'image_urls': img,  # Pass the image URLs to the template
                'question': user_question,
                'answer': response
            })
    else:
        return render(request, 'chatbot/index.html')