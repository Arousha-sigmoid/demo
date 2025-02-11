filters = {}
filters['Hospital Contracts Overview'] = {
    'Hospital Status':['Select All', 'Lost', 'Won'],
    'NICU Presence':['Select All', 'Yes', 'No'],
    'Hospital State': 'All and a list of all state codes present in the USA',
    'Hospital City': 'All and a list of all cities present in the USA',
    'Information Type':['Hospital Contracts', 'Hospital Births']
    }
filters['Retail Geo Connector'] = {
    'Hospital Status':['Select All', 'Lost', 'Won'],
    'Hospital Contract Owner':['All', 'Abbott Exclusive', 'Choice', 'Gerber Exclusive', 'MJN Exclusive', 'SPOT Non-Contracted', 'Unknown'],
    'NICU Presence':['Select All', 'Yes', 'No'],
    'Hospital State': 'All and a list of all state codes present in the USA',
    'Hospital City': 'All and a list of all cities present in the USA',
    'Map Gradient': ['POS Sales', 'POS Units', 'WoC', 'Inventory'],
    'Select Hospital': 'All or The names of a hospital for which the user wants to see the nearby stores',
    'Select Retailer':'The retailer names for which the user wants to see the stores',
    'With in Distance': 'The distance from the hospital within which the user wants to see the stores, it can be between 0 to 30 miles'
    }
filters['Hospital Summary Tracker'] = {
    'Hospital Status':['Select All', 'Lost', 'Won'],
    'Hospital Contract Owner':['All', 'Abbott Exclusive', 'Choice', 'Gerber Exclusive', 'MJN Exclusive', 'SPOT Non-Contracted', 'Unknown'],
    'NICU Presence':['Select All', 'Yes', 'No'],
    'Hospital State': 'All and a list of all state codes present in the USA',
    'Hospital City': 'All and a list of all cities present in the USA',
    'Retailer': 'The retailers for which the user wants to see the store',
    'With in Distance': 'The distance from the hospital within which the user wants to see the stores, it can be between 0 to 30 miles'
    }
filters['Sellout Tracker'] = {
    'Hospital State': 'All and a list of all state codes present in the USA',
    'Hospital City': 'All and a list of all cities present in the USA',
    'Hospital Status':['Select All', 'Lost', 'Won'],
    'Retailer': 'The retailers for which the user wants to see the store',
    'Global Brand': ['All', 'Enfamil', 'Enfamil WIC', 'Nutramigen', 'Nutramigen / Allergy', 'Enfagrow', 'Specialty', 'Super High Premium', 'Vitamins', 'Pregestimil', 'Puramino'],
    'WIC / WENR': ['All', 'WIC', 'WENR'],
    'Hospital Contract Owner':['All', 'Abbott Exclusive', 'Choice', 'Gerber Exclusive', 'MJN Exclusive', 'SPOT Non-Contracted', 'Unknown'],
    'NICU Presence':['Select All', 'Yes', 'No'],
    'Data Granularity': ['Week', 'Month'],
    'Select Hospital': 'All or The names of a hospitals for which the user wants to see the sales of the nearby stores'
    }
filters['CTS Brand Share Report'] = {
    'NICU Presence':['Select All', 'Yes', 'No'],
    'Hospital State': 'All and a list of all state codes present in the USA',
    'Hospital City': 'All and a list of all cities present in the USA',
    'Hospital Territory Number': 'Select All or particular territories numbers for which the user wants to see brand share numbers',
    'Hospital': 'The names of particular hospitals if any for which the user wants to see the brand share information',
    'WIC Status': ['WIC', 'Non-WIC'],
    'Brand Share Cohort': ['In Hospital', '1 month', ' 2 months', '3 months'],
    'Month Rolling': 'If the user mentions any month rolling number'
}


# defining the tabs

tab_info = {}
tab_info['Hospital Contracts Overview'] = """This tab has provides visibility at state and city level information on hospitals' contract win and loss tracking. The information can either be displayed in terms of hospitals contracts won / lost, or in terms of hospital births won / lost. This tab has following two main charts, with the ability to switch between the main KPIs which are hospital contracts and hospital births:
- A map of the USA showing at a state level the information about the hospitals contracts / births, such as won / lost / net for MJN till date. 
- A chart showing at a monthly level the number of hospital contracts / births won and lost by MJN since Jan 2022 using stacked bar chart, and in the same plot showing the net rolling monthly trend of hospital contracts / births for MJN using a line chart. 
There is also top panel that displays information about the number of hospital births and contracts won by MJN in the latest month, and also till date, and also Reckitt's share in total hospital births."""

tab_info['Retail Geo Connector'] = """This tab identifies nearest stores available to the hospitals that are part of MJN's tracking. We can see all the hospitals that are part of MJN's tracking, and also locate the nearest stores to each hospital. This tab has the following two main views:
- A map showing the locations of all the hospitals, where the marker for each hospital is color coded according to the current contract holders of the hospital. There is also a list of all the hospitals next to the map, and we can select as many hospitals as we want 
- A map showing the locations of all the stores that are present within 'x' miles of the selected hospitals. The distance radius is selected by the user, and can be between 0 to 30 miles. The marker for the stores location is color coded according to either sales, inventory, units sold, or weeks of cover, dependent on what the user selects. Next to the chart a table is present which lists all the displayed stores' address, retailer, city, state, distance from hospital, latest week sales / units sold / weeks of cover.
"""

tab_info['Hospital Summary Tracker'] = """This tab provides insights on hospitals, total births, cities, MJN and competitor share, and retail information all in one tab. There are two sub-tabs present within this tab:
- Hospital: The first element is a table which lists the details at a hospital level, like Hospital address, city, state, contract status with MJN, hospital type, total births, preterm births, percentage of different feeding methods practiced there (breast fed, formula fed, supplemented, etc.). The second element is another table which lists the total number of stores around a hospital, and also the stores' distribution across different channels and retailers. The user can select the distance radius within which the stores need to be located at to be linked to a hospital. """

tab_info['Sellout Tracker'] = """This tab shows trend overview and insights for POS Sales and inventory for stores. This tab has the following three views:
- Monthly or Weekly Trend Charts for POS Sales, POS Units, Inventory on Hand, and Weeks of Cover (WOC). The information can be filtered across cities, states, brands, retailers, hospitals, etc. 
- A table which shows the stores that are present around the hospitals that are in scope according to the selected filters. For these stores, information like Retailer Name, POS Sales, Units Sold, Inventory on hand, and Weeks of Cover is displayed for the latest month or week, and all at a brand level. 
- A horizontal bar chart showing the POS Sales by Brands for the latest month / week."""

tab_info['CTS Brand Share Report'] = """This tab provides insights through Brand Share Trend View along hospital contracts / births. There are two main sections in this tab:
- A monthly chart showing brand share for Abbott and MJN, contracts and births won / lost, and the sample size for each month (number of people who filled the CTS). 
- A monthly chart showing brand share for Abbott and MJN across groups of people who received discharge packs from the two manufacturers. 
"""
