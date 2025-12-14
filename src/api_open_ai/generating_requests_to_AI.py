from os import getenv
from groq import Groq
from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from config_project.promt import SQL_GENERATION_PROMPT

GROQ_API_KEY = getenv("GROQ_API_KEY")


client = Groq(
    api_key=GROQ_API_KEY,
)

def generate_sql(question_from_user: str) -> str:
    """
    Генерация SQL запроса для обработки запроса пользователя
    :param question_from_user: запрос от пользователя

    :return answer - сгенерированный SQL запрос от неиронки
    """

    # prompt = SQL_GENERATION_PROMPT.format(user_question=question_from_user)
    messages = [
        ChatCompletionSystemMessageParam(role="system", content=SQL_GENERATION_PROMPT),
        ChatCompletionUserMessageParam(role="user", content=question_from_user),
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )
    answer = chat_completion.choices[0].message.content
    return answer

