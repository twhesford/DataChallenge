import numpy as np

def date_array(years,cols,sep='-'):

    def makemonth(month):
        if month < 10:
            return str(0) + str(month)
        else:
            return str(month)
    def makeday(day):
        if day < 10:
            return str(0) + str(day)
        else:
            return str(day)
    
    
    num_lp_yrs = list(map(lambda x : True if x%4 ==0 else False,years)).count(True)
    
    out = np.full((365*len(years)+(num_lp_yrs),cols),np.nan,dtype=object)

    i = 0
    for year in years:

        months = [31,28,31,30,31,30,31,31,30,31,30,31]

        if year % 4 == 0:

            months[1] = 29

            mon = 0
            day = 0
            while mon < 12:
                out[i,0] = str(year) + sep + makemonth(mon+1) + sep + makeday(day+1)
                day += 1

                if day == months[mon]:
                    mon += 1
                    day = 0
                i += 1

        else:
            mon = 0
            day = 0
            while mon < 12:
                out[i,0] = str(year) + sep + makemonth(mon+1) + sep + makeday(day+1)
                day += 1

                if day == months[mon]:
                    mon += 1
                    day = 0
                i += 1   
    return out