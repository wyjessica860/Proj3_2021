## name: Yue Wang ##
## uniqname: wyjessic ##
import sqlite3
import sys
import plotly.graph_objs as go
# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'
def connect_helper(query,param=None):
    con = sqlite3.connect(DBNAME)
    cur = con.cursor()
    query = query.replace('\n','')
    result = []
    if param == None:
        result = cur.execute(query).fetchall()
    else:
        result = cur.execute(query,param).fetchall()
    con.close()    
    return result

# Part 1: Implement logic to process user commands
def Bar(com_list):
    bar_param = 'SpecificBeanBarName, Company, Sell.EnglishName, Rating, CocoaPercent,Source.EnglishName'
    param,LIMIT = [],10
    DESC = ' DESC '
    where_flag, first_flag, plot_flag = False,False, False
    Countries_table = 'Sell'
    query_base = '''
                    Select SpecificBeanBarName, Company, 
                    Sell.EnglishName, Rating, CocoaPercent,Source.EnglishName 
                    From [Bars] as B 
                    JOIN [Countries] as Sell ON B.CompanyLocationId = Sell.ID
                    JOIN [Countries] as Source ON B.BroadBeanOriginId = Source.ID 
                    
                '''
    query_order = ' ORDER BY Rating'
    query_limit = ' LIMIT '
    for x in com_list:
        if 'barplot' == x:
            plot_flag = True
        if 'source' == x:
            Countries_table = 'Source'
        if 'country=' in x or 'region=' in x : where_flag = True
        if 'cocoa' == x:
            query_order = ' ORDER BY CocoaPercent'
        if 'bottom' == x:
            DESC = ''
        if x.isnumeric() :
            LIMIT = int(x)

    if where_flag:
        for x in com_list:
            if 'country=' in x:
                val = x.split('=')[1]
                param.append(val)
                if first_flag: 
                    if len(val) == 2:
                        query = query +' and '+Countries_table+'.Alpha2 == ? '
                    elif len(val) == 3:
                        query = query +' and '+Countries_table+'.Alpha3 == ? '
                    else:
                        query = query +' and '+Countries_table+'.EnglishName == ? '
                else:
                    first_flag = True
                    if len(val) == 2:
                        query = query_base +' WHERE '+Countries_table+'.Alpha2 == ? '
                    elif len(val) == 3:
                        query = query_base +' WHERE '+Countries_table+'.Alpha3 == ? '
                    else:
                        query = query_base +' WHERE '+Countries_table+'.EnglishName == ? '
            if 'region=' in x:
                val = x.split('=')[1]
                param.append(val)
                if first_flag:
                    query = query + ' and '+Countries_table+'.Region == ? '
                else:
                    query = query_base +' WHERE '+Countries_table+'.Region == ? '
    
        return plot_flag, bar_param, connect_helper(query = query+ query_order + DESC + query_limit + str(LIMIT),param = param)
    else:
        return plot_flag, bar_param, connect_helper(query = query_base + query_order + DESC + query_limit + str(LIMIT))
def Company(com_list):
    company_param= ''
    param,DESC,LIMIT = [],' DESC ', 10
    where_flag, first_flag, plot_flag = False,False, False

    thirdselect = ' AVG(B.Rating) '
    query_limit = ' LIMIT '
    for x in com_list:

        if 'country=' in x or 'region=' in x : where_flag = True
        if 'cocoa' == x:
            thirdselect = ' AVG(B.CocoaPercent) '
        if 'number_of_bars' == x:
            thirdselect = ' COUNT(B.ID) '
        if 'bottom' == x:
            DESC = ''
        if x.isnumeric() :
            LIMIT = int(x)
        
    query_base = f'''
                    Select B.Company, Sell.EnglishName, {thirdselect}
                    FROM Bars as B
                    JOIN [Countries] as Sell ON B.CompanyLocationId = Sell.ID
                    GROUP BY Company
                    HAVING COUNT(B.ID) > 4
                '''
    query_order = f' ORDER BY {thirdselect}'
    company_param = f'Select B.Company, Sell.EnglishName, {thirdselect}'
    if where_flag:
        for x in com_list:
            if 'barplot' == x:
                plot_flag = True
            if 'country=' in x:
                val = x.split('=')[1]
                param.append(val)
            
                if len(val) == 2:
                    query = query_base +' and Sell.Alpha2 = ? '
                elif len(val) == 3:
                    query = query_base +' and Sell.Alpha3 = ? '
                else:
                    query = query_base +' and Sell.EnglishName = ? '
            if 'region=' in x:
                val = x.split('=')[1]
                param.append(val)
                
                query = query_base +' and Sell.Region = ? '
    
        return plot_flag, company_param,connect_helper(query = query+ query_order + DESC + query_limit + str(LIMIT),param = param)
    else:
        return plot_flag, company_param,connect_helper(query = query_base + query_order + DESC + query_limit + str(LIMIT))
def Country(com_list):
    country_param = ''
    plot_flag = False
    param,DESC,LIMIT = [],' DESC ', 10
    where_flag, first_flag, source_flag= False,False,False
    Countries_table = 'Sell'
    thirdselect = ' AVG(B.Rating) '
    query_limit = ' LIMIT '
    for x in com_list:
        if 'barplot' == x:
            plot_flag = True
        if 'source' == x:
            source_flag = True
            Countries_table = 'Source'
        if 'region=' in x : where_flag = True
        if 'cocoa' == x:
            thirdselect = ' AVG(B.CocoaPercent) '
        if 'number_of_bars' == x:
            thirdselect = ' COUNT(B.ID) '
        if 'bottom' == x:
            DESC = ''
        if x.isnumeric() :
            LIMIT = int(x)
    if source_flag: 
        firstselect = 'Source.EnglishName , Source.Region '
        groupbyname = 'Source.EnglishName'
    else: 
        firstselect = 'Sell.EnglishName , Sell.Region'
        groupbyname = 'Sell.EnglishName'
    query_base = f'''
                    Select {firstselect}, {thirdselect}
                    From [Bars] as B 
                    JOIN [Countries] as Sell ON B.CompanyLocationId = Sell.ID
                    JOIN [Countries] as Source ON B.BroadBeanOriginId = Source.ID
                    GROUP BY {groupbyname}
                    HAVING COUNT(B.ID) > 4
                '''
    country_param = f'{firstselect}, {thirdselect}'
    query_order = f' ORDER BY {thirdselect}'
    if where_flag:
        for x in com_list:
            if 'region=' in x:
                val = x.split('=')[1]
                param.append(val)
                
                query = query_base +' and '+Countries_table+'.Region = ? '
    
        return plot_flag, country_param,connect_helper(query = query+ query_order + DESC + query_limit + str(LIMIT),param = param)
    else:
        return plot_flag, country_param,connect_helper(query = query_base + query_order + DESC + query_limit + str(LIMIT))

def Region(com_list):
    region_param = ''
    param,DESC,LIMIT = [],' DESC ', 10
    plot_flag = False
    where_flag, first_flag, source_flag= False,False,False
    thirdselect = ' AVG(B.Rating) '
    Countries_table = 'Sell'
    query_limit = ' LIMIT '
    for x in com_list:
        if 'barplot' == x:
            plot_flag = True
        if 'source' == x:
            source_flag = True
            Countries_table = 'Source'
        if 'cocoa' == x:
            thirdselect = ' AVG(B.CocoaPercent) '
        if 'number_of_bars' == x:
            thirdselect = ' COUNT(B.ID) '
        if 'bottom' == x:
            DESC = ''
        if x.isnumeric() :
            LIMIT = int(x)
    if source_flag: 
        firstselect = 'Source.Region '
        groupbyname = 'Source.Region'
    else: 
        firstselect = ' Sell.Region'
        groupbyname = 'Sell.Region'
    query_base = f'''
                    Select {firstselect}, {thirdselect}
                    From [Bars] as B 
                    JOIN [Countries] as Sell ON B.CompanyLocationId = Sell.ID
                    JOIN [Countries] as Source ON B.BroadBeanOriginId = Source.ID
                    GROUP BY {groupbyname}
                    HAVING COUNT(B.ID) > 4
                '''
    region_param = f'Select {firstselect}, {thirdselect}'
    query_order = f' ORDER BY {thirdselect}'
    return plot_flag, region_param, connect_helper(query = query_base + query_order + DESC + query_limit + str(LIMIT))

def _plot(param,result,command):
    xaxis = [ row[0] for row in result]
    param = param.split(',')
    keywords = 'Rating'
    if 'cocoa' in command:
        keywords = 'Cocoa'
    elif 'number_of_bars' in command:
        keywords = 'COUNT'
    for x in param:
        if keywords in x:
            i = param.index(x)
            break
    yaxis = [ row[i] for row in result]

    bar_data = go.Bar(x=xaxis,y=yaxis)
    basic_layout = go.Layout()
    fig = go.Figure(data=bar_data, layout=basic_layout)
    fig.show()
    
            


def process_command(command):
    com_list = command.split(' ')
    high_level_cat  = ['bars','companies','countries','regions']
    try:
        high_level = high_level_cat.index(com_list[0])
        if high_level == 0:
            plot_flag, param, result = Bar(com_list[1:])
            if plot_flag:  _plot(param,result,command)
            print_func(param, result)
            return 0
        if high_level == 1:
            plot_flag, param, result = Company(com_list[1:])
            if plot_flag:  _plot(param,result,command)
            print_func(param, result)
            return 0
        if high_level == 2:
            plot_flag, param, result = Country(com_list[1:])
            if plot_flag:  _plot(param,result,command)
            print_func(param, result)
            return 0
        if high_level == 3:
            plot_flag, param, result = Region(com_list[1:])
            if plot_flag:  _plot(param,result,command)
            print_func(param, result)
            return 0
    except:
        print ('Command not recognized:',command)
    
def print_func(param,result):
    param = param.split(',')
    for row in result:
        row_output = ''
        for x in param:
            o = row[param.index(x)]
            if 'CocoaPercent' in x :
                row_output +='{:.0%}'.format(o) + '  '
                continue
            if 'Rating' in x :
                row_output +='{:.1f}'.format(o) + '  '
                continue
            if 'COUNT' in x :
                row_output +=str(o) + '  '
                continue


            
            if len(o) > 12:
                o = o[:12] + '...'


            row_output +='{:16s}'.format(o)
        print(row_output)   


def load_help_text():
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'help':
            print(help_text)
            continue
        else:
            process_command(response)
            
    print('bye')



# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    interactive_prompt()

