from flask import Flask, render_template, request, jsonify
import json
import os
import google.generativeai as genai

app = Flask(__name__)

@app.route("/")
def user_dashboard():
    return render_template("user_file.html")

@app.route("/admin")
def admin():
    return render_template("index_dash.html")

@app.route("/submit", methods=["POST"])
def submit():
    if request.is_json:
        data_post = request.get_json()
    else:
        data_post=request.form
    rating=data_post.get("rating")
    review=data_post.get("review")
    
    if rating is None or review is None:
        return jsonify({"error":"Missing rating or review"}),400
    summary,action=call_AI(review)
    submission={
        "rating":rating,
        "review":review,
        "summary":summary,
        "suggested_action":action
    }
    with open("submissions.json","a") as f:
        f.write(json.dumps(submission) + "\n")
    return jsonify({
        "Success":True
    }),200
    #
    # extract rating + review
    # call AI
    # store in submissions.json
    # return summary + actions
@app.route("/data")
def data():
    submissions=[]
    try:
      with open("submissions.json","r") as f:
        for line in f:
           submissions.append(json.loads(line.strip()))
    except FileNotFoundError:
        submissions=[]    
    return jsonify(submissions)
    # read submissions.json and return

def call_AI(review_text):
    # call openai or gemini
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt=f"""
    You are a review i.e. customer feedback analyser. 
    Input review: "{review_text}"
    Return JSON only in this format:
    {{
        "summary": "a short summary",
        "action":"suggested action to take to improve the customer feedback "
    }} 
    """
    model=genai.GenerativeModel("gemini-2.0-flash")
    response=model.generate_content(prompt)
    try:
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        ai_data = json.loads(raw_text)
        summary=ai_data.get("summary")
        action=ai_data.get("action")
    except:
        summary="Could not analyse review"
        action=["Manual follow_up required"]
    return summary,action

if __name__ == "__main__":
    app.run(debug=True)
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)


