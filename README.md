## tele_uploader
Telegram bot script uploading media files with caption automatically from the desired folder.
- You need some prerequisite like MySQL and ffmpeg to make it work.

## how to install
1. download script
```shell
wget https://raw.githubusercontent.com/joongon/tele_uploader/main/tele_uploader.py
```
2. key in required information like telegram token, chat_id, target folder, etc.
3. run the script
* PREREQUISTE : MySQL DB configuration, ffmpeg tool

### MySQL 설정
1. DB 생성
```sql
CREATE DATABASE 데이터베이스이름;
```
2. TABLE 생성
```SQL
CREATE TABLE 테이블이름(
    id INT NOT NULL AUTO_INCREMENT,
    full_path TEXT,
    folder TEXT,
    file TEXT,
    extension VARCHAR(10),
    size FLOAT,
    time_mod DATETIME,
    time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tag TEXT,
    mark VARCHAR(10),
    remarks TEXT,
    PRIMARY KEY (id)
)
```
3. INDEX 설정(full_path 필드에 INDEX설정)
```SQL
    ALTER TABLE 테이블이름 ADD INDEX idx_full_path(full_path)
```