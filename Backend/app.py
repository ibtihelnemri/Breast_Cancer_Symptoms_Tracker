from flask import Flask, render_template, request, jsonify
from db import save_symptom_to_firebase, fetch_symptoms_from_firebase
import openai
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load OpenAI API key from the environment
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load SerpApi API key
serpapi_key = os.getenv('SERPAPI_KEY')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    symptoms = fetch_symptoms_from_firebase()
    return render_template('index.html', symptoms=symptoms)


# Route to get the details of a specific symptom
@app.route('/get_symptom_details/<symptom_id>', methods=['GET'])
def get_symptom_details(symptom_id):
    """
    Fetch symptom details from Firebase using the symptom ID.
    """
    symptoms = fetch_symptoms_from_firebase()  # Fetch all symptoms
    symptom_data = symptoms.get(symptom_id)    # Get the specific symptom details

    if symptom_data:
        return jsonify(symptom_data)  # Return the symptom data as JSON
    else:
        return jsonify({"error": "Symptom not found"}), 404
    

@app.route('/predict', methods=['POST'])
def predict():
    # Get the symptoms entered by the user
    symptom_text = request.form['symptoms']

    # Check if the form data is received
    print(f"Received symptoms: {symptom_text}")
    
    # Analyze the symptoms using GPT-4 to assess risk
    risk_assessment = analyze_symptoms_with_gpt4(symptom_text)
    
    # Generate a title for the symptoms using GPT-4
    generated_title = generate_title_with_gpt4(symptom_text)
    
    # Save the symptom text, generated title, and risk assessment to Firebase
    save_symptom_to_firebase(symptom_text, generated_title, risk_assessment)

    # Check if the risk assesment is received
    print(f"risk assesment: {risk_assessment}")
    
    # Fetch updated symptoms to display history
    symptoms = fetch_symptoms_from_firebase()

    return render_template('index.html', symptoms=symptoms, result=risk_assessment)


# Route to display available appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():

    # Get country and city from the query parameters
    specialty = request.args.get('specialty')
    city = request.args.get('city')

    # Call the scraping function to get facility data
    display_results = scrape_doctor_appointments(specialty, city)

    # Pass the extracted data to the HTML template (index.html in this case)
    #return render_template('index.html', facilities=display_results)
    return jsonify(display_results)


# Function to interact with GPT-4 for symptom risk analysis
def analyze_symptoms_with_gpt4(symptoms_text):
    prompt = (
        f"Given the following description of symptoms: '{symptoms_text}', "
        "please assess whether the symptoms indicate a high or low risk for breast cancer. "
        "Provide your assessment gently, and offer reassurance where possible. "
        "Then, give some soft, supportive recommendations for next steps, "
        "with a focus on the importance of staying calm and taking action at a comfortable pace. "
        "Use bullet points and headings to structure your advice clearly. "
        "If appropriate, advise when it might be a good idea to check in with a healthcare provider, "
        "and include gentle reminders that many symptoms can have benign causes."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 model
            messages=[
                {"role": "system", "content": "You are a helpful, empathetic assistant that specializes in medical symptom analysis, offering gentle advice and support."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,  # Allow more space for recommendations
            n=1,
            stop=None,
            temperature=0.5
        )

        result = response['choices'][0]['message']['content'].strip()
        result = result.replace("\n", "<br>")
        return result
    except openai.error.OpenAIError as e:
        return "Sorry, I'm having trouble generating text right now."
    

# Function to interact with GPT-4 for generating a concise title for symptoms
def generate_title_with_gpt4(symptoms_text):
    prompt = (
        f"Given the following description of symptoms: '{symptoms_text}', "
        "please generate a concise title that accurately captures the main theme or topic of the symptoms."
    )
    try :
        response = openai.ChatCompletion.create(
        model="gpt-4",  # Use GPT-4 model
        messages=[
            {"role": "system", "content": "You are a helpful assistant that specializes in generating concise titles for medical symptoms."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=80,
        n=1,
        stop=None,
        temperature=0.5
    )

        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        return "Sorry, I'm having trouble generating title right now."
    

def scrape_doctor_appointments(specialty, city):

    url = "https://serpapi.com/search"

    params = {
        "q": f"{specialty} doctors in {city}",
        "location": city,
        "hl": "fr",  # Language
        "gl": "fr",  # Country
        "api_key": serpapi_key
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()

        # Initialize an empty list to store the appointment details
        appointments = []

        # Loop through local results to extract relevant appointment details
        for place in data.get('local_results', {}).get('places', [])[:5]:  # Get up to 5 results
            appointment = {
                'name': place.get('title', 'N/A'),
                'address': place.get('address', 'N/A'),
                'link': place['links'].get('website', '#')
            }
            appointments.append(appointment)

        return appointments
    else:
        print(f"Error: {response.status_code}")
    return []


if __name__ == '__main__':
    app.run(debug=True)