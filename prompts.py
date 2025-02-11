import pandas as pd
import json

def format_database_information(df):
    text = ""
    grouped = df.groupby('Table Name')
    for table, group in grouped:
        text += f"{table}:\n"
        for _, row in group.iterrows():
            text += f"- {row['Column Name']} ({row['Description']})\n"
        text += "\n"
    return text

DF = pd.read_csv('data/sherlock_data_dictionary.csv')
DATABASE_INFORMATION = format_database_information(DF)
with open('data/unique_values.json', 'r') as file:
    UNIQUE_VALUES = json.load(file)
with open('data/state_code.json', 'r') as file:
    STATE_CODE = json.load(file)
with open('data/joining_info.json', 'r') as file:
    JOINING_INFO = json.load(file)



GUARDRAIL_CLASSIFICATION_PROMPT ="""
    You are an AI assistant designed to classify questions for a text-to-SQL application. Your task is to analyze given questions and categorize them based on the following criteria:
    1. Is it a business question that can be answered using a database containing hospital contract, births, sales, inventory, brand share data? The question should not be asking about this app's abilities and capabilities, but a direct business question related to the underlying datasets.
    2. If so, is the question free from biased, toxic, or unethical content?
    3. If not, is the question related to database information? Is the user asking directly about the KPIs available?
    4. If not, is the question related the app and its features?

    ## Instructions:
    1. Read the provided question carefully.
    2. Determine if the question can be answered using a hospital contracts, births, sales, share, and inventory database for infant nutrition products. Does it ask for specific data that would typically be stored in a database?
    3. If the question is business-appropriate, assess whether it contains any biased, toxic, or unethical content.
    4. If the question is not business-appropriate, determine if it's related to database information or usage of this app and its features.
    5. For any questions involving the use of specific columns, syntax corrections, or similar SQL-related queries, classify them under 'Business' and 'Safe Content' categories.
    6. Provide your classification in the following python dictionary format make sure to include in double quotes. Make sure the output is python dictionary. Do not return anything except python dictionary.

    ```
    Business: [Yes / No]
    Safe Content: [Yes / No] 
    Database Related: [Yes / No] 
    About App: [Yes / No] 
    Explanation: [Brief 10 words explanation of your classification]
    ```

    ## Your Task:
    Analyze the given question and provide your classification based on the instructions above. Remember, the focus is on questions that can be directly translated into executable SQL queries.
    Question: {question}
    """


SCOPE_CLASSIFICATION_PROMPT = """
You are an AI assistant designed to classify questions for a text-to-SQL application. Your task is to analyze given questions and categorize them based on the following criteria:

1. Can the question be answered within the application's scope, i.e., questions related to hospital contracts, births, infant nutrition stores around hospitals, sales for infant nutrition products and brands, inventory in stores of retailers brand share, brand share across samples & discharge packs received?
2. Or is it "Out of Scope"? If it is out of scope, categorize whether it is:
   - Predictive: Requires forecasting or predicting future outcomes.
   - Diagnostic: Asks for reasons or causes (e.g., "Why did sales drop?").
   - Analytical: Involves hypothetical scenarios, or impact analysis (e.g., "What happens if we decrease price?" or "Which are the fastest growing stores?").

## Instructions:

1. Read the provided question carefully.
2. Determine if the question is:
   - A business query related to hospital contracts, births, infant nutrition stores around hospitals, sales for infant nutrition products, inventory in stores of retailers, and can be classified as "Descriptive SQL Query" 
   - or "Out of Scope."
3. For business queries, classify them based on the following:
   - Does it ask for specific data stored directly in the database (e.g., SELECT queries)?
   - Does it involve operations like filtering, grouping, aggregating (e.g., `SUM`, `COUNT`, `AVG`), or ranking?
   - Does it involve multi-step operations, such as calculating metrics (e.g., share, percentage), ranking results, or joining multiple tables?
   - If the question is about topics and domains outside the ones mentioned, or requires advanced reasoning, simulations, or predictive modeling, classify it as "Out of Scope."
   - If the question is not a Descriptive SQL Query, identify if it falls under one of the following out-of-scope categories:
     - Predictive: Requires future projections or forecasting.
     - Diagnostic: Involves identifying causes or reasons for trends or events.
     - Analytical: Asks for very complex hypothetical analysis.

## Example Classifications:

1. Question: "What are the top 5 products by sales in 2024?"
   Output:
   {{
       "Scope": "Descriptive SQL Query",
       "Category": "None",
       "Reason": "SQL query for ranking sales data."
   }}

2. Question: "What will sales be next quarter?"
   Output:
   {{
       "Scope": "Out of Scope",
       "Category": "Predictive",
       "Reason": "Predictive question requiring future forecasting."
   }}

3. Question: "Why did sales drop last month?"
   Output:
   {{
       "Scope": "Out of Scope",
       "Category": "Diagnostic",
       "Reason": "Diagnostic question requiring cause analysis."
   }}


4. Question: "What are the monthly rolling hospital contracts won for MJN?"
   Output:
   {{
       "Scope": "Descriptive SQL Query",
       "Category": "None",
       "Reason": "Monthly grouping and counting hospital contracts is SQL-based."
   }}

5. Question: "Which states have the highest share of contracts by births and what is the POS sales in these states?"
   Output:
   {{
       "Scope": "Descriptive SQL Query",
       "Category": "None",
       "Reason": "Multi-step SQL query involving shares and sales retrieval."
   }}

6. Question: "Show all customers who purchased Product X last month."
   Output:
   {{
       "Scope": "Descriptive SQL Query",
       "Category": "None",
       "Reason": "SQL query for retrieving customer purchase data."
   }}

Question: "{question}"

Respond with a JSON object containing:
{{
    "Scope": "Descriptive SQL Query" or "Out of Scope",
    "Category": "Predictive", "Diagnostic", or "Analytical" (if applicable),
    "Reason" or "Response": "Provide the classification reason or user guide answer here."
}}
"""

DOMAIN_PROMPT = """
A user has asked the following question: {question}
Your task is to decide which of the following topics is a given query about:
1. Topic 1 - The question is about hospital contracts won or lost, hospital births, pos sales, brand sales, inventory, weeks of cover, retailers, stores around hospitals. 
2. Topic 2 - The question is about brand share, discharge packs, owned births ratio, or samples given.

Classify each query as either belonging to Topic 1 or Topic 2. 
Return only 'Topic 1' or 'Topic 2' in your response. 
Do not provide any explanation or any extra words.
"""


NER_PROMPT = '''
    Your task is to extract entities from user queries that can be matched against a database for hospital contracts for baby nutrition and retailer sales around hospitals for a text-to-SQL application. Focus on entities that correspond to database fields, tables, or values. Use the following steps and examples to guide your reasoning.
    Steps:
    1. Identify potential entities by looking for specifc names, identifiers, categories, or values that might exist in a database.
    2. Pay special attention to entities such as Hospital Names, Retailers, Brands, State, City, Manufacturers, Contract Holding Companies. 
    3. Consider common database fields in a hospital and baby nutrition sales context, such as hospital names, retailer names, state names, brand names.
    4. Ignore general descriptive terms, or other elements unlikely to have exact matches in a database.
    5. Do not categorize the same entity in two or more groups.
    6. Do not assume anything and do not replace an entity with anything; classify it in the appropriate group.
    7. If anything is enclosed in single or double quotes consider it as one entity.
    8. Account for spelling mistakes that a user can make

    Entity Types:
    - Hospital: The name or mention of any hospital
    - City: The name of a city in the USA
    - State: Any state of the USA, could be the full form, or the state code
    - Retailer: The name of retailer chain which is selling the baby nutrition products
    - Brand: The name of a baby nutrition brand, like Enfamil, Enfagrow, etc.
    - Store ID: The ID of a store
    - Hospital ID: The ID of a hospital
    - Current Contract Holder: The name of a manufacturing company that holds a contract with a hospital
    - Previous Contract Holder: The name of a manufacturing company that previously held a contract with a hospital
    - State WIC Contract Owner: The name of a manufacturing company that holds the WIC contract for a state

    Example 1:
    Query: "What are the total POS sales for Walmart in Ohio?"
    {{
            "Entity": {{
                "Retailer": ["Walmart"],
                "State": ["Ohio"]
            }}
    }}

    Example 2:
    Query: How many hospitals in NY have MJN contract?
    {{
            "Entity": {{
                "State": ["NY"],
                "Current Contract Holder": ["MJN"]
            }}
    }}

    Now, extract the database-matchable entities from the following query:
    {input_text}
    ## Output Format
    Provide your output as a JSON object where the keys are the entity types and the values are Python lists containing the extracted entities. If an entity is not found, return an empty list for that key.
    Process the given text and extract the relevant entities according to the schema and output format described above. Provide only the JSON output, without any additional explanation.
    '''

SEARCH_DICT = {
    'Hospital': ['sap_account_name'],
    'Current Contract Holder': ['current_hfp'],
    'Previous Contract Holder': ['previous_hfp'],
    'Brand': ['global_brand'],
    'Retailer': ['retailer'],
    'Hospital ID': ['sap_account_number'],
    'Store ID': ['store_id'],
    'State WIC Contract Owner': ['state_wic_contract_owner']}


QUERY_SPELLING_REFORMULATION_PROMPT = """
    You are an AI assistant tasked with reformulating a user's question based on the entities we have extracted from it. Your goal is to replace any misspellings with the correct entities that we are providing and replacing the state names with the state codes that we are providing. If no entities are being provided, just to a general spell correction for the user's query.
    User's original question: 
    {question}

    Extracted Entities:
    {entity_dict}

    Instructions:
    1. Identify which parts or words of the user's question that match or closely match the values in the entity dictionary.
    2. Replace these parts or words with the correct values from the entity dictionary.
    3. Reformulate the question using proper grammar and maintaining the original intent.
    5. Do not add any explanations or comments. Only provide the reformulated question.

    Example:

    Original question: What were the sales in New York and San Fransisco for Walmrt last year?
    Extracted Entities:
    State: ['NY', 'SF']
    Retailer: ['Walmart']
    Reformulated question: What were the sales in NY and SF for Walmart last year?

    Please provide only the reformulated question for the above given user question.
    """


QUESTION_REFORMULATION_PROMPT = """
    You are an AI assistant tasked with reformulating a user's question based on provided column value information. Your goal is to correct any misspellings or inaccuracies in the user's question using the given information.

    User's original question: 
    {question}

    Column value information:
    {columns_value_information}

    Instructions:
    1. Identify any entities in the user's question that match or closely match the values in the column value information.
    2. Replace these entities with the correct values from the column value information.
    3. If a match is found, add the corresponding column name in parentheses before the corrected value.
    4. Reformulate the question using proper grammar and maintaining the original intent.
    5. Do not add any explanations or comments. Only provide the reformulated question.

    Example:
    Original question: What were the sales in New York and San Fransisco last year?
    Column value information:
    Column: City
    Value: New York City

    Column: City
    Value: San Francisco

    Reformulated question: What were the sales in (City) New York City and (City) San Francisco last year?

    Please provide the reformulated question for the above given user question.
    """


RESPONSE_TYPE_CLASSIFICATION = '''You are an AI assistant designed to classify user questions for a text-to-SQL application.
Your task is to analyze each question and determine which of the following categories it falls into:

- Data and Text Conversion: Questions that require retrieving data from the database, followed by generating a natural language explanation, interpretation, or summary. This involves converting structured data into easily understandable textual content, such as answering "how" or "why" based on the data retrieved.

- Data, Text, and Visualization: Questions that not only require data retrieval and textual explanation but also need a visual representation (such as a chart, graph, or plot) to better illustrate the results. These questions demand presenting data insights using both text and visuals for a comprehensive understanding.

Return your response in the following Python dictionary format:
{{
   "classification": "One of: 'Data and Text Conversion', 'Data, Text, and Visualization'",
   "explaination": "Your explaination in one line"
}}
Do not include any other text or explanations in your response besides this dictionary.
Please classify the following user question: {user_question}
'''


KPI = """
1. Hospitals Won: The distinct hospitals with contract_status='Won' and the current_hfp='MJN Exclusive'
2. Hospitals Lost: The distinct hospitals with contract_status='Lost' and the previous_hfp='MJN Exclusive'
3. Net Hospitals Won: The difference between the number of distinct hospitals won and the number of distinct hospitals lost by MJN.
4. Rolling: The cumulative sum of hospital contracts or hospital births calculated over a rolling time period (e.g., month, quarter, year).
5. For rolling always extract out the relevant time period (e.g., month, quarter, year) and provide that time period in the seperate column.
6. Births Won: The sum of the total births in the distinct hospitals won by MJN.
7. Births Lost: The sum of the total births in the distinct hospitals lost by MJN.
8. Net Births: The difference between the total births in the distinct hospitals won by MJN and the total births in the distinct hospitals lost by MJN.
9. Reckitt's Share of Births: (Total number of births in distinct hospitals where current_hfp='MJN Exclusive')/(Total number of births in all distinct hospitals) * 100
10. Cities are tagged as 'Opportunity' when Reckitt's share of births in that city falls between "40%" and "66%". 
    Formula for Opportunity Cities = Cities where (40%≤Reckitt’s Share of Births≤66%).
11. Top/Bottom: Always use group by for the entity written after top/bottom key word.
"""


INSTRUCTION = '''
    1. If the question is only about hospitals, contract status, or stores around hospitals, and does not ask about sales or inventory data, only use the hospital_report table and do not perform any joins.
    2. If the question is about sales and inventory for stores and retailers without mentioning hospitals, use only the sales_inventory table, and do not perform any joins. 
    3. If the question is about sales and inventory in stores or retailers around a hospital, then you need to join the hospital_report table with the sales_inventory table.
    4. If a sales or inventory question is asked at a month or year level, convert it to the format YYYYMM for the 'year_month' column in the SQL Query. The YYYYMM should be a number and not a string. For example, October 2024 should be 202410. 
    5. For sales data at the weekly level, the week start and end dates are stored in the date format 'YYYY-mm-dd'.
    6. For contract start and expiry dates in the hospital_report table, use the date format 'YYYY-mm-dd' in the SQL Query.
    7. Provide the appropriate granularity of the sales data according to the question.
    8. If the question is about hospitals, births, or contracts, always use DISTINCT COUNT for sap_account_number and sap_account_name.
    9. Always remember the hospital_report table is at a hospital x store level. Hence information needed at a hospital level needs a DISTINCT query. Since the information is present at a hospital x store level, do not aggregate numbers at a row level when the question is about hospitals.
    10. If the question is related to sales in stores or retailers present in a state / city, use the 'state' or 'city' columns present in the sales_inventory table.
    11. Always implement case-insensitive matching by converting both the column and search value to lower case in the 'where' clause.
    13. If a question is asked about the number of births in a hospital, do not sum across all the rows for the hospital, take the UNIQUE value for the rows with latest flag.
    14. Do not return explanation, steps etc.
    15. Remove null values where requried.
    16. If is related to ordering,ranking,top,best,most always remove the null values from the column before doing the ranking or ordering.
    17. Do not do the over analysis, only do the answer based on the question.
    18. Only reference columns that exist in the provided database. Carefully analyze the column descriptions to ensure accuracy. If the question cannot be answered with the available database columns, provide a clear, user-friendly message explaining that the required information is unavailable and suggest some columns on which they can ask the questions.
    19. If anything is ambigious then leave the placeholder for that, do not assume anything.
'''


FILTER_INFORMATION = '''
    When filtering data based on location name, dealer name, country name, or product name in where clause:
    - Always use the LIKE operator for these text-based filters and in select statement always include the distinct filter value.
    - Always implement matching-lower case both on columns and value to improve user experience.
    - Always Display results for each unique match, ensuring no duplicates in select.
    - Order the results alphabetically for easier navigation.
    - For example:
        SELECT DISTINCT column_name
        FROM table_name
        WHERE LOWER(column_name) LIKE LOWER('%search_term%')
        ORDER BY column_name
    Always return the value of all distinct match in select statement
    '''


SQL_GENERATOR_PROMPT = '''Transform the following natural language requests into valid SQLite queries for SQLite database. Assume a database with the following table and columns exists:
{database_information}
Follow these instructions when generating SQL queries:
{instruction} 
Available KPIs:
{kpis}
Use below joining information to join hospital_report table with sales_inventory table:
{joining_info}
Provide your answer in the following format only:
SQL_Query_Start:
    "SQLite_Query"
SQL_Query_End.
'''


PLOT_CODE_TEMPLATE = '''
    You are an AI assistant tasked with generating plotly code to visualize data based on a question and data information.
    Human: Here's the dataframe structure and column datatypes:
    {data_info}

    Here is the actual dataframe showing the values:
    {dataframe}
    
    This is the question:
    {user_question}
    
    Do not create any dataframes of your own. Assume the dataframe is named 'dataframe' and using the structure provided above write code for this dataframe only.
    Please generate plotly code to visualize this data for the question. 
    Use pandas for data manipulation and plotly for visualization.
    Make sure to name the plot as 'fig' in the code.
    Assume that all the information in the dataframe is in lowercase.
    Do not include anything except the python code like explaination etc.
    Always use margin in plot of 50 like margin = dict(t=50,r=50).
    Only generate single most relevant plot for the question.
    Show pie-chart when need is to represent parts of a whole as percentages or proportion.
    Show line chart when there is trend analysis.
    In case of encountering date type columns, make the date column user readable. eg- 'Dec 2024' for '122024', '2024' for '2024', '11 November 2024' for '11112024'.
    Use data from the dataframe itself. Don't hallucinate values or use dummy data. Don't assume anything.
    Do not save the plot, and do not give code that can result in error like 'An error occurred: 'str' object has no attribute 'savefig'.
    Give appropriate axis title according to the data provided.
    The axis tick labels should also be suitable.
    Do not include fig.show() in the code.
    The theme should be dark blue. The background should be white. For plots with multiple trends, the shades of blue should be clearly distinguishable.
    
    Provide your answer in the following format only and do not add multiline quotes:
    Code_Start:
        "Plot_Code"
    Code_End.
    '''


MAIN_PROMPT_SS = """Following is a list of five tabs present inside the Sherlock Dashboard and a description of the information stored in them:

{tab_info}

Suppose a user has asked: "{query}". We need to select the best tab where the user can find an answer to their question.

For this purpose, provide the correct section within the tab well, based on the description provided. If no tab can answer the user's question, return 'Null'.

Provide your response in the following format: 
```
Tab Name
```

For example, if the user's query is "How many net contracts has MJN won in Texas?", the answer should be:
```
Correct Tab:
Hospital Contracts Overview
```
"""


FILTER_PROMPT = """A user has asked the following query: "{query}" 
To get an answer to his query, he needs to set the filters in a dashboard to get the desired information. 
Given below is a list of filters present in the dashboard and the type of options present for each filter:

{filters}

Using the information present in the user's query, provide the filters that are mentioned in the query and need to be set. 
Only provide a filter and its value if it is directly mentioned in the user's query. The suggested value of the filter should only be from its provided list of possible values present above.
Generate your response in the following format:
* Filter Name - Correct Filter Value
* Filter Name - Correct Filter Value
and so on.
Do not give any explanations for your answer."""


# Answer Format Prompt
ANSWER_FORMAT_PROMPT = '''Summarize the answer to the question for a business execute audience: "{user_question}" using the provided dataframe:\n"{answer_dict}".

- Use bullet points for clarity wherever needed.
- Come up with a natural language response, and do not just simply mirror the numbers in the dataframe. Try to provide insights wherever possible.
- Highlight key numbers using bold formatting (e.g., **1000**)
- Focus on directly answering the question without extra recommendations or reasoning.
- Keep the summary concise and to the point.
- Do not add any extra information like explaination,steps,like etc.
- Do not hallucinate any numbers on your own.
Formatting guidelines:
- Start directly with the answer, without mentioning the audience or using phrases like "Here is a summary..."
- Use a single blank line between bullet points
- Replace any '$' with "\$" in the final text
- Present the information as a natural, conversational response without referencing the data source
Aim for a clear, concise summary that directly addresses the question based on the provided dataframe'''


KPI_PROMPT = """A user has asked the following question about our data: {question}. 

Provide a succint answer based on the below information about the Sherlock Report. Format the answer in a clean and bulleted manner, so that it can be cleanly displayed on a streamlit app.

The Sherlock Dashboard is a PowerBI Report built on top of numerous gold tables. It contains hospital contract information and sales & inventory information for MJN's baby nutrition products in North America. Below is the information about the gold tables:
1. hospital_report: This table focuses mainly on MJN's hospital contract wins and losses. It contains information about hospitals like current & previous contract holders, contract change date, number of births, feeding practices, stores and retailers around the hospital along with their distances in miles. 
2. pos_inventory_sales: This table contains sales & inventory data at a store x brand level at a weekly granularity. The retailer and complete address for each store is also present. The POS sales data is present, along with sales units, inventory, and weeks of cover.
3. cts_brand_share: This comprises of 10 tables that have information around CTS brand share, discharge packs, and owned births ratios.

Following are the main KPIs covered in the report:

- Hospitals Won / Lost: Provides details around the hospitals in which MJN either won or lost the contract. 

- Births Won / Lost: The birth statistics for the hospitals covered under MJN's catalogue.

- Reckitt's Share in Hospitals / Births: The share of hospital contracts and births that is under MJN, compared to competitors. 

- POS Sales / Units: The sales and units sold in every story at a weekly level. The data is available at a brand level.

- Inventory on Hand & Weeks of Cover: The inventory and woc for every store for the latest week.

- CTS Brand Share: The consumer tracking survey data used to calculate MJN's brand share.

"""

