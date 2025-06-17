from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import csv
import os
from flask import Flask
import base64
import numpy as np
import cv2
from model import predict_pcos_model_based
from symptom_detection import detect_symptoms_from_image

app = Flask(__name__)

@app.route('/')
def home():
    return "PCOS Subtype Predictor Running..."

latest_symptom_data = {
    "acne": "No",
    "fatigue": "No",
    "hair_loss": "No",
    "facial_hair": "No",
    "skin_texture": "Normal"
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    print(f"User logged in: {name}, Age: {age}, Gender: {gender}")
    return redirect(url_for('dashboard'))

@app.route('/manual')
def manual_prediction():
    return render_template('prediction.html')

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/about')
def about():
    return render_template('about.html')

def get_recommendations(pcos_type):
    normalized_type = pcos_type.strip().lower()
    mapping = {
        "hyperandrogenic pcos": "Hyperandrogenic PCOS",
        "insulin-resistant pcos": "Insulin-Resistant PCOS",
        "inflammatory pcos": "Inflammatory PCOS",
        "pill-induced pcos": "Pill-Induced PCOS",
    }
    key = mapping.get(normalized_type)
    if not key:
        return {
            "lifestyle": ["No recommendations found for this subtype."],
            "diet": ["Please check the subtype returned by the model."]
        }
    recommendations = {
        "Hyperandrogenic PCOS": {
            "lifestyle": ["Incorporate stress-reducing activities like yoga or meditation.",
                          "Maintain a consistent sleep schedule.",
                          "Limit exposure to endocrine disruptors in skincare and food."],
            "diet": ["Eat anti-inflammatory foods like berries, turmeric, and leafy greens.",
                     "Avoid dairy and processed sugars.",
                     "Consider spearmint tea to reduce androgen levels."]
        },
        "Insulin-Resistant PCOS": {
            "lifestyle": ["Include 30 minutes of moderate exercise daily.",
                          "Manage stress through journaling or breathwork.",
                          "Avoid long gaps between meals to stabilize glucose."],
            "diet": ["Focus on high-fiber, low-GI foods like oats, beans, and lentils.",
                     "Avoid refined carbs and sugary drinks.",
                     "Consider inositol supplements with medical guidance."]
        },
        "Inflammatory PCOS": {
            "lifestyle": ["Reduce toxin exposure (plastics, processed foods).",
                          "Get enough quality sleep each night.",
                          "Incorporate gentle movement like walking or stretching."],
            "diet": ["Go for anti-inflammatory foods: leafy greens, nuts, turmeric.",
                     "Limit red meat, alcohol, and dairy.",
                     "Use omega-3 rich foods like flaxseed and salmon."]
        },
        "Pill-Induced PCOS": {
            "lifestyle": ["Restore natural cycles with good sleep and reduced stress.",
                          "Avoid over-exercising which can delay cycle return.",
                          "Monitor symptoms and consult a gynecologist if needed."],
            "diet": ["Eat whole foods rich in B-vitamins and magnesium.",
                     "Support liver detox with leafy greens and cruciferous vegetables.",
                     "Limit caffeine and alcohol to balance hormones."]
        }
    }
    return recommendations[key]

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        auto_detect = request.form.get('autoDetect')
        if auto_detect == 'yes':
            age = 22
            weight = 55.0
            acne = "Yes"
            hair_loss = "No"
            irregular_period = "No"
            insulin = "Normal"
            fatigue = "Mild"
        else:
            age = int(request.form['age'])
            weight = float(request.form['weight'])
            acne = request.form['acne']
            hair_loss = request.form['hair_loss']
            irregular_period = request.form['irregular_period']
            insulin = request.form['insulin']
            fatigue = request.form['fatigue']

        # Prepare input dictionary for model
        input_dict = {
            "Menstrual Irregularities": irregular_period,
            "Weight Issues": "Overweight" if weight > 55 else "Normal",
            "Acne": acne,
            "Hirsutism (Excess Hair Growth)": "Unknown",
            "Hair Loss/Baldness": hair_loss,
            "Obesity Type": "Obese PCOS",
            "Sebum Production (Oily Skin/Scalp)": "Unknown",
            "Scalp Hair Loss": "Unknown",
            "Diet": "Junk/Fast food",
            "Antiseptic Pills Usage": "No",
            "Neck Pigmentation(Acanthosis Nigricans)": "No",
            "Age Group": "Young Adult" if age < 30 else "Adult",
            "Lifestyle": "Sedentary",
            "Stress Level": "High" if fatigue == "Severe" else "Moderate",
            "HRV": "Low",
            "Body Temperature": "Normal",
            "Food Habits": "Vegetarian"
        }

        # Predict using the model
        prediction = predict_pcos_model_based(input_dict)

        # Extract subtype from prediction (clean string if needed)
        subtype = prediction.replace("Predicted:", "").strip()

        # Get recommendations based on subtype
        tips = get_recommendations(subtype)

        # Log the prediction (optional)
        with open('prediction_logs.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                age, weight, acne, hair_loss, irregular_period,
                insulin, fatigue, subtype,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])

        # Pass both prediction and tips to result
        return render_template('result.html', prediction=subtype, tips=tips)

    return render_template('predict.html')


@app.route('/result')
def result():
    prediction = request.args.get('prediction', '')
    subtype = prediction.split('Predicted Subtype:')[-1].strip() if 'Predicted Subtype:' in prediction else prediction.strip()
    tips = get_recommendations(subtype)
    return render_template('result.html', prediction=subtype, tips=tips)

@app.route('/video', methods=['GET', 'POST'])
def video():
    if request.method == 'POST':
        if 'video_file' not in request.files or request.files['video_file'].filename == '':
            return render_template('video.html', message="No video file provided.")
        video_file = request.files['video_file']
        filepath = os.path.join('static', 'uploads', video_file.filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        video_file.save(filepath)
        message = f"Uploaded video '{video_file.filename}' received and saved. (Analysis coming soon!)"
        return render_template('video.html', message=message)
    return render_template('video.html')

@app.route('/analyze_frame', methods=['POST'])
def analyze_frame():
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    img_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    result = detect_symptoms_from_image(frame)
    return jsonify({'result': result})

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        file_path = 'contact_messages.csv'
        file_exists = os.path.isfile(file_path)
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Name', 'Email', 'Message', 'Timestamp'])
            writer.writerow([name, email, message, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        return render_template('contact.html', success=True)
    return render_template('contact.html')

@app.route('/submission')
def submission():
    return render_template('submission.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    return render_template('admin_login.html')


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


