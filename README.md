# VKinder - dating bot

### This bot can find a pair using the Vkontakte API according to the parameters you specified, such as gender, status, age, place of residence. 

** Before using pls rename a file "default_keys.py" to "keys.py" and put inside your personal VK token, your group VK token and DB info. 

** At first launch pls set {"rebuild_tables": true} in file "options.cfg". When this flag set tables in given DB will be dropped and recreated. All data in DB will be lost. After first launch this flag will return to false automatically. 


1. Bot uses 2 tokens (group token for chat conversations with clients, personal token for making search of users)
2. Bot can receive and remember some client's preferences (country, search history, lists of rated users) which stored in DB
3. Bot controlled by text commands or screen buttons. Bot shows prompts of acceptable commands 
4. Bot can mark VK users as liked, disliked or banned. Bot can show previously rated users
5. Bot and it's components have console logging and some unittests via moked server
6. Bot can speak almost simultaneously with any number of users. There will be delays in commands processing because bot works in single thread
7. Bot can understand commands synonyms, which can be extended
8. Bot supports timeout of client activity and close session if client is absent

Block diagram of main work flow:


DB diagram:


Screenshots:
