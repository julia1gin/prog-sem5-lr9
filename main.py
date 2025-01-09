import time
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import logic

logic.few_tests()

app = FastAPI()

get_token_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>Log in here!</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="login" autocomplete="off" placeholder="Логин"/>
            <input type="text" id="password" autocomplete="off" placeholder="Пароль"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            
            function sendMessage(event) {
                var login = document.getElementById("login")
                var password = document.getElementById("password")
                
                ws.send('{"login":"' + login.value + '","password":"'+password.value+'"}')
                login.value = ''
                password.value = ''
                event.preventDefault()
            }
            
            function CopyToClipboard(id)
            {
                var r = document.createRange();
                r.selectNode(document.getElementById(id));
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(r);
                document.execCommand('copy');
                window.getSelection().removeAllRanges();
            }
        </script>
        <a href="#" onclick="CopyToClipboard('messages');return false;">Click to copy!</a>
    </body>
</html>
"""

get_status_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>Получить статус кэшбека</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="token" autocomplete="off" placeholder="Введите токен"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws2 = new WebSocket("ws://localhost:8000/ws2");
            ws2.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('text')
                var content = document.createTextNode(event.data)
                


                   message.appendChild(content)
                   messages.appendChild(message)


                
            };
            function sendMessage(event) {
                var token = document.getElementById("token")

                ws2.send('{"token":"' + token.value + '"}')
                token.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

index_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>Привет мир!</h1>
        <h4>Для получения данных о уровнях кэшбеков необходимо выполнить несколько простых действий:</h4>
        <ol>
        <li>перейдите по ссылке  <a href="./get_token">Получить токен по логину и паролю</a>, введите логин и пароль существующего пользователя</li>
        <li>Получите токен и скопируйте его, используя кнопку-ссылку.</li>
        <li>Перейдите по ссылке <a href="./get_status">Узнать статус по токену</a></li>
        <li>Введите полученный токен и наслаждайтесь результатом!</li>
        </ol>

        
        <h4>Список предварительно зарегестрированных пользователей:</h4>
        
        <ul>
            <li>Логин: 'Vasya0j', Пароль: 'Password123'</li>
            <li>Логин:'Petya', Пароль: 'MySecretPassword'</li>
            <li>Логин:'Richguy', Пароль: 'qwerty258'</li>
            <li>Логин:'newGuy', Пароль: 'noonewilleverhackpasswordthatlong'</li>
        </ul>
        
       
        
    </body>
</html>
"""


@app.get("/get_token")
async def get():
    return HTMLResponse(get_token_html)

@app.get("/get_status")
async def get():
    return HTMLResponse(get_status_html)

@app.get("/")
async def get():
    return HTMLResponse(index_html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        jdata = json.loads(data)
        pas = jdata['password']
        log = jdata['login']
        str1 = f'["login":"{log}","password":"{pas}"]'
        code = signJWT(str1.replace('[','{').replace(']', '}'))
        await websocket.send_text(code['access_token'])


@app.websocket("/ws2")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        jdata = json.loads(data)
        token = jdata['token']

        try:
            jdata = json.loads(decodeJWT(token)['user_id'])
            person = logic.get_person(jdata['login'], jdata['password'])
            plan = logic.check_discount_lvl(person)
            print('frhbjkhhjb')
            ans = f'''[
            "Клиент":"{jdata['login']}",
            "Уровень кэшбека":"{plan.name}",
            "Процент кэшбека":{plan.percent}]
            "Следующий уровень:":"{plan.next}"]
            '''
            await websocket.send_text(ans.replace('[','{').replace(']','}'))

        except KeyError:
            print('error')
            await websocket.send_text('Пользователь не найден')




#########################

import jwt

secret = 'my_secret_password'
algorithm = 'HS256'

def signJWT(user_id: str) -> dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 900
    }
    token = jwt.encode(payload, secret, algorithm=algorithm)

    return {"access_token": token}

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, secret, algorithms=[algorithm])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}