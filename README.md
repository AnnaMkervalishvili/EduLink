EduLink is a educational webstie where instructors can register themselves, create classes and student can join these classes ( students part will be added later)

currently Instructors can:
- login to their account or register
- edit private info like Name, profile picture etc.
- create and delete classes
   - edit and delete homeworks, Materials and announcements
   - change info about classes
- see their curriculum that is created based on registered class's times

Technologies that I used are:  
- Backend - flask framework
 
  - flask_login : for authentication
  - flask-SQLAlchemy : to connect flask to SQLite 
  - Werkzeug : for password hashing
  - uuid : for generating unique names for uploaded files
  - os : to interact file path and environment
  - datetime : for deadlines, timezones and class times

- Database 
  - SQLite from SQLAlchemy ORM
- Frontend 
  - HTML : for creating templates
  - Jinja - to dynamically sent data to HTML
  - CSS+Bootstrap - for responsive and elegant design
  - Docker : to run file in container
     - Dockerfile: defines environment
     - requirements.txt: to install all python requirements inside

inside terminal type: docker build -t edulink and after building is finished type: docker run -p 5000:5000 edulink and you can run the website locally.

future updated
 -upload more than 1 file
 -create folders for uploading files
 -add class background pictures
 -sort materials by date or name
 -students full interface
 -divide routes into different files
 - add function to hide class, or show it at exact date
 - class can be conducted only once a week (no feature for adding different time)
Not solved edge cases:
- in curriculum, class time is not placed till end - only at the start. not duration
- when users, or classes are deleted, folder names are not renumbered. eg. there were instructor folders with ids: 1,2,3; if first one is deleted, 2 and 3 will stay. it won't be changed to 1 and 2, and new will be added as 4
- email and phone is not confirmed 
- there is no password confirmation or forgotten password
- not edge case but id should be string
- if written 2 oclock app doesnt identify it as 14:00 automatically
- when writing deadline, from month to year, cursor is not automatically moved 




How to run:
clone the repository

git clone https://github.com/AnnaMkervalishvili/EduLink.git
cd EduLink
docker build -t edulink .
docker run -p 5000:5000 edulink
 










