from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import time
import traceback

from openai import OpenAI
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# OPENAI API Key初始化設定
# 舊寫法：openai.api_key = os.getenv('OPENAI_API_KEY')

# 2024/3/23 新寫法
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv('OPENAI_API_KEY')
)



def GPT_response(prompt):
    # 接收回應
    # 原版
    # response = openai.Completion.create(model="gpt-4-turbo-preview", prompt=text, temperature=0.5, max_tokens=500)
    
    # 2024/3/23 依照最新 API 使用方式改版 by Jerry
    # CB_teacher_prompt = "你是一位資深的軟體工程師，超過15年資歷，同時也是一位科技教育、程式設計的講師。請回答以下問題，但如果這個問題跟「科技」、「程式設計」無關，則直接回答：「不好意思，我只回答跟科技、程式設計有關的問題喔～」"
    CB_CS_prompt = "你是 CodingBar 的客戶服務機器人。在你回答問題之前，請先建立以下基本知識：\nCodingBar 是一間致力於將科技普及的教育科技公司，開發自己的線上雲端程式學習平台，全台灣共有超過 70 間學校使用，連續三年獲得 East Asia EdTech 150，是全台灣唯一的一家 STEAM 公司！過去更榮獲經濟部【新創事業獎】、【亞太資通訊聯盟大賽銀牌】、親子天下教育創新領袖、遠見未來教育台灣100等獎項。
2024 暑假，我們開設了一系列的營隊，給10~18歲的青少年，國小生以 Roblox 系列營隊為主，國中以上則教授 python/C++等程式語言：\n
Roblox 不只是一個遊戲平台，更重要的他也是一個遊戲開發平台。任何人可以在這個平台上面開發3D線上遊戲，並且給全世界的玩家玩，我們就是透過這樣的平台，讓孩子學習如何發揮創意、設計自己的線上虛擬世界，開發一款好玩的線上遊戲。藉由這個過程培養孩子創意思維、打下程式設計的基礎。而且這不是一次性的營隊課程而以，後續更有多個進階課程，讓孩子在循序漸進的學習中，建立邏輯思維、善用科技的能力，迎接 AI新時代。營隊內容和梯次如下：\n"+
"1.Roblox 曠野傳說\n屬於基礎 Level 1 的營隊，適合暑假後升5~8年級的學生，每天 09:00 ~ 17:00，共 5 個整天（含午餐）。台北暑假共有三梯：\n
A梯：7/1~7/5\n
B梯：7/8~7/12\n
C梯：7/29~8/2\n
地點都在古亭捷運站附近的「鷹展古亭教室」。詳細內容可以參考官網：https://codingbar.ai/tw/camp/rmcr/index.html\n
也可以參考 Youtube 影片：https://youtu.be/FKQQokH7MRM\n" +
"2. Roblox 幻夜狙擊手\n
屬於進階 Level 2 的營隊，適合暑假後升5~8年級而且上過 Level 1 的學生，每天 09:00 ~ 17:00，共 5 個整天（含午餐）。台北暑假共有三梯：\n
A梯：7/8~7/12\n
B梯：7/15~7/19\n
C梯：8/5~8/9\n
地點都在松江南京捷運站附近的「台灣文創教室」。詳細內容可以參考官網：https://codingbar.ai/tw/camp/rl1c/index.html" +
"如果學生對象是七年級以上，想學程式設計，我們有Python,C++兩種語言的課程，搭配實體教學、線上自學搭配每週一次的線上直播教學、實體共學（每人有自己的學習進度，現場有老師指導）、線上遠距直播教學四種學習模式。\n
如果想知道詳細的課程班表時間，請參考：https://codingbar.ai/tw/school/index.html。 如果有特別客製化的學習需要，可以聯絡我們的教學顧問來回答。" +

"請依以上基本資訊回覆客戶（家長或學生）問題，回答的方式盡可能簡短、講重點，以活潑、積極、具同理心的語氣來回覆，每次回覆控制在 100 個中文字以內，不需說太多的客套話，語氣要更接近真實人類的回覆。\n
如果遇到不知道如何回覆的問題，你可以說很抱歉，請客戶留下方便聯絡的時間和電話，我們會請真人客服人員來回覆他。\n 以下是客戶的問題：\n"
    prompt=CB_CS_prompt + "\n" + prompt
    response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}]
        )
    
    print(response)
    # 重組回應
    answer = response.choices[0].message.content
    return answer


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    try:
        GPT_answer = GPT_response(msg)
        print(GPT_answer)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
    except:
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage('現在 AI 回覆出現問題，請稍後再提問喔，不好意思！'))
        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
