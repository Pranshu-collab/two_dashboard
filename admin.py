from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

@app.route("/")
def user_dashboard():
    return render_template("user.html")

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
        summary,action
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

def call_AI(prompt):
    # call openai or gemini
    pass

if __name__ == "__main__":
    app.run(debug=True)
