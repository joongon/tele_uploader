
import os
import re
import requests
import pymysql as pq
import subprocess
import datetime
import time
from pathlib import Path

try:
    os.system('clear')
except:
    os.system('cls')

#Warning : 동영상 변환을 위해 ffmpeg가 설치되어 있어야 한다.
#initial condition ######################
target1 = '절대경로명' #폴더만 태크생성
target2 = '절대경로명' # 폴더 + 파일명 태그형성
###### TUB(Telegram Uploading Bot) 정보 #########################
TOKEN = '업로드 텔레그램 봇 토큰' #devexclusive_bot
chat_id = '업로드 대화방 ID' #DevforXELP

##### TUB(Telegram Uploading Bot) 실행 이슈/정보 Noti 전용 텔레그램 bot 정보
##### Optional, Skip 가능
TOKEN_message = '노티(시작/에러 등)용 텔레그램 봇 토큰' #notifier bot
chat_id_message = '노티대화방 ID' #noti channel

######## Telegram Server info ####################################
p_server = "사설 텔레그램 서버 주소" #사설 Telegram Server
o_server = "https://api.telegram.org" #공식 서버

######## MYSQL 정보 ####################
host = 'localhost' #MYSQL Server IP
id = 'MYSQL ID' # id
password = 'MYSQL PASSWORD' # password
database = 'MYSQL DB NAME' 
table = 'DB TABLE NAME'
#=======================================

dlay = 5 # Telegram Upload delay (unit: second)
#==================================================================


url_document = f'{p_server}/bot{TOKEN}/sendDocument'
url_photo = f'{p_server}/bot{TOKEN}/sendPhoto'
url_video = f'{p_server}/bot{TOKEN}/sendVideo'
url_animation = f'{p_server}/bot{TOKEN}/sendAnimation'
url_message = f'{o_server}/bot{TOKEN_message}/sendMessage'

#==========================================
def name_cleaner(trash):
    p = re.compile(r'\[|\]|\(|\)|-|_|,|=')
    removed = p.sub('', trash)
    return removed

def tele_Message(chat_id, url_message):
    params = {'chat_id': chat_id, 'text':'Pure BOT 테스트입니다.'}
    result = requests.get(url_message, params=params)
    return result

def trash_remover(target):
    p = re.compile('[|]')
    cleaned = p.sub('', target)
    return cleaned

def ts_converter(mtime): #path = timestamp가 필요한 폴더의 절대경로
    #unix time : 1970년 1월 1일 00:00:00 UTC로부터 현재까지의 누적된 초(seconds)의 값
    dt = datetime.datetime.fromtimestamp(mtime) #datetime 형식으로 변경
    mtime_result = dt.strftime('%Y-%m-%d %H:%M:%S') # yyyy-mm-dd hh:mm:ss 형식의(iso format)으로 변경
    return mtime_result

def path_curer(path):
    path = path[1:]
    path2 = path.split('/')
    cured_path = ""
    for item in path2:
        cured_path += "/" + "'" + item + "'"
    return cured_path

class Scanner:
    list_file = [] #class 변수
    def __init__(self, target):
        self.target = target
    
    def scanner(self):            
            list = os.scandir(self.target)
            for entry in list:
                if entry.is_dir():
                    Scanner(entry.path).scanner()
                else:
                    path_info = entry.path
                    time_mod_info = entry.stat().st_mtime
                    file_size_info = entry.stat().st_size
                    file_info = [path_info, file_size_info, time_mod_info]
                    Scanner.list_file.append(file_info)
            return Scanner.list_file #[[full_path, file_size, time_mod], [full_path, file_size, time_mod], ...]
    
class DB_Comparison:
    def __init__(self):
        pass
    def db_compare(self, full_path): #full_path
        db = pq.connect(host=host, user=id, password=password, db=database, charset='utf8mb4')
        cur = db.cursor()
        # query = f'SELECT full_path FROM {table} WHERE full_path = %s AND mark = %s'
        query = f'SELECT full_path FROM {table} WHERE full_path = %s'
        result = cur.execute(query, (full_path[0]))
        db.close()
        return result

class Tagger:
    def __init__(self, full_path): 
        self.full_path = full_path

    def path_parser(self): 
        folder_path_temp = ""
        split_item = self.full_path.split('/')
        for i in range(len(split_item) -1):
            folder_path_temp += split_item[i] + '/'
            folder_path = folder_path_temp[:-1]
        file = split_item[-1]
        full_path = folder_path + '/' + file
        extension = file.split('.')[-1]
        list_tag_info = [full_path, folder_path, file, extension]
        return list_tag_info

    def tag_maker(self, list_path_info, option=1): #list_path_into = [full_path, folder_path, file, extension]
        if option == 1:
            list_info = name_cleaner(list_path_info[1])
            print(list_info, '---------------> list_info')
            list_folder_info = list_info.split('/')
            
            tag_info = ""
            for i in range(6, len(list_folder_info)):
                tag_info_2nd = list_folder_info[i].split()
                for item in tag_info_2nd:
                    tag_info += " #" + item
        elif option == 2:
            list_info1 = name_cleaner(list_path_info[1])
            list_info2 = name_cleaner(list_path_info[2])

            list_folder_info1 = list_info1.split('/')
            tag_info1 = ""
            for i in range(6, len(list_folder_info1)):
                tag_info_2nd1 = list_folder_info1[i].split()
                for item in tag_info_2nd1:
                    tag_info1 += " #" + item
            
            list_file_info = list_info2.split('.')
            file_name_only = ""
            tag_info2 = ""
            for i in range(len(list_file_info) - 1):
                file_name_only += list_file_info[i]
                cured_file_name = name_cleaner(file_name_only)
                list_cured_name = cured_file_name.split()
                for item in list_cured_name:
                    tag_info2 += " #" + item
            tag_info = tag_info1 + tag_info2
        return tag_info

class DB_Marker:
    def __init__(self): #path = full_path
        pass
        
    def db_marker(self, path):
        db = pq.connect(host=host, user=id, password=password, db=database, charset='utf8mb4')
        cur = db.cursor()
        query = f"UPDATE {table} SET mark = '1' WHERE full_path = %s"
        result = cur.execute(query, path)
        db.commit()
        db.close()
        return result

class DB_Handler:
    def __init__(self, *args): #list_2nd_for_path_info in tuple or list in tuple
        self.args = args

    def db_prep(self, option): # item = ['path', size, 'time_mode(unix_time)']
        print(self.args, "-----------> self.args") #삭제
        tagger = Tagger(self.args[0][0]) #args[0][0] = full_path
        main_info = tagger.path_parser()
        print(main_info, "-------> main_info") # to be deleted
        info_size = self.args[0][1]
        info_time = ts_converter(self.args[0][2])
        if option == 2:
            info_tag = tagger.tag_maker(main_info, option) 
        else:
            info_tag = tagger.tag_maker(main_info)
        aux_info = [info_size, info_time, info_tag, '0']
        total_info_list = main_info + aux_info
        return total_info_list #[full_path, folder, file, extension, size, time_mod, tag, mark='0']

    def db_input(self):
        large_list = self.args[0]
        db = pq.connect(host=host, user=id, password=password, db=database, charset='utf8mb4')
        cur = db.cursor()
        query = f'INSERT INTO {table} (full_path, folder, file, extension, size, time_mod, tag, mark) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        try:
            result = cur.executemany(query, large_list)
            print(result, '-----------------> DB Insert Result')
            db.commit()
        except Exception as e:
            er_message = f"Error Message for DB register: {e}\n\
                (XELP soft_flavour1 bot)DB 등록 중 문제가 생겼습니다."
            print(er_message)
            
            try:
                params = {'chat_id': chat_id_message, 'text': er_message}
                requests.get(url_message, params=params)
            except:
                pass
        db.close()

    def db_reader(self):
        db = pq.connect(host=host, user=id, password=password, db=database, charset='utf8mb4')
        cur = db.cursor()
        query = f"SELECT DISTINCT full_path, tag, extension FROM {table} WHERE mark = '0'"
        cur.execute(query)
        tobe_uploaded = cur.fetchall()
        print(tobe_uploaded, '---------------> to be uploaded')
        db.close()
        return tobe_uploaded

class Uploader:    
    def __init__(self, second_order_tuple):
        self.second_order_tuple = second_order_tuple
        
    def tele_uploader(self): #((full_path, tag, extension), (full_path, tag, extension), ...)
        tuple_info = self.second_order_tuple
        list_result = []
        video_group = ['avi', 'mp4', 'mov', 'MOV', 'MP4', 'AVI']
        animation_group = ['gif', 'GIF']
        photo_group = ['jpg', 'jpeg', 'png', 'PNG', 'JPG', 'JPEG', 'webp']
        singularity_group = ['webm', 'ts', 'TS', 'mkv', 'MKV']
        marker = DB_Marker()

        try: 
            for item in tuple_info:
                print(item, '------------------> item')
                path = item[0]
                print(path, "------------------> path")
                file_temp = path.split('/')[-1]
                list_file_temp = file_temp.split('.')
                file = ""
                for i in range(len(list_file_temp) - 1):
                    file += list_file_temp[i]
                tag1 = file    
                tag2 = item[1]
                tag = tag1 + '\n' + tag2
                print(tag, "-----------------> tag")
                extension = item[2]
                print(extension, "-------------> extension")
                if extension in video_group:
                    data = {'chat_id': chat_id, 'caption': tag, 'supports_streaming': True}
                    files = {'video': open(path, 'rb')}
                    result = requests.post(url_video, files=files, data=data)
                    time.sleep(dlay)
                    marker.db_marker(path)
                elif extension in photo_group:
                    data = {'chat_id': chat_id, 'caption': tag}
                    files = {'photo': open(path, 'rb')}
                    result = requests.post(url_photo, files=files, data=data)
                    time.sleep(dlay)
                    marker.db_marker(path)
                elif extension in animation_group:
                    data = {'chat_id': chat_id, 'caption': tag}
                    files = {'animation': open(path, 'rb')}
                    result = requests.post(url_animation, files=files, data=data)
                    time.sleep(dlay)
                    marker.db_marker(path)

                elif extension in singularity_group:
                    path = path_curer(path)
                    # shell1 = f"ffmpeg -i {path} -pix_fmt rgb24 output.gif"
                    shell1 = f"ffmpeg -y -i {path} output.mp4"
                    shell2 = f"rm -f output.mp4"
                    subprocess.call(shell1, shell=True)
                    data = {'chat_id': chat_id, 'caption': tag, 'supports_streaming': True}
                    files = {'video': open('output.mp4', 'rb')}
                    result = requests.post(url_video, files=files, data=data)
                    subprocess.call(shell2, shell=True)
                    time.sleep(dlay)
                    marker.db_marker(path)

                elif extension == 'db' or extension == 'html':
                    result = ""
                    print(marker.db_marker(path), '-------------> db_marker_result')
                    print(path, '---------------> path for db_marker')
                else:
                    data = {'chat_id': chat_id, 'caption': tag}
                    files = {'document': open(path, 'rb')}
                    result = requests.post(url_document, files=files, data=data)
                    time.sleep(dlay)
                list_result.append(result)
       
        except Exception as e:
            print(e)
            text = "()Telegram 업로드 중에 문제가 생겼습니다. DB에 등록된 파일과 실제 파일경로가 다르거나 없습니다."
            print(text)
            params = {'chat_id': chat_id_message, 'text': text}
            requests.get(url_message, params=params)
        return list_result

class Main:
    
    def __init__(self, target, option=1):
        self.target = target
        self.option = option
    
    def runner(self):
        db_object = []
        scan = Scanner(self.target)
        dbcompare = DB_Comparison()
        for item in scan.scanner(): # item = ['full_path', size, 'time_mode(unix_time)']
            if dbcompare.db_compare(item[0]) == 0:
                db_object.append(DB_Handler(item).db_prep(self.option))
            else:
                print('Redundancy, not processed with DB.')
        
        if db_object == []:
            pass
        else:
            print(db_object, "-----------> db_object")
            DB_Handler(db_object).db_input() # db_object1= [[full_path, folder, file, extension, size, time_mod, tag], [full_path, folder, file, extension, size, time_mod, tag], ...]
        Uploader(DB_Handler().db_reader()).tele_uploader()
        return print('All processed')
        
if __name__ == '__main__':
    try:
        ex1 = Main(target1)
    except Exception as e:
        pass
    try:
        ex2 = Main(target2, 2)
    except Exception as e:
        pass
    try:
        ex1.runner()
    except Exception as e:
        pass
    try:
        ex2.runner()
    except Exception as e:
        pass


    