import os
os.environ["OPENAI_API_KEY"] = "sk-proj-8qgEGKv7427e7ytpe2F4T3BlbkFJQK9jLoFPgOVhBMPNv29k"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
db_user = "root"
db_password = ""
db_host = "localhost"
db_name = "chinook"
import openai
from langchain.chains.openai_tools import create_extraction_chain_pydantic
import pandas as pd
import ast  # For potential parsing (use with caution)
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities.sql_database import SQLDatabase
# db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=1,include_tables=['customers','orders'],custom_table_info={'customers':"customer"})
db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
#print(db.dialect)
#print(db.table_info)
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
generate_query = create_sql_query_chain(llm, db)

def get_table_description(create_table_statements):
    response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": f"Create Table Statements:  ['{create_table_statements}']\n"
            }
          ]
        },
        
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "From above table can you describe the table in very short words in layman terms, what can the table be about without using the datatypes "
            }
          ]
        },
      ],
    temperature=1,
    max_tokens=256,
    )
    return response.choices[0].message.content.strip()

def get_create_table_details(table, db):
    execute_query = QuerySQLDataBaseTool(db=db)
    table_details = ""
    query=f"SHOW CREATE TABLE {table}"
    table_info_string = execute_query.invoke(query)
    table_info = ast.literal_eval(table_info_string)
    return(table_info[0][1])
    
def get_table_details_full(db):
    table_description = db.get_usable_table_names()
    table_docs = []
    execute_query = QuerySQLDataBaseTool(db=db)
    datafin = []
    tab_desc =[]
    for index in table_description:
        a= get_create_table_details(index,db)
        print(index)
        print("\n")
        tab_descr=get_table_description(a)
        tab_desc.append(index)
        tab_desc.append(tab_descr)
        datafin.append(tab_desc)
        tab_desc =[]
    header = ['Table', 'Description']
    data = pd.DataFrame(datafin, columns=header)
    data.to_csv('Table_training_data.csv', index=False)
get_table_details_full(db)

