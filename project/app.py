from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # 啟用 CORS

# 設定 API Key(使用環境變數)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 初始化 Gemini 模型
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/api/gpt', methods=['POST'])
def gpt_response():
    data = request.json
    prompt = data.get('prompt', '')
    role = data.get('role', '一般人')  # 預設為一般人

    if not prompt:
        return jsonify({'reply': '請提供問題！'}), 400

    # 根據身份定義不同的提示詞
    role_prompts = {
        "國小低年級": f"請用國小低年級都看得懂的回答：{prompt}",
        "國小中年級": f"請用國小中年級都看得懂的回答：{prompt}",
        "國小高年級": f"請用國小高年級都看得懂的回答：{prompt}",
        "國中生": f"請用適合國中程度的方式回答：{prompt}",
        "高中生": f"請用適合高中程度的方式回答：{prompt}",
        "一般人": f"一般的回答：{prompt}"
    }

    # 根據用戶身份來調整 prompt
    final_prompt = role_prompts.get(role, prompt)

    try:
        # 使用 Gemini API 發送請求
        response = model.generate_content(final_prompt)
        
        # 返回生成的回應
        reply = response.text
        
        return jsonify({'reply': reply})
    
    except Exception as e:
        return jsonify({'reply': f'伺服器錯誤：{str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
