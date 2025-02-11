# importing libraries
import Levenshtein
from Levenshtein import distance as levenshtein_distance
import openai
import os
import pandas as pd
from openai import OpenAI
import numpy as np
from io import StringIO
import plotly.express as px
import prompts
import prompts_brand_share
import streamlit as st
import sqlite3
import smart_search
import json

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]


def guardial_classification_prompt(question):
  prompt=prompts.GUARDRAIL_CLASSIFICATION_PROMPT.format(conversation_history='', question=question)
  completion = client.chat.completions.create(
      model="gpt-4o",
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {
              "role": "user",
              "content": prompt
          }
      ],temperature=0.4
  )
  return completion.choices[0].message.content.replace('```python', '').replace('```', '').strip()


def answer_data(question):
      prompt=prompts.KPI_PROMPT.format(conversation_history='', question=question)
      completion = client.chat.completions.create(
      model="gpt-4o",
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {
              "role": "user",
              "content": prompt
          }
          ],temperature=0.4)
      text = completion.choices[0].message.content
      return text



def scope_classification_prompt(query):
    prompt = prompts.SCOPE_CLASSIFICATION_PROMPT.format(question=query.strip())
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    raw_response = completion.choices[0].message.content.strip()
    return json.loads(raw_response.replace('```json', '').replace('```', '').strip())


def classify_domain(question):
    prompt=prompts.DOMAIN_PROMPT.format(conversation_history='', question=question)
    completion = client.chat.completions.create(model="gpt-4o",
                                                messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                          {"role": "user", "content": prompt}],temperature=0.4)
    text = completion.choices[0].message.content
    return text


def ner(question):
    ner_prompt = prompts.NER_PROMPT.format(input_text=question)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": ner_prompt}],
        temperature=0.4
        )
    result = completion.choices[0].message 
    return eval(result.content.replace('```json', '').replace('```', '').strip())

def ner_brand(question):
    ner_prompt = prompts_brand_share.NER_PROMPT.format(input_text=question)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": ner_prompt}],
        temperature=0.4
        )
    result = completion.choices[0].message 
    return eval(result.content.replace('```json', '').replace('```', '').strip())


def find_state(scode, state_entity_list):
    to_replace = []
    replace_by = []
    for state in state_entity_list:
        all_matches = []
        for value in list(scode.keys()):
            similarity = 1 - (levenshtein_distance(state.lower(), value.lower()) / max(len(state), len(value)))
            all_matches.append({'state':value, 'similarity':similarity})
        all_matches.sort(key=lambda x: x["similarity"], reverse=True)
        if (all_matches[0]['similarity']>0.6):
            to_replace.append(state)
            replace_by.append(scode[all_matches[0]['state']])

    for z in range(len(to_replace)):
        ind = state_entity_list.index(to_replace[z])
        state_entity_list[ind] = replace_by[z]
    print('New Entity List : ', state_entity_list)
    return state_entity_list


def find_entities(entity_dict, selected_pairs):
    to_replace = []
    replace_by = []
    for k, v in entity_dict.items():
        if k in ['State', 'City']:
            pass
        else:
            if v:
                for query_value in v:
                    #print(query_value)
                    all_matches = []
                    for value in prompts.UNIQUE_VALUES[prompts.SEARCH_DICT[k][0]]:
                        #print(value)
                        if k=='Hospital':
                            name = value[0]
                            loc = value[1]
                        else:
                            name = value
                            loc = ''
                        similarity = 1 - (levenshtein_distance(query_value.lower(), name.lower()) / max(len(query_value), len(name)))
                        #print(similarity)
                        all_matches.append({'hosp':name, 'loc':loc, 'similarity':similarity})
                    temp = pd.DataFrame(all_matches, columns=['hosp', 'loc', 'similarity']).sort_values('similarity', ascending = False)
                    temp2 = temp[temp['similarity']>0.2][:10].sort_values('similarity', ascending = False)
                    print(temp2)
                    if len(temp2)==0:
                        print('No Matches')
                    #elif len(temp2)==1:
                    else:
                        print(query_value, 'changed to', temp2['hosp'].iloc[0])
                        ind = entity_dict[k].index(query_value)
                        entity_dict[k][ind] = temp2['hosp'].iloc[0].lower()
                        selected_pairs[temp2['hosp'].iloc[0].lower()] = {'column': prompts.SEARCH_DICT[k][0]}
    return entity_dict, selected_pairs


def find_entities_brand(entity_dict, selected_pairs):
    to_replace = []
    replace_by = []
    for k, v in entity_dict.items():
        if v:
            for query_value in v:
                #print(query_value)
                all_matches = []
                for value in prompts_brand_share.BRAND_SHARE_UNIQUE_VALUES[prompts_brand_share.SEARCH_DICT[k][0]]:
                    #print(value)
                    name = value
                    loc = ''
                    similarity = 1 - (levenshtein_distance(query_value.lower(), name.lower()) / max(len(query_value), len(name)))
                    #print(similarity)
                    all_matches.append({'hosp':name, 'loc':loc, 'similarity':similarity})
                temp = pd.DataFrame(all_matches, columns=['hosp', 'loc', 'similarity']).sort_values('similarity', ascending = False)
                temp2 = temp[temp['similarity']>0.2][:10].sort_values('similarity', ascending = False)
                print(temp2)
                if len(temp2)==0:
                    print('No Matches')
                #elif len(temp2)==1:
                else:
                    print(query_value, 'changed to', temp2['hosp'].iloc[0])
                    ind = entity_dict[k].index(query_value)
                    entity_dict[k][ind] = temp2['hosp'].iloc[0].lower()
                    selected_pairs[temp2['hosp'].iloc[0].lower()] = {'column': prompts_brand_share.SEARCH_DICT[k][0]}
    return entity_dict, selected_pairs


def spell_check_entities(user_query, extracted_entities):
        strr = ''
        for key in extracted_entities.keys():
            if len(extracted_entities[key])>0:
                strr = strr + '\n' + key + ': ' + str(extracted_entities[key])
        prompt = prompts.QUERY_SPELLING_REFORMULATION_PROMPT.format(question=user_query, entity_dict = strr)
        completion = client.chat.completions.create(model="gpt-4o",
                                                messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                          {"role": "user","content": prompt}],temperature=0.4)
        return completion.choices[0].message.content
        

def process_sql_query(user_query, selected_pairs, domain_result):
    try:
        print("Classify response type...")
        response_type = classify_response(user_query)
        print('Response Type: ', response_type)
        new_question = handle_question_reformulation(user_query, selected_pairs)
        if domain_result.strip()=='Topic 1':
            cleaned_query, res = generate_and_execute_sql(new_question)
        else:
            cleaned_query, res = generate_and_execute_sql_brand(new_question)
        return response_type, new_question, cleaned_query, res
    except Exception as e:
        print(e)
        return '', '', '', pd.DataFrame()


def classify_response(user_question):
    prompt = prompts.RESPONSE_TYPE_CLASSIFICATION.format(user_question=user_question)
    completion = client.chat.completions.create(model="gpt-4o",
                                                messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                          {"role": "user","content": prompt}],temperature=0.4)
    return eval(completion.choices[0].message.content.replace('```python', '').replace('```', '').strip())['classification']


def reformulate_question(question, tc):
    countt = 1
    strr = ''
    for z in tc.keys():
        strr = strr + str(countt) + '.' + 'Entity - ' + str(z) + ', '+ 'Column - '+ str(tc[z]['column']) + '\n'
        countt = countt+1
    
    prompt = prompts.QUESTION_REFORMULATION_PROMPT.format(question=question,columns_value_information=strr)
    completion = client.chat.completions.create(model="gpt-4o",
                                                messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                          {"role": "user","content": prompt}],temperature=0.4)
    return completion.choices[0].message.content
    

def handle_question_reformulation(original_question, selected_pairs):
    print("Preparing your answer...")
    if len(selected_pairs.keys())>0:
        reformulated_question = reformulate_question(original_question, selected_pairs)
        print("\nI understood your question as:", reformulated_question, '\n')
    else:
        print('No changes needed in query')
        reformulated_question = original_question
    return reformulated_question


# Define function to execute SQL queries
def execute_sql_query(sql_query, db_name):
    try:
        # Execute the query on the registered SQL table
        con = sqlite3.connect(db_name)
        query = con.execute(sql_query)
        cols = [column[0] for column in query.description]
        pd.options.display.precision = 20
        result= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
        #result.show()  # Display the results
        return result
    except Exception as e:
        return f"Error executing query: {str(e)}"

    

def extract_sql_query(response):
    start_marker = "SQL_Query_Start:\n```sql"
    end_marker = "```\nSQL_Query_End."
    start_index = response.find(start_marker)
    end_index = response.find(end_marker)
    if start_index != -1 and end_index != -1:
        sql_query = response[start_index + len(start_marker):end_index].strip()
        return sql_query
    else:
        return "Could not extract SQL query from the response."
    

def classify_sql_query(input_text):
    prompt = f"""Classify the following input as either an SQL query or generic text. Return only "true" if it's an SQL query, or "false" if it's generic text:
    {input_text}
    Do not return anything except true and false"""
    completion = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                                          {"role": "user","content": prompt}],temperature=0.4)
    response = completion.choices[0].message.content
    return response.strip().lower() == "true"
    

def generate_and_execute_sql(question):
    db_name='data/sherlock.db'
    print("Generating SQL query...")
    system_message = prompts.SQL_GENERATOR_PROMPT.format(database_information=prompts.DATABASE_INFORMATION, instruction=prompts.INSTRUCTION,
                                                 kpis=prompts.KPI,joining_info=prompts.JOINING_INFO)
    full_prompt = f"{system_message}\n\nUser question: {question}"
    completion = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                                          {"role": "user","content": full_prompt}],temperature=0.4)
    sql_response = completion.choices[0].message.content
    print('Raw SQL Response: ', sql_response)
    try:
        sql = extract_sql_query(sql_response)
    except Exception as e:
        print(f"We couldn't generate a valid SQL query. Please try rephrasing your question. Error: {e}")
    res = pd.DataFrame()
    if sql:
        print("Executing SQL query...")
        cleaned_query = sql.strip('"')
        print('Cleaned SQL Query: ', cleaned_query)
        sql_checker = classify_sql_query(cleaned_query)
        print(f"Checking if SQL query is valid: {sql_checker}")
        if sql_checker:
            try:
                res = execute_sql_query(cleaned_query, db_name)
                print('SQL Execution Result: ', res)
                return cleaned_query, res
            except Exception as e:
                print(f"An error occurred while executing sql query: {e}")
                return cleaned_query, res
        else:
            return cleaned_query, res
    else:
        return '', res
    

def generate_and_execute_sql_brand(question):
    db_name = 'data/brand_share.db'
    print("Generating SQL query...")
    system_message = prompts_brand_share.SQL_GENERATOR_PROMPT.format(database_information=prompts_brand_share.DATABASE_INFORMATION, instruction=prompts_brand_share.INSTRUCTION,
                                                 kpis=prompts_brand_share.KPI)
    full_prompt = f"{system_message}\n\nUser question: {question}"
    completion = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                                          {"role": "user","content": full_prompt}],temperature=0.4)
    sql_response = completion.choices[0].message.content
    print('Raw SQL Response: ', sql_response)
    try:
        sql = extract_sql_query(sql_response)
    except Exception as e:
        print(f"We couldn't generate a valid SQL query. Please try rephrasing your question. Error: {e}")
    res = pd.DataFrame()
    if sql:
        print("Executing SQL query...")
        cleaned_query = sql.strip('"')
        print('Cleaned SQL Query: ', cleaned_query)
        sql_checker = classify_sql_query(cleaned_query)
        print(f"Checking if SQL query is valid: {sql_checker}")
        if sql_checker:
            try:
                res = execute_sql_query(cleaned_query, db_name)
                print('SQL Execution Result: ', res)
                return cleaned_query, res
            except Exception as e:
                print(f"An error occurred while executing sql query: {e}")
                return cleaned_query, res
        else:
            return cleaned_query, res
    else:
        return '', res
        

def generate_plot(query_results, reformulated_question):
    plot_code = None
    if len(query_results)>0: 
        plot_code = generate_plot_code(query_results, reformulated_question)
    return plot_code


def generate_plot_code(result_df, user_question):
    """Generate plot code based on query results."""
    try:
        buffer = StringIO() 
        result_df.info(buf=buffer) 
        info = buffer.getvalue() 
        #print(info)
        #info=result_df
        plot_prompt = prompts.PLOT_CODE_TEMPLATE.format(data_info=info,dataframe=result_df, user_question=user_question)
        #print(plot_prompt)
        completion = client.chat.completions.create(model="gpt-4o",
                                            messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                        {"role": "user","content": plot_prompt}],temperature=0.4)
        plot_code = completion.choices[0].message.content
        plot_code=plot_code.split("Code_Start:")[-1].split('Code_End.')[0].replace('```python', '').replace('```', '').strip()
        return plot_code
    except Exception as e:
        print(f"Unable to generate plot due to an error {e}.")
        return ''
        

def generate_text(query, df):
    text_prompt = prompts.ANSWER_FORMAT_PROMPT.format(user_question=query,answer_dict=df)
    #print(text_prompt)
    completion = client.chat.completions.create(model="gpt-4o",
                                        messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                    {"role": "user","content": text_prompt}],temperature=0.4)
    text = completion.choices[0].message.content
    return text
    

def get_tab(tab_info, user_query):
    prompt=prompts.MAIN_PROMPT_SS.format(tab_info=tab_info, query=user_query)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
                }
            ],temperature=0.4)
    return completion.choices[0].message.content.replace('```\nCorrect Tab:', '').replace('```', '').strip()


def get_filters(tab_filters, user_query,tab_name, tab_info):
    prompt=prompts.FILTER_PROMPT.format(filters=tab_filters, query=user_query, tab_name=tab_name, tab_info=tab_info)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
                }
            ],temperature=0.4)
    return completion.choices[0].message.content.replace('```\nCorrect Tab:', '').replace('```', '').strip()


def main(query):
    global client
    client = OpenAI()
    reformulated_question, sql_query, plot_code_final, final_tab, filts, text_answer = '', '', '', '', '', ''
    query_result = pd.DataFrame()
    print("User's Query: ", query)
    guardrail_output = eval(guardial_classification_prompt(query)) 
    print(guardrail_output, '\n')
    if (guardrail_output['Business']=='Yes') & (guardrail_output['Safe Content']=='Yes'):
        # Scope Classification
        scope_result = scope_classification_prompt(query)
        print("Scope Classification Result:", scope_result)
        if scope_result.get("Scope") == "Out of Scope":
            print(f"Out of Scope: {scope_result.get('Reason')}")
            text_answer = f"The question you have asked is out of scope for my abilities. Reason: {scope_result.get('Reason')}"
            return reformulated_question, sql_query, query_result, plot_code_final, final_tab, filts, text_answer
        else:
            domain_result = classify_domain(query)
            print(domain_result)
            if domain_result.strip()=='Topic 1':
                print('Processing Entities...')
                ner_result = ner(query)
                print('Extracted Entities: ', ner_result, '\n')
                if all(not value for value in ner_result.values()):   # all entities are empty
                    print("Entity Selection skipped")
                    selected_pairs = {}
                    new_ner_result = ner_result
                else:
                    if len(ner_result['State'])>0: 
                        print('State entity present - Replacing state names with state codes...')
                        new_state_entities = find_state(prompts.STATE_CODE, ner_result['State']) # replacing state names with state codes in the entity dictionary
                        ner_result['State'] = new_state_entities
                    selected_pairs = {}
                    new_ner_result, selected_pairs = find_entities(ner_result, selected_pairs)
                    print('new entity dict:', new_ner_result)
                new_query = spell_check_entities(query, new_ner_result)
                print('Processed Query: ', new_query)
                print('\nSelected pairs for question reformulation using column mapping: ',  selected_pairs, '\n\n')
                type_answer, reformulated_question, sql_query, query_result = process_sql_query(new_query, selected_pairs, domain_result)   
                if reformulated_question!='':   
                    final_tab = get_tab(smart_search.tab_info, reformulated_question)
                else:
                    final_tab = get_tab(smart_search.tab_info, new_query)
                print('Smart Search Result: ', final_tab)
                if (final_tab!='') or (final_tab !='Null'):
                    try:
                        filts = get_filters(smart_search.filters[final_tab], new_query, final_tab, smart_search.tab_info[final_tab])
                    except:
                        filts = ''
                    print('Filters to select: ', filts)
                if len(query_result)>0:
                    for j in query_result.columns:
                        try:
                            query_result[j] = query_result[j].apply(lambda x: x.lower())
                            print('changed to lowercase: ', j)
                        except Exception as e:
                            print('not changed to lower case', j, e)
                            pass  
                    plot_code_final = ''
                    if type_answer == 'Data, Text, and Visualization':
                        plot_code_final = generate_plot(query_result, reformulated_question)      
                text_answer = generate_text(new_query, query_result)
                return reformulated_question, sql_query, query_result, plot_code_final, final_tab, filts, text_answer
            
            elif domain_result.strip()=='Topic 2':
                db_name = 'data/brand_share.db'
                print('Processing Entities...')
                ner_result = ner_brand(query)
                print('Extracted Entities: ', ner_result, '\n')
                if all(not value for value in ner_result.values()):   # all entities are empty
                    print("Entity Selection skipped")
                    selected_pairs = {}
                    new_ner_result = ner_result
                else:
                    selected_pairs = {}
                    new_ner_result, selected_pairs = find_entities_brand(ner_result, selected_pairs)
                    print('new entity dict:', new_ner_result)
                new_query = spell_check_entities(query, new_ner_result)
                print('Processed Query: ', new_query)
                print('\nSelected pairs for question reformulation using column mapping: ',  selected_pairs, '\n\n')
                type_answer, reformulated_question, sql_query, query_result = process_sql_query(new_query, selected_pairs, domain_result)   
                if reformulated_question!='':   
                    final_tab = get_tab(smart_search.tab_info, reformulated_question)
                else:
                    final_tab = get_tab(smart_search.tab_info, new_query)
                print('Smart Search Result: ', final_tab)
                if (final_tab!='') or (final_tab !='Null'):
                    try:
                        filts = get_filters(smart_search.filters[final_tab], new_query, final_tab, smart_search.tab_info[final_tab])
                    except:
                        filts = ''
                if len(query_result)>0:
                    for j in query_result.columns:
                        try:
                            query_result[j] = query_result[j].apply(lambda x: x.lower())
                            print('changed to lowercase: ', j)
                        except Exception as e:
                            print('not changed to lower case', j, e)
                            pass  
                    plot_code_final = ''
                    if type_answer == 'Data, Text, and Visualization':
                        plot_code_final = generate_plot(query_result, reformulated_question)      
                text_answer = generate_text(new_query, query_result)
                return reformulated_question, sql_query, query_result, plot_code_final, final_tab, filts, text_answer
            else:
                text_answer = 'Question is not relevant to the Sherlock Report.'
                return reformulated_question, sql_query, query_result, plot_code_final, final_tab, filts, text_answer

    elif guardrail_output['Database Related']=='Yes':
        text_answer = answer_data(query)
        return reformulated_question, sql_query, query_result, plot_code_final, final_tab, filts, text_answer
    
    elif guardrail_output['Safe Content']=='No':
        text_answer = "This question violates our safety guidelines. Please ask an appropriate question related to the Sherlock Report."
        return reformulated_question, sql_query, query_result, plot_code_final, final_tab, filts, text_answer
    
    elif guardrail_output['About App']=='Yes':
        text_answer = """
**Data Companion Bot Overview**

The Data Companion Bot is designed to provide insightful, data-driven answers for various business questions related to MJN's operations in North America. It focuses on key areas such as:

- Hospital Contracts & Births

- MJN Product Sales across Brands, Retailers, and Stores

- CTS Brand Share

Key Capabilities:

- Generates efficient and accurate SQL queries based on natural language questions.

- Produces visualizations to help interpret and understand the data.

- Provides business-focused answers from rich underlying datasets, helping to inform decision-making.

- The bot is optimized for fast, reliable insights to assist teams in analyzing and understanding important business metrics related to hospital contracts, sales performance, and product distribution.

"""
        return reformulated_question, sql_query, query_result, plot_code_final, final_tab, filts, text_answer
    else:
        text_answer = "This question is not related to the Sherlock Report."
        return reformulated_question, sql_query, query_result, plot_code_final, final_tab, filts, text_answer
    
            