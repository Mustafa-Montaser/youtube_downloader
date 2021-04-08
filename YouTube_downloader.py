from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import sqlite3
import time
from datetime import datetime
import pyperclip
import pytube
from pytube import YouTube
# from pytube.request import get
# python -m pip install git+https://github.com/nficano/pytube

i_from = 1
i_to = 1
playlist_length = 0
folder_name = ""
downloadState = False
urlState = False
playlistRangeState = False
downloadedVideoList = []

db = sqlite3.connect("data.db")
db.execute("CREATE TABLE IF NOT EXISTS download_info (id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT, file_location TEXT, file_url TEXT, date_time TEXT, epoch_timestamp INTEGER)")
db.commit()
db.close()

# functions

def get_download_type(_downloadType):
    global playlistRangeState
    urlEntry.config(state="normal")
    if _downloadType == "singleVideo":
        downloadTypeRadio1.config(bd=7)
        downloadTypeRadio2.config(bd=2)
        downloadTypeCheckLabel.config(text="Downloading for single video", fg="#292a2d")
        urlPlaylistFromEntry.config(state="disabled")
        urlPlaylistToEntry.config(state="disabled")
        playlistRangeState = True
    elif _downloadType == "playlist":
        downloadTypeRadio1.config(bd=2)
        downloadTypeRadio2.config(bd=7)
        downloadTypeCheckLabel.config(text="Downloading for playlist", fg="#292a2d")
        urlPlaylistFromEntry.config(state="normal")
        urlPlaylistToEntry.config(state="normal")
    download_state()


def get_quality_value(_qualityValue):
    if _qualityValue == "360p":
        urlQualityRadio1.config(bd=7, bg="#fff", fg="black")
        urlQualityRadio2.config(bd=2, bg="#1c2b3e", fg="#fff")
        urlQualityRadio3.config(bd=2, bg="#1c2b3e", fg="#fff")
    elif _qualityValue == "720p":
        urlQualityRadio1.config(bd=2, bg="#1c2b3e", fg="#fff")
        urlQualityRadio2.config(bd=7, bg="#fff", fg="black")
        urlQualityRadio3.config(bd=2, bg="#1c2b3e", fg="#fff")
    elif _qualityValue == "audio":
        urlQualityRadio1.config(bd=2, bg="#1c2b3e", fg="#fff")
        urlQualityRadio2.config(bd=2, bg="#1c2b3e", fg="#fff")
        urlQualityRadio3.config(bd=7, bg="#fff", fg="black")
    download_state()


def open_location():
    global folder_name
    folder_name = filedialog.askdirectory()
    if len(folder_name) > 1:
        locationCheckLabel.config(text=folder_name, fg="green")
    else:
        locationCheckLabel.config(text="Please select download path", fg="red")
    download_state()


def callback_URL(_sv):
    global urlState
    url_ = _sv.get()
    if len(url_) != 0: 
        try:
            videoLink = YouTube(url_) 
            urlvideoTitleLabel.config(text="Video title         :   " + videoLink.title)
            videoLen = videoLink.length
            if videoLen > 60:
                videoLen2 = str(int(videoLen / 60)) + " min : " + str(videoLen - int(videoLen / 60) * 60) + " sec"
                urlVideoLengthLabel.config(text="Video length    :   " + str(videoLen2))
            else:
                urlVideoLengthLabel.config(text="Video length    :   " + str(videoLen) + " sec")
            urlPlaylistFromEntry.delete(0, "end")
            urlPlaylistToEntry.delete(0, "end")
            if downloadType.get() == "playlist":
                playlist = pytube.Playlist(url_)
                urls_videos = playlist.video_urls
                global playlist_length
                playlist_length = len(urls_videos)
                urlPlaylistFromEntry.config(state="normal")
                urlPlaylistToEntry.config(state="normal")
                urlPlaylistFromEntry.delete(0, "end")
                urlPlaylistToEntry.delete(0, "end")
                urlPlaylistFromEntry.insert(0, "1")
                urlPlaylistToEntry.insert(0, str(playlist_length))
                global i_from, i_to
                i_from = 1
                i_to = playlist_length
                global playlistRangeState
                playlistRangeState = True
            urlCheckLabel.config(text="")
            urlCheckplaylistRangeLabel.config(text="")
            urlState = True
        except:
            urlState = False
            urlCheckLabel.config(text="URL error. please insert correct youtube video url", fg="red")
    download_state()


def paste_url():
    if downloadType.get() == "singleVideo" or downloadType.get() == "playlist": 
        url.set("")  
        url.set(pyperclip.paste())
    

def clear_url():
    if downloadType.get() == "singleVideo" or downloadType.get() == "playlist":  
        url.set("")
        urlvideoTitleLabel.config(text="Video title         :   ")
        urlVideoLengthLabel.config(text="Video length    :   ")
        urlPlaylistFromEntry.delete(0, "end")
        urlPlaylistToEntry.delete(0, "end")
        downloadButton.config(state="disabled")


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    per = str(format(percentage_of_completion, '.2f')) + " %"
    downloadProgressLabel.config(text=per)
    downloadProgressLabel.update()


def on_complete(_messageOnComplete, ___downloadType, _file_name, __url):
    global i_from
    global db
    clearAll = False
    if ___downloadType == "playlist":
        _text = "Video number " + str(i_from + 1) + " is downloaded successfully"
        downloadProgressLabel.config(text=_text)
        downloadProgressLabel.update()
        downloadedVideoList.append(_file_name)
        if i_from == i_to:
            msg = ""
            for i in downloadedVideoList:
                msg += i + "\n"
            _message = "All selected videos are downloaded successfully\n"
            _message += "=======================================\n"
            _message += msg
            messagebox.showinfo(title="YTD message", message=_message)
            downloadedVideoList.clear()
            # get all videos titles to be displayed
            clearAll = True
    
    elif ___downloadType == "singleVideo":
        downloadProgressLabel.config(text="Video is downloaded successfully")
        messagebox.showinfo(title="YTD message", message=_messageOnComplete)
        clearAll = True

    date_time = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
    time_object = time.strptime(date_time, "%d/%m/%Y  %H:%M:%S")
    epoch_timestamp = int(time.mktime(time_object))
    db = sqlite3.connect("data.db")
    db.execute("INSERT INTO download_info (file_name, file_location, file_url, date_time, epoch_timestamp) VALUES (?, ?, ?, ?, ?)", (_file_name, folder_name, __url, date_time, epoch_timestamp))
    db.commit()
    db.close()
    if clearAll:
        downloadVideoTitleLabel.config(text="")
        downloadProgressLabel.config(text="")
        url.set("")
        urlEntry.config(state="disabled")
        urlvideoTitleLabel.config(text="Video title         : ")
        urlVideoLengthLabel.config(text="Video length    : ")
        urlPlaylistFromEntry.delete(0, "end")
        urlPlaylistToEntry.delete(0, "end")
        downloadType.set(" ")
        qualityValue.set(" ")
        downloadTypeRadio1.config(bd=2)
        downloadTypeRadio2.config(bd=2)
        urlQualityRadio1.config(bg="#1c2b3e", fg="#fff", bd=2)
        urlQualityRadio2.config(bg="#1c2b3e", fg="#fff", bd=2)
        urlQualityRadio3.config(bg="#1c2b3e", fg="#fff", bd=2)
        downloadTypeCheckLabel.config(text="")
        global downloadState
        downloadState = False
        downloadButton.config(state="disabled")
        clearAll = False



def download_video(_url, __qualityValue, _QualityState, __downloadType):
    file = YouTube(_url) 
    file.register_on_progress_callback(on_progress)
    if __qualityValue == "360p":
        ready = file.streams.filter(progressive=True, file_extension="mp4", res="360p").first()
        _QualityState = True
    elif(__qualityValue == "720p"):
        ready = file.streams.filter(progressive=True, file_extension="mp4", res="720p").last()
        _QualityState = True
    elif(__qualityValue == "audio"):
        ready = file.streams.filter(only_audio=True).first()
        _QualityState = True

    if _QualityState:
        file_name = file.title
        downloadVideoTitleLabel.config(text=file_name)
        if __downloadType == "playlist":
            if playlist_length <= 99:
                if i_from + 1 <= 9:
                    file_name = "0" + str(i_from + 1) + "- " + file.title
                else:
                    file_name = str(i_from + 1) + "- " + file.title
            elif playlist_length <= 999:
                if i_from + 1 <= 9:
                    file_name = "00" + str(i_from + 1) + "- " + file.title
                elif i_from + 1 <= 99:
                    file_name = "0" + str(i_from + 1) + "- " + file.title
                else:
                    file_name = str(i_from + 1) + "- " + file.title
        try:
            ready.download(folder_name, file_name)
            downloadButton.config(state="disabled")
        except:
            downloadProgressLabel.config(text="This video doesn't support 720p. Will be downloaded as 360p")
            downloadProgressLabel.update()
            time.sleep(3)
            ready = file.streams.filter(progressive=True, file_extension="mp4", res="360p").first()
            ready.download(folder_name, file_name)
            
        messageOnComplete = "Downloaded successfully"
        messageOnComplete += "\n======================================"
        messageOnComplete += "\n File Name: \n " + file.title
        on_complete(messageOnComplete, __downloadType, file_name, _url)
        messageOnComplete = ""


def download():
    global i_to
    global i_from
    global playlist_length
    _qualityValue = qualityValue.get()
    qualityState = False
    if downloadState and urlState and playlistRangeState and folder_name != " ": 
        try:
            _url = url.get()
            _downloadType = downloadType.get()
            if _downloadType == "playlist":
                _playlist = pytube.Playlist(_url)  #try
                _urls_videos = _playlist.video_urls
                playlist_length = len(_urls_videos)
                try:
                    i_from = int(urlPlaylistFromEntry.get())   #try
                    i_to = int(urlPlaylistToEntry.get())   #try
                    if i_from < i_to and i_from > 0 and i_to <= playlist_length:
                        i_from = i_from - 1
                        i_to = i_to - 1
                        urlCheckplaylistRangeLabel.config(text="")
                        while i_from <= i_to:
                            download_video(_urls_videos[i_from], _qualityValue, qualityState, _downloadType)
                            i_from += 1
                    else:
                        urlCheckplaylistRangeLabel.config(text="Playlist Range error")
                except:
                    urlCheckplaylistRangeLabel.config(text="Playlist Range error")       
            elif _downloadType == "singleVideo":
                urlCheckplaylistRangeLabel.config(text="")
                download_video(_url, _qualityValue, qualityState, _downloadType)
        except:
            urlCheckLabel.config(text="URL error. please insert correct youtube video url", fg="red")


def playlist_range_check(event):
    global playlistRangeState
    global i_from
    global i_to
    try:
        i_from = int(urlPlaylistFromEntry.get()) 
        i_to = int(urlPlaylistToEntry.get()) 
        if (i_from < i_to and i_from > 0 and i_to <= playlist_length and downloadType.get() == "playlist") or downloadType.get() == "singleVideo":
            urlCheckplaylistRangeLabel.config(text="")
            playlistRangeState = True
        else:
            urlCheckplaylistRangeLabel.config(text="Playlist Range error")
            playlistRangeState = False
    except:
        urlCheckplaylistRangeLabel.config(text="Playlist Range error")
        playlistRangeState = False
    download_state()


def download_state():
    global downloadState
    if downloadType.get() != " " and urlState and playlistRangeState and qualityValue.get() != " " and len(folder_name) > 1:
        downloadState = True
        downloadButton.config(state="normal")
    else:
        downloadState = False
        downloadButton.config(state="disabled")



def clear_download_history(_tv):
    db = sqlite3.connect("data.db")
    dbCurser = db.cursor()
    dbCurser.execute("DELETE FROM download_info")
    dbCurser.execute("UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'download_info'")
    check = dbCurser.execute("SELECT EXISTS (SELECT 1 FROM download_info)")
    db.commit()
    if not check.fetchone()[0]:
        for row in _tv.get_children():
            _tv.delete(row)
    db.close()


def get_history_info(event, _tv):
    row = _tv.focus()[0]
    rowData = _tv.item(row, "values")
    pyperclip.copy(rowData[3])


def browse_history():
    db = sqlite3.connect("data.db")
    dbCurser = db.cursor()
    data = dbCurser.execute("SELECT id, file_name, file_location, file_url, date_time FROM download_info")
    datalist = data.fetchall()
    db.commit()
    db.close()
    root2 = Tk()
    root2.title("YTD MANS DOWNLOADER HISTORY")
    # root2.iconbitmap("F:/1-ENGINEERING/COURSES/python/z_scripts/YTD_REV2/logo.ico")
    root2.geometry("900x700")
    root2.grid_rowconfigure(0, weight=1)
    root2.grid_columnconfigure(0, weight=1)
    tv = ttk.Treeview(root2)
    tv.grid(row=0, column=0, sticky="nsew", columnspan=5)
    tv["column"] = ("id", "file_name", "file_location", "file_url", "date_time")
    tv.column("#0", width=0, stretch="no")
    tv.column("id", width=10, anchor="center")
    tv.column("file_name", width=130, anchor="w")
    tv.column("file_location", width=130, anchor="w")
    tv.column("file_url", width=130, anchor="w")
    tv.column("date_time", width=100, anchor="center")
    tv.heading("#0", text="")
    tv.heading("id", text="ID", anchor="center")
    tv.heading("file_name", text="Title", anchor="center")
    tv.heading("file_location", text="Location", anchor="center")
    tv.heading("file_url", text="URL", anchor="center")
    tv.heading("date_time", text="Date and Time", anchor="center")
    for row in range(len(datalist)):
        tv.insert(parent="", index="end", iid=row, text="", values=datalist[row])
    tv.bind("<Double-1>", lambda event: get_history_info(event, tv))
    clearHistoryButton = Button(root2, text="Delete All", font=("jost", 12,), bg="#292a2d", fg="#fff", bd=3, cursor="hand2", command=lambda: clear_download_history(tv))
    clearHistoryButton.grid(row=1, column=0)
    

    

### GUI ###
# root
root = Tk()
root.title("YTD MANS DOWNLOADER")
# root.iconbitmap("F:/1-ENGINEERING/COURSES/python/z_scripts/YTD_REV2/logo.ico")
root.geometry("650x700")
root.config(bg="#1c2b3e")
root.resizable(False, False)

# root building
# choosing type of download
downloadTypeFrame = LabelFrame(root, bg="#486b94", bd=3, width=640, height=140)
downloadTypeFrame.pack()
downloadTypeLabel = Label(downloadTypeFrame, text="Please select type of download", bg="#486b94", fg="#fff", font=("jost", 15, "bold"))
downloadTypeLabel.place(x=300, y=20, anchor="center")
downloadType = StringVar()
downloadType.set(" ")
downloadTypeRadio1 = Radiobutton(downloadTypeFrame, text="Single Video", value="singleVideo", variable=downloadType, bg="#486b94", font=("jost", 12, "bold"), relief="sunken", cursor="hand2", command=lambda: get_download_type(downloadType.get()))
downloadTypeRadio1.place(x=190, y=70, anchor="center", width=150, height=50)
downloadTypeRadio2 = Radiobutton(downloadTypeFrame, text="Playlist", value="playlist", variable=downloadType, bg="#486b94", font=("jost", 12, "bold"), relief="sunken", cursor="hand2", command=lambda: get_download_type(downloadType.get()))
downloadTypeRadio2.place(x=410, y=70, anchor="center", width=150, height=50)
downloadTypeCheckLabel = Label(downloadTypeFrame, text="", font=("jost", 12, "bold"), fg="#fff", bg="#486b94")
downloadTypeCheckLabel.place(x=300, y=115, anchor="center")

# URL get link 
urlFrame = LabelFrame(root, bg="#1c2b3e", bd=3, width=640, height=320)
urlFrame.pack()
urlLabel = Label(urlFrame, text="Enter the URL of the video", font=("jost", 15, "bold"), bg="#1c2b3e", fg="#fff")
urlLabel.place(x=300, y=30, anchor="center")
urlClearButton = Button(urlFrame, text="C", font=("jost", 12,), bg="#292a2d", fg="#fff", bd=3, cursor="hand2", command=clear_url)
urlClearButton.place(x=20, y=75, anchor="center", width=25, height=30)
urlPasteButton = Button(urlFrame, text="P", font=("jost", 12,), bg="#292a2d", fg="#fff", bd=3, cursor="hand2", command=paste_url)
urlPasteButton.place(x=50, y=75, anchor="center", width=25, height=30)
url = StringVar()
url.trace("w", lambda name, index, mode, sv=url: callback_URL(sv))
urlEntry = Entry(urlFrame, font=("jost", 12), textvariable=url, state="disabled")
urlEntry.place(x=320, y=75, anchor="center", width=500, height=30)
urlCheckLabel = Label(urlFrame, text="", font=("jost", 12), bg="#1c2b3e", fg="red")
urlCheckLabel.place(x=300, y=110, anchor="center")
urlvideoTitleLabel = Label(urlFrame, text="Video title         : ", font=("jost", 12, "bold"), bg="#1c2b3e", fg="#d7c0aa")
urlvideoTitleLabel.place(x=50, y=130, anchor="w")
urlVideoLengthLabel = Label(urlFrame, text="Video length    : ", font=("jost", 12, "bold"), bg="#1c2b3e", fg="#d7c0aa")
urlVideoLengthLabel.place(x=50, y=170, anchor="w")
urlPlaylistLabel = Label(urlFrame, text="Playlist length :    From", font=("jost", 12, "bold"), bg="#1c2b3e", fg="#d7c0aa")
urlPlaylistLabel.place(x=50, y=210, anchor="w")
urlPlaylistFromEntry = Entry(urlFrame, font=("jost", 12), state="disabled", justify='center')
urlPlaylistFromEntry.place(x=260, y=210, anchor="center", width=50, height=25)
urlPlaylistFromEntry.bind("<KeyRelease>", playlist_range_check)
urlPlaylistLabel2 = Label(urlFrame, text=" To ", font=("jost", 12, "bold"), bg="#1c2b3e", fg="#d7c0aa")
urlPlaylistLabel2.place(x=320, y=210, anchor="center")
urlPlaylistToEntry = Entry(urlFrame, font=("jost", 12), state="disabled", justify='center')
urlPlaylistToEntry.place(x=370, y=210, anchor="center", width=50, height=25)
urlPlaylistToEntry.bind("<KeyRelease>", playlist_range_check)
urlCheckplaylistRangeLabel = Label(urlFrame, text="", font=("jost", 12), bg="#1c2b3e", fg="red")
urlCheckplaylistRangeLabel.place(x=405, y=210, anchor="w")
urlQualityLabel = Label(urlFrame, text="Choose Quality : ", font=("jost", 12, "bold"), bg="#1c2b3e", fg="#d7c0aa")
urlQualityLabel.place(x=50, y=270, anchor="w")
qualityValue = StringVar()
qualityValue.set(" ")
urlQualityRadio1 = Radiobutton(urlFrame, text="360p", value="360p", variable=qualityValue, bg="#1c2b3e", fg="#fff", font=("jost", 12, "bold"), relief="sunken", cursor="hand2", command=lambda: get_quality_value(qualityValue.get()))
urlQualityRadio1.place(x=250, y=270, anchor="center", width=110, height=50)
urlQualityRadio2 = Radiobutton(urlFrame, text="720p", value="720p", variable=qualityValue, bg="#1c2b3e", fg="#fff", font=("jost", 12, "bold"), relief="sunken", cursor="hand2", command=lambda: get_quality_value(qualityValue.get()))
urlQualityRadio2.place(x=370, y=270, anchor="center", width=110, height=50)
urlQualityRadio3 = Radiobutton(urlFrame, text="Audio", value="audio", variable=qualityValue, bg="#1c2b3e", fg="#fff", font=("jost", 12, "bold"), relief="sunken", cursor="hand2", command=lambda: get_quality_value(qualityValue.get()))
urlQualityRadio3.place(x=490, y=270, anchor="center", width=110, height=50)

# select file location
locationFrame = LabelFrame(root, bg="#1c2b3e", bd=3, width=640, height=65)
locationFrame.pack()
locationLabel = Label(locationFrame, text="Select file location : ", font=("jost", 14, "bold"), bg="#1c2b3e", fg="#fff")
locationLabel.place(x=20, y=30, anchor="w")
locationButton = Button(locationFrame, text="select location", font=("jost", 12,), bg="#292a2d", fg="#fff", bd=3, cursor="hand2", command=open_location)
locationButton.place(x=215, y=32, anchor="w")
locationCheckLabel = Label(locationFrame, text="", font=("jost", 12,), bg="#1c2b3e", fg="red")
locationCheckLabel.place(x=340, y=32, anchor="w")

# download
downloadFrame = LabelFrame(root, bg="#1c2b3e", bd=3, width=640, height=150)
downloadFrame.pack()
downloadButton = Button(downloadFrame, text="DOWNLOAD", font=("jost", 12,), bg="#292a2d", fg="#fff", bd=3, cursor="hand2", state="disabled", command=download)
downloadButton.place(x=200, y=25, anchor="center", width=350, height=35)
downloadBrowseHistory = Button(downloadFrame, text="History", font=("jost", 12,), bg="#292a2d", fg="#fff", bd=3, cursor="hand2", command=browse_history)
downloadBrowseHistory.place(x=500, y=25, anchor="center", width=150, height=35)
downloadVideoTitleLabel = Label(downloadFrame, text="", font=("jost", 14), bg="#1c2b3e", fg="green")
downloadVideoTitleLabel.place(x=300, y=70, anchor="center")
downloadProgressLabel = Label(downloadFrame, text="", font=("jost", 14), bg="#1c2b3e", fg="#f3aa63")
downloadProgressLabel.place(x=300, y=110, anchor="center")

# RUN
root.mainloop()


