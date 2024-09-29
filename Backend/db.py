from firebaseConfig import db

# Function to save symptoms to Firebase
def save_symptom_to_firebase(symptom, generated_title, risk_assessment):
    """
    Saves a user's symptom data, generated title, and risk assessment to Firebase Realtime Database with a timestamp.

    Args:
    - symptom_text (str): A description of the user's symptom in free text format.
    - generated_title (str): The generated title summarizing the user's symptoms.
    - risk_assessment (str): The risk assessment result based on the symptoms.
    """
    print(f"Attempting to save symptom: {symptom}")  # Print statement to verify input
    data = {
        "symptom": symptom,             # The free text symptom entered by the user
        "title": generated_title,            # Generated title from GPT-4
        "risk_assessment": risk_assessment,  # Risk assessment (e.g., High risk or Low risk)
    }
    db.child("symptoms").push(data)      # Push the data to Firebase Realtime Database
    print("Symptom saved successfully!")  # Print after saving successfully

# Function to fetch all symptoms data from Firebase
def fetch_symptoms_from_firebase():
    """
    Retrieves all symptom data from Firebase Realtime Database.

    Returns:
    - symptoms (dict): A dictionary of all stored symptom records, or an empty list if no records are found.
    """
    symptoms = db.child("symptoms").get()
    return symptoms.val() if symptoms.val() else []