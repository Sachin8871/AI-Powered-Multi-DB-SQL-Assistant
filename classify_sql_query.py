from langchain.prompts import ChatPromptTemplate
import re

def classify_query_first_word(query: str) -> str:
    if not isinstance(query, str) or not query.strip():
        return "wrong query"

    query = query.strip()

    # Remove comments
    query = re.sub(r"(--[^\n]*\n)|(/\*[\s\S]*?\*/)", "", query, flags=re.IGNORECASE)
    query = query.strip()
    query_lower = re.sub(r'\s+', ' ', query.lower())

    match = re.match(
        r'(\(*\s*)*(with|select|insert|update|delete|create|alter|drop|truncate|rename|grant|revoke|set|show|describe|pragma|explain)',
        query_lower
    )

    if not match:
        return "wrong query"

    keyword = match.group(2)

    retrieval_keywords = {'select', 'show', 'describe', 'pragma', 'explain'}
    modifying_keywords = {
        'insert', 'update', 'delete', 'create', 'alter', 'drop', 'truncate',
        'rename', 'grant', 'revoke', 'set'
    }

    if keyword == 'with':
        return "uncertain"  # could be modifying or retrieval, send to LLM
    if keyword in retrieval_keywords:
        return "retrieve"
    elif keyword in modifying_keywords:
        return "modifying"

    return "wrong query"


def classify_query_model(query : str, model) -> str:
    prompt2 = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Determine if the SQL is:\n"
                "- 'Modifying'\n"
                "- 'Retrieve'\n"
                "- 'Wrong query.'\n"
                "Only return one of those words (Read the entire input, do not decide based only on initial words)."),
        ("human", "{query}")
    ])

    chain2 = prompt2 | model
    response = chain2.invoke({"query": "insert"}).content
    return response


def classify_sql_query_hybrid(query: str, model) -> str:
    result = classify_query_first_word(query)

    if result == "uncertain":
        # Use LLM fallback
        response = classify_query_model(query, model).strip().lower()
        return response

    return result













# def classify_sql_query(query: str) -> str:
#     if not isinstance(query, str) or not query.strip():
#         return "wrong query"
    
#     query = query.strip().lower()
#     # Remove multiple semicolons or whitespaces
#     query = re.sub(r'\s+', ' ', query)

#     retrieval_keywords = ['select', 'show', 'describe', 'pragma', 'explain', 'with']
#     modifying_keywords = [
#         'insert', 'update', 'delete', 'create', 'alter', 'drop', 'truncate',
#         'rename', 'grant', 'revoke', 'set'
#     ]

#     for keyword in retrieval_keywords:
#         if query.startswith(keyword):
#             return "retrieve"

#     for keyword in modifying_keywords:
#         if query.startswith(keyword):
#             return "modifying"

#     return "wrong query"


# keys = ['ADD', 'ALL', 'ALTER', 'AND', 'ANY', 'AS', 'ASC', 'AUTHORIZATION', 'BACKUP', 'BETWEEN', 'BY', 'CASE', 'CHECK', 'COLUMN', 'COMMIT',
#     'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURSOR', 'DATABASE', 'DEFAULT',
#     'DELETE', 'DESC', 'DISTINCT', 'DROP', 'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXISTS', 'EXPLAIN', 'FETCH', 'FOR', 'FOREIGN', 'FROM',
#     'FULL', 'FUNCTION', 'GRANT', 'GROUP', 'HAVING', 'IF', 'IN', 'INDEX', 'INNER', 'INSERT', 'INTERSECT', 'INTO', 'IS', 'JOIN', 'KEY',
#     'LEFT', 'LIKE', 'LIMIT', 'NATURAL', 'NOT', 'NULL', 'OFFSET', 'ON', 'OR', 'ORDER', 'OUTER', 'PRIMARY', 'PROCEDURE', 'REFERENCES',
#     'RETURN', 'REVOKE', 'RIGHT', 'ROLLBACK', 'ROLLUP', 'ROWNUM', 'SAVEPOINT', 'SELECT', 'SET', 'SOME', 'TABLE', 'TOP', 'TRANSACTION',
#     'TRIGGER', 'UNION', 'UNIQUE', 'UPDATE', 'USE', 'VALUES', 'VIEW', 'WHEN', 'WHERE', 'WHILE', 'WITH', 'GROUP BY', 'ORDER BY', 'INNER JOIN',
#     'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'IS NULL', 'IS NOT NULL', 'UNION ALL', 'NOT EXISTS', 'THEN', 'SHOW', 'DESCRIBE', 'PRAGMA',
#     'MERGE', 'SEQUENCE', 'RENAME', 'BEGIN', 'RELEASE SAVEPOINT', 'SET TRANSACTION', 'PRIMARY KEY', 'FOREIGN KEY', 'NOT NULL',
#     'AUTO_INCREMENT', 'IDENTITY', 'SERIAL', 'TRUE', 'FALSE'
# ]
# retrieval_keywords = [
#     'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'OFFSET',
#     'DISTINCT', 'UNION', 'UNION ALL', 'INTERSECT', 'EXCEPT', 'IN', 'LIKE', 
#     'IS', 'IS NULL', 'IS NOT NULL', 'EXISTS', 'NOT EXISTS', 'GROUP', 'ORDER',
#     'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'JOIN', 'ON', 
#     'SHOW', 'DESCRIBE', 'PRAGMA', 'EXPLAIN', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AS'
# ]
# modifier_keywords = [
#     'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'ALTER', 'DROP', 
#     'TRIGGER', 'TABLE', 'VIEW', 'DATABASE', 'COLUMN', 'INDEX', 'CONSTRAINT', 
#     'PRIMARY', 'PRIMARY KEY', 'FOREIGN', 'FOREIGN KEY', 'NOT NULL', 'AUTO_INCREMENT', 
#     'UNIQUE', 'USE', 'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK', 'SAVEPOINT', 'BEGIN', 
#     'TRANSACTION', 'SET TRANSACTION', 'RELEASE SAVEPOINT', 'SEQUENCE', 'MERGE', 
#     'RENAME', 'FUNCTION', 'PROCEDURE', 'IDENTITY', 'SERIAL'
# ]
# other_keywords = [
#     'ADD', 'ALL', 'AND', 'ANY', 'ASC', 'AUTHORIZATION', 'BACKUP', 'BY', 
#     'CHECK', 'CROSS', 'CURRENT', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 
#     'CURSOR', 'DEFAULT', 'DESC', 'ESCAPE', 'FETCH', 'FOR', 'IF', 'KEY', 
#     'LEFT', 'NATURAL', 'NOT', 'NULL', 'OR', 'OUTER', 'REFERENCES', 
#     'ROLLUP', 'ROWNUM', 'SOME', 'TOP', 'TRUE', 'FALSE', 'WHILE', 'WITH'
# ]