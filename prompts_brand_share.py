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

BRAND_SHARE_DF = pd.read_csv('data/brand_share_data_dictionary.csv')
DATABASE_INFORMATION = format_database_information(BRAND_SHARE_DF)
with open('data/brand_share_unique_values.json', 'r') as file:
    BRAND_SHARE_UNIQUE_VALUES = json.load(file)


NER_PROMPT = '''
    Your task is to extract entities from user queries that can be matched against a database for brand share and sample discharge packs for manufacturers of baby nutrition products. Focus on entities that correspond to database fields, tables, or values. Use the following steps and examples to guide your reasoning.
    Steps:
    1. Identify potential entities by looking for specifc names, identifiers, categories, or values that might exist in a database.
    2. Do not categorize the same entity in two or more groups.
    3. If anything is enclosed in single or double quotes consider it as one entity.
    4. Account for spelling mistakes that a user can make

    Entity Types:
    - Brand Manufacturer: The name of the brand manufacturer such as "ABBOTT", "MJN", etc. If the user is mentioning 'Reckitt' as manufacturer, replace it with MJN, and then extract it as the appropriate entity.
    - Feeding Period: A time entity which represents a baby's feeding period, e.g., 'in hospital', "INH", "1MO", '1 month', "2MO", '2 month', etc.
    - WIC Flag: A flag which shows the WIC status of the individual that participated in the program, e.g., "WIC" or "Non-WIC".
    - Hospital Feeding Practice: The feeding practice administered by a hospital, e.g., "MJN Exclusive"  or "Gerber Exclusive" or "Abbott Exclusive", etc.
    - Contract Status: The status of a hospital contract with respect to MJN, e.g., "Won" or "Lost".
    - Sample Manufacturer: The manufacturer provided the sample, e.g., 'Gerber', "GER", "MJN", 'Abbott',  "ABB", etc. If the user is mentioning 'Reckitt' as manufacturer, replace it with MJN, and then extract it as the appropriate entity.
    - Baby Birth: A time entity representing the date, month, or year of when a baby was born, and for which the brand share information is required. This should be converted to the format 'YYYYMM' and then extracted as an entity.

    Example 1:
    Query: "What was Reckitt's brand share for wic for November 2022?"
    {{
            "Entity": {{
                "Brand Manufacturer Name": ["MJN"],
                "WIC Flag": ["WIC"],
                "Baby Birth": ["202211"]
            }}
    }}

    Example 2:
    Query: "What is the number of discharge packs recieved from Abbott in December 2022 for babies in hospital?"
    {{
            "Entity": {{
                "Sample Manufacturer": ["Abbott"],
                "Feeding Period": ["in hospital"],
                "Baby Birth": ["202212"]
            }}
    }}

    Example 3:
    Query: "What is MJN brand share for people who got the Abbott sample in May 2024 for a 3 month period?"
    {{
            "Entity": {{
                "Brand Manufacturer": ["MJN"],
                "Sample Manufacturer": ["Abbott"],
                "Feeding Period": ["3 month"],
                "Baby Birth": ["202405"]
            }}
    }}


    Now, extract the database-matchable entities from the following query:
    {input_text}
    ## Output Format
    Provide your output as a JSON object where the keys are the entity types and the values are Python lists containing the extracted entities. If an entity is not found, return an empty list for that key.
    Process the given text and extract the relevant entities according to the schema and output format described above. Provide only the JSON output, without any additional explanation.
    '''

SEARCH_DICT = {
    'Brand Manufacturer': ['brand_mfg_nm'],
    'Feeding Period': ['FDG_period_cd'],
    'WIC Flag': ['Ever_wic_fl'],
    'Hospital Feeding Practice': ['hospital_feeding_practice_hfp'],
    'Contract Status': ['contract_status'],
    'Sample Manufacturer': ['srd_MFG_CD'],
    'Baby Birth': ['Baby_birth_yrmo']
    }


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

    Original question: What is the brand share for mjn for 2 month infants in mjn exclusive hospitals for Nov 22?
    Extracted Entities:
    Brand Manufacturer: ["MJN"]
    Feeding Period: ["2MO"]
    Hospital Feeding Practice: "MJN Exclusive"
    Baby Birth: ["202211"]

    Reformulated question: What were the sales in NY and SF for Walmart last year?

    Please provide only the reformulated question for the above given user question.
    """


KPI = """
1. Abbott Brand Share:
   - First Filter rows based on the 'Baby_birth_yrmo' and 'FDG_period_cd'.
   - Formula: COALESCE(SUM(BRAND_WT_ADJ × CUMUL_MB_WT_ADJ for Abbott)/SUM(BRAND_WT_ADJ × CUMUL_MB_WT_ADJ for all brands),0)*100 || '%'

2. Reckitt Brand Share:
   - First Filter rows based on the baby birth year and feeding period.
   - Formula: COALESCE(SUM(BRAND_WT_ADJ × CUMUL_MB_WT_ADJ for MJN)/SUM(BRAND_WT_ADJ × CUMUL_MB_WT_ADJ for all brands),0)*100 || '%'

3. Owned Birth Ratio (MJN/Abbott):
   - If Ever_wic_fl == 'WIC' -> Formula: SUM(net_total_births) - SUM(net_nw_births)
   - If Ever_wic_fl == 'Non-WIC' -> Formula: SUM(net_nw_births)
   - If Ever_wic_fl is not present -> Formula: SUM(net_total_births)
   - MJN Births: The correct formula for Ever_wic_fl and hospital_feeding_practice_hfp='MJN Exclusive'
   - Abbott Births: The correct formula for Ever_wic_fl and hospital_feeding_practice_hfp='Abbott Exclusive'
    Final Formula for Owned Birth ratio (MJN/Abbott) = COALESCE(MJN Births/NULLIF(Abbott Births,0),0)

4. Births Won or Births lost:
   - If Ever_wic_fl == 'WIC' -> Formula: SUM(net_total_births) - SUM(net_nw_births)
   - If Ever_wic_fl == 'Non-WIC' -> Formula: SUM(net_nw_births)
   - If Ever_wic_fl is not present -> Formula: SUM(net_total_births)

5. Discharge packs Recieved from Abbott/MJN = SUM(Brand_wt_adj)

6. MJN Brand Share for Abbott Sample:
   - First Filter rows based on the 'Baby_birth_yrmo' and 'FDG_period_cd'.
   - Formula: COALESCE(SUM(BRAND_WT_ADJ×CUMUL_MB_WT_ADJ for MJN under ABBOTT) / SUM(BRAND_WT_ADJ×CUMUL_MB_WT_ADJ for all brands under ABBOTT),0)*100 || '%'

7. MJN Brand Share for MJN Sample:
   - Filter rows based on the 'Baby_birth_yrmo' and 'FDG_period_cd'.
   - Formula: COALESCE(SUM(BRAND_WT_ADJ×CUMUL_MB_WT_ADJ for MJN under MJN) / SUM(BRAND_WT_ADJ×CUMUL_MB_WT_ADJ for all brands under MJN),0)*100 || '%'

8. Abbott Brand Share for MJN Sample:
   - Filter rows based on the 'Baby_birth_yrmo' and 'FDG_period_cd'.
   - Formula: COALESCE(SUM(BRAND_WT_ADJ×CUMUL_MB_WT_ADJ for Abbott under MJN) / SUM(BRAND_WT_ADJ×CUMUL_MB_WT_ADJ for all brands under MJN),0)*100 || '%'

9. Abbott Brand Share for Abbott Sample:
   - Filter rows based on the 'Baby_birth_yrmo' and 'FDG_period_cd'.
   - Formula: COALESCE(SUM(BRAND_WT_ADJ×CUMUL_MB_WT_ADJ for Abbott under Abbott) / SUM(BRAND_WT_ADJ×CUMUL_MB_WT_ADJ for all brands under Abbott),0)*100 || '%'
"""


INSTRUCTION = '''
1. If the question is about Reckitt's share and Abbot's share only use the 'brand_product_alignment_vw' table and do not perform any joins.
2. If the question is about discharge packs or samples, only use the 'sample_brand_share_vw' table and do not perform any joins.
3. If using the 'brand_product_alignment_vw' table or the 'sample_brand_share_vw' table, convert the 'Baby_birth_yrmo' column into the YYYYMM format in the SQL Query. The YYYYMM should be a number and not a string. For example, October 2024 should be 202410.
4. If using the 'win_lost_dim' table, then the 'contract_start_date' column should be in the date format 'YYYY-mm-dd' in the SQL Query.
5. If the question is related to discharge packs / samples received, and a value is provided for FD_period_cd, the following cases arise:
   - If FDG_period_cd = "INH", then the value of 'Baby_birth_yrmo' should remain the same. 
   - If FDG_period_cd = "1MO", then the value of 'Baby_birth_yrmo' should be subtracted by 1 month, and that value should be used in the sql query. 
   - If FDG_period_cd = "2MO", then the value of 'Baby_birth_yrmo' should be subtracted by 2 months, and that value should be used in the sql query. 
   - If FDG_period_cd = "3MO", then the value of 'Baby_birth_yrmo' should be subtracted by 3 months, and that value should be used in the sql query.
6. If the question is contains more than one feeding period code, i.e., INH, 1MO, 2MO, or 3MO, then always filters the rows based on the 'OR' condition in the SQL generated query.
7. For the questions related to discharge pack recieved from abbott or mjn, always use the column 'srd_MFG_CD'.
8. Always implement case-insensitive matching by converting both the column and search value to lower case in the 'where' clause.
9. Do not return explanation, steps etc.
10. Do not do the over analysis, only do the answer based on the question.
11. Only reference columns that exist in the provided database. Carefully analyze the column descriptions to ensure accuracy. If the question cannot be answered with the available database columns, provide a clear, user-friendly message explaining that the required information is unavailable.
'''


SQL_GENERATOR_PROMPT = '''Transform the following natural language requests into valid SQLite queries for SQLite database. Assume a database with the following table and columns exists:
{database_information}
Follow these instructions when generating SQL queries:
{instruction} 
Available KPIs:
{kpis}
Provide your answer in the following format only:
SQL_Query_Start:
    "SQLite_Query"
SQL_Query_End.
'''


