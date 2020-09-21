from tkinter import *
from tkcalendar import Calendar, DateEntry
from tkinter import filedialog

import os
import requests, zipfile, io,logging
import pandas as pd
from datetime import datetime,timedelta

# d_path= r"D:\Aesha\nse"

global No_of_download,Working_day,Non_Work_day, fin, folder_selected
No_of_download=0
Working_day=0
Non_Work_day=0
folder_selected = os.getcwd()
print(folder_selected)

today_date=datetime.now().strftime("%Y%b%d")
logging.basicConfig(filename="Log_"+today_date+".log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.INFO)

#Def for downloading and Unzipping the File
def req(zip_file_url, i):
    global No_of_download, fin, folder_selected
    r = requests.post(zip_file_url)
    status_code=r.status_code
    #print(status_code)
    #If status code is <> 200, it indicates that no data is present for that date. For example, week-end, or trading holiday.
    if status_code==200:
        No_of_download=No_of_download+1
        logger.info("File Available.Downloading")
        status = Label(root, text="Available").grid(row=i, column=1)
        z = zipfile.ZipFile(io.BytesIO(r.content))

        z.extractall(path=folder_selected)

        for file in z.namelist():
            df = pd.read_csv(file)
            modified = df[(df['SERIES'] == 'EQ') | (df['SERIES'] == 'BE')]
            exc = modified.replace(to_replace = 'BE', value = 'EQ')
            exc['TIMESTAMP'] = pd.to_datetime(exc['TIMESTAMP'], format = '%d-%b-%Y').dt.strftime("%d%m%Y")
            fin = exc[['SYMBOL', 'SERIES', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'TOTTRDQTY', 'TIMESTAMP']]

            if folder_selected:
                fin.to_csv(os.path.join(folder_selected, file[2:]), index = False)
            os.remove(file)

            # fin.to_csv(d_path + '\\'+ file, index=False)
        # z.extractall(path=d_path)
    else:
        logger.info("******File Not Available.Moving to next date.")
        status = Label(root, text="Not available").grid(row=i, column=1)

def logic(startdate, enddate):

    global No_of_download,Working_day,Non_Work_day

    daterange = pd.date_range(datetime.strptime(startdate, "%Y%b%d"),datetime.strptime(enddate, "%Y%b%d"))

    i = 6
    #Looping through each date, and downloading the file.
    for single_date in daterange:
        loop_date=single_date.strftime("%Y-%b-%d")
        year,month,date=loop_date.split('-')
        month=month.upper()
        weekday=single_date.weekday()
        #If day is not Saturday or Sunday,then proceed to download the file.
        if weekday not in [5,6]:
            Working_day=Working_day+1
            logger.info("Trying to download File of :"+loop_date)
            current = Label(root, text=single_date.strftime("%d-%b-%Y")).grid(row=i, column=0, pady=5)
            temp_zip_file_url = 'https://www1.nseindia.com/content/historical/EQUITIES/'+year+'/'+month+'/cm'+date+month+year+'bhav.csv.zip'
            req(zip_file_url=temp_zip_file_url, i=i)
            #print(temp_zip_file_url)
        else:
            Non_Work_day=Non_Work_day+1
        i = i + 1



    #print("Number of files downloaded:"+str(No_of_download))
    logger.info("****************************************************************************************")
    logger.info("No. of files downloaded="+str(No_of_download))
    logger.info("Span= " + startdate+ " to " + enddate )
    logger.info("No. of weekdays in the given time span="+str(Working_day))
    logger.info("****************************************************************************************")
    logging.shutdown()

    # exportCSV()


root = Tk()

root.geometry("600x500")

def pressed():

    startdate = cal1.get_date().strftime('%Y%b%d')
    enddate = cal2.get_date().strftime('%Y%b%d')
    # print(startdate, enddate)
    logic(startdate, enddate)

# fin.to_csv(export_file_path, index = False, header=True)

def exportCSV ():
    global fin, folder_selected

    # export_file_path = filedialog.asksaveasfile(defaultextension='.csv')
    folder_selected = os.path.normpath(filedialog.askdirectory(initial = '/'))



def setsame(e):
    cal2.set_date(cal1.get_date())

start = Label(root, text = "Start:", pady = 20)
cal1 = DateEntry(width=12, background='darkblue',
                foreground='white', borderwidth=2, date_pattern='dd/mm/yy')
cal1.bind("<<DateEntrySelected>>", setsame)


end = Label(root, text = "End:",  pady=10)
cal2 = DateEntry(width=12, background='darkblue',
                foreground='white', borderwidth=2, date_pattern='dd/mm/yy')

btn = Button(root, text="Download", command=pressed, padx=40)

# path = Label(root, text = folder_selected, pady=5)
curr = Label(root, text = "Current Path :    "+folder_selected, padx = 30, pady=5)

locn = Button(root, text="Change Path", command=exportCSV, padx=20)


start.grid(row=2, column=0)
cal1.grid(row=2, column=1)

end.grid(row=3, column=0)
cal2.grid(row=3, column=1)

btn.grid(row=4, column=1, pady=10)

# path.grid(row=4, column=1, pady=10, padx=10)
curr.grid(row=0, column=0, pady=10, padx=10)

locn.grid(row=1, column=0, padx=10)


root.mainloop()
