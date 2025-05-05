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
  - Jinja - to dynamicly sent data to HTML
  - CSS+Bootstrap - for responsive and elegant design
  - Docker : to run file in containter
     - Dockerfile: defines environment
     - requirements.txt: to install all pythong requirements inside

inside terminal type: docker build -t edulink and after building is finished type: docker run -p 5000:5000 edulink and you can run the website locally.

Demo Credentials: 
 - Email: admin@gmail.com - Password: admin

Demo Credentials:
 -upload more than 1 file
 -create folders for uploading files
 -add class background pictures
 -sort materials by date or name
 -students full interface
 -divide routes into different files
 





