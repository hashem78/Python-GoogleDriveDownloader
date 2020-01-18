from __future__ import print_function
import os
from apiclient.discovery import build
from httplib2 import Http, HttpLib2Error
from oauth2client import file, client, tools
import requests



try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except:
    flags = None

folderType = "application/vnd.google-apps.folder"
dlall = False
mTypes = {
        "html":"text/html",
        "zip":"application/zip",
        "plain-text":"text/plain",
        "rtf":"application/rtf",
        "openoffice-doc":"application/vnd.oasis.opendocument.text",
        "openoffic-sheet":"x-vnd.oasis.opendocument.spreadsheet",
        "openoffice-presentation":"application/vnd.oasis.opendocument.presentation",
        "pdf":"application/pdf",
        "msoffice-doc":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "msoffice-excel":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        "msoffice-powerpoint":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "csv":"text/csv",
        "jpeg":"image/jpeg",
        "png":"image/png",
        "svg":"image/svg+xml",
        "json":"application/vnd.google-apps.script+json",
}
class FD:
    def __init__(self,fid=""):
        self.__SCOPES = "https://www.googleapis.com/auth/drive"
        self.__store = file.Storage('storage.json')
        self.__creds = self.__store.get()
        if not self.__creds or self.__creds.invalid:
            flow = client.flow_from_clientsecrets("credentials.json",scope=self.__SCOPES)
            self.__creds = tools.run_flow(flow,self.__store,flags) if flags else tools.run(flow,self.__store)
        self.__DRIVE = build('drive', 'v3',http=self.__creds.authorize(Http()))
        #empty list to store dir/file names
        self.__files = list()
        self.__fid = fid
        self.get_folder_id()
    def get_folder_id(self):
        if self.__fid == "":
            self.__fid = input("Enter folderId: ")
       # print("What to look for?")
       # for item in mTypes:
       #     print(item)
       # uchoice = input("Enter choice: ")
       # self.__files = self.__DRIVE.files().list(q="mimeType='%s'" % mTypes[uchoice]).execute().get("files",[])
       #self.__files = self.__DRIVE.files().get(fileId="1d10Awz2P99PuWOYuxVGpiVR-PhDct1hD").execute()
       #self.__files =+
       # self.__DRIVE.files().get(fileId = "1d10Awz2P99PuWOYuxVGpiVR-PhDct1hD",fields="children").execute()
        try:
            isFolder = self.__DRIVE.files().get(fileId = self.__fid,fields="mimeType").execute()
            if not isFolder['mimeType'] == folderType:
                raise TypeError()
            else:
                self.__files = self.__DRIVE.files().list(q="'%s' in parents" % self.__fid).execute().get('files',[])
        except TypeError:
            print("NOT A FOLDER, exiting...")
            exit()
        except:
            print("An httpError occured, exiting...")
            exit()

    def print_file_ids(self):
        for f in self.__files:
            print(f)
    def get_selections(self):
        selections = dict()
        ids = list()
        index = 1
        global dlall

        for f in self.__files:
            if not dlall:
                print(index,f['name'])
            selections[index] = [f['id'],f['name'],f['mimeType']]
            index += 1
        if not dlall:
            print(index,"All")
            choices = input("Enter choice(s), seperated by spaces: ")
        else:
            choices = index
        #error checking
        try:
            if int(choices) == index:
                dlall = True
                return list(selections.values())
            else:
                choices = list(map(int,choices.split(' ')))
        except ValueError as ve:
            print(ve.args," is not a numeric, exiting...")
            return []
    
        try:
            for choice in choices:
                ids.append(selections[choice])
            return ids
        except KeyError as ke:
            print(ke.args," is not a valid selection, exiting...")
            return []

    def download(self):
        items = self.get_selections()
        for item in items:
            if item[2] == folderType:
                newFolder = FD(item[0])
                newFolder.download()
            else:
                data = self.__DRIVE.files().get_media(fileId = item[0]).execute()
                if data:
                    with open("%s"%item[1],'wb') as fh:
                        fh.write(data)
                    print("DOWNLOADED ",item[1])
def main():
    Test1 = FD()
    Test1.get_folder_id()
    #Test1.print_file_ids()
    Test1.download()
main()