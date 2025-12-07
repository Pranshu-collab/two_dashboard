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
    try:
        data_post = request.get_json() if request.is_json else request.form
        rating = data_post.get("rating")
        review = data_post.get("review")
        if not rating or not review:
            return jsonify({"error": "Missing rating or review"}), 400
        summary, action = call_AI(review)
        submission = {
            "rating": rating,
            "review": review,
            "summary": summary,
            "suggested_action": action,
        }
        with open("submissions.json", "a") as f:
            f.write(json.dumps(submission) + "\n")
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/submissions")
def data():
    submissions = []
    try:
        with open("submissions.json", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    submissions.append(json.loads(line))
    except FileNotFoundError:
        submissions = []
    except Exception:
        submissions = []
    return jsonify(submissions)
    
def call_AI(review_text):
    api_key = os.getenv("GOOGLE_API_KEY_3")
    if not api_key:
        return ("Manual follow-up required.")
    genai.configure(api_key=api_key)
    prompt = f"""
    You are a customer review analyzer.
    Input review: "{review_text}"
    Return JSON ONLY:
    {{
        "summary": "short summary",
        "action": "recommended action to improve customer experience"
    }}
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        ai_data = json.loads(raw_text)

        summary = ai_data.get("summary", "No summary generated.")
        action = ai_data.get("action", "No action found.")

        return summary, action

    except Exception:
        return ("Could not analyze review due to AI error.",
                "Manual follow-up required.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)




