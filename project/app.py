import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from openai import OpenAI
import requests

app = Flask(__name__)
CORS(app)

# API 金鑰
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROK_API_KEY = os.getenv('GROK_API_KEY')

# 初始化 Gemini 和 OpenAI 客戶端
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/ai', methods=['POST'])
def ai_response():
    data = request.json
    prompt = data.get('prompt', '')
    role = data.get('role', '一般人')
    model = data.get('model', 'gemini')

    if not prompt:
        return jsonify({'reply': '請提供問題！'}), 400

    # 角色提示詞
    role_prompts = {
    "國小生": f"你是一位親切的大哥哥/大姊姊，要用國小生聽得懂的話來解釋這件事，用簡單的句子，不要用太難的字。如果一定要用難字，要加上注音（像這樣：制度(ㄓˋ ㄉㄨˋ)）。請回答這個問題：{prompt}",
    "國中生": f"你在跟一位國中生解釋這件事，請用清楚、有條理的方式講解內容，也可以舉個簡單的例子幫助理解：{prompt}",
    "高中生": f"請用適合高中生的語氣和思考方式來回答，內容可以有點深度，邏輯要清楚，也可以加入自己的見解：{prompt}",
    "一般人": f"請用一般大眾都能理解的方式來說明，不用太學術，但要說得清楚、完整：{prompt}"
}

    final_prompt = role_prompts.get(role, prompt)

    try:
        if model == 'gemini':
            response = gemini_model.generate_content(final_prompt)
            reply = response.text

        elif model == 'chatgpt':
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一個有幫助的AI助理"},
                    {"role": "user", "content": final_prompt}
                ]
            )
            reply = response.choices[0].message.content

        elif model == 'grok':
            headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "grok-2",  # 根據官方更新模型名
                "messages": [{"role": "user", "content": final_prompt}],
                "temperature": 0.7
            }
            grok_response = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
            grok_response.raise_for_status()
            reply = grok_response.json()["choices"][0]["message"]["content"]

        else:
            reply = "❌ 未知的 AI 模型"

        return jsonify({'reply': reply})

    except requests.exceptions.RequestException as e:
        return jsonify({'reply': f'API 請求錯誤：{str(e)}'}), 500
    except Exception as e:
        return jsonify({'reply': f'伺服器錯誤：{str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)


