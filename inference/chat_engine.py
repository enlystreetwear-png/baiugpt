from rag.retriever import retrieve_context
import re


def normalize_text(text):
    text = text.lower().strip()

    # remove extra spaces before punctuation
    text = re.sub(r"\s+([?.!,])", r"\1", text)

    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


def is_greeting(text):
    text = normalize_text(text)

    greetings = [
        "hi",
        "hello",
        "hey",
        "hai",
        "good morning",
        "good evening",
        "good afternoon"
    ]

    return text in greetings


def get_simple_response(user_input):
    text = normalize_text(user_input)

    responses = {
        "who are you": "I am BaiuGPT, your local AI assistant.",
        "who are you?": "I am BaiuGPT, your local AI assistant.",

        "what is your name": "My name is BaiuGPT.",
        "what is your name?": "My name is BaiuGPT.",

        "are you good": "Yes, I am working properly. My RAG system can search my local knowledge base.",
        "are you good?": "Yes, I am working properly. My RAG system can search my local knowledge base.",

        "how are you": "I am working well. Ask me something from my knowledge base.",
        "how are you?": "I am working well. Ask me something from my knowledge base."
    }

    return responses.get(text)


def format_rag_answer(context):
    import re

    context = context.strip()

    source_name = "Unknown source"
    source_url = ""

    # Extract source name
    name_match = re.search(r"SOURCE_NAME:\s*(.*?)\s*SOURCE_URL:", context)

    if name_match:
        source_name = name_match.group(1).strip()

    # Extract source URL
    url_match = re.search(r"SOURCE_URL:\s*(.*?)\s*SOURCE_TYPE:", context)

    if url_match:
        source_url = url_match.group(1).strip()

    # Remove source metadata from answer text
    context = re.sub(r"SOURCE_NAME:.*?SOURCE_TYPE:\s*\w+", "", context)

    # Remove citation markers like [1], [citation needed]
    context = re.sub(r"\[[^\]]*\]", "", context)

    # Clean spaces
    context = re.sub(r"\s+", " ", context).strip()

    # Keep first 4 sentences
    sentences = context.split(". ")
    short_answer = ". ".join(sentences[:4])

    if not short_answer.endswith("."):
        short_answer += "."

    if source_url:
        return f"{short_answer}\n\nSource: {source_name}\n{source_url}"

    return short_answer


def answer_question(user_input):
    user_input = user_input.strip()

    if is_greeting(user_input):
        return "Hi! I am BaiuGPT. Ask me anything from my knowledge base."

    simple = get_simple_response(user_input)

    if simple:
        return simple

    context = retrieve_context(user_input, top_k=3)

    if not context:
        return "I do not have enough knowledge about that yet."

    return format_rag_answer(context)