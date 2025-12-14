from src.api_open_ai.generating_requests_to_AI import generate_sql
from src.database.db_selectors import direct_sql_requests


async def get_answer(question:str):
    query = generate_sql(
        question_from_user=question
    )
    result = direct_sql_requests(sql_query=query)
    print('РУЗУЛЬТАТ ИЗ БД', result)
    return result