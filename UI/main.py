from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput 
from kivy.uix.button import Button
import requests

class SymptomApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        self.symptom_input = TextInput(hint_text="Please, describe your symptoms including all the details", multiline=True)
        layout.add_widget(self.symptom_input)

        submit_button = Button(text="Submit", on_press=self.submit_symptoms)
        layout.add_widget(submit_button)

        return layout
    
    def submit_symptoms(self, instance):
        symptoms = self.symptom_input.text

        # Send free text symptom to backend API (Flask)
        response = requests.post('http://localhost:5000/predict', json={"symptoms": symptoms})
        prediction = response.json().get('risk', 'No risk data')
        
        # Display prediction to user
        print(f"AI Response: {prediction}")

if __name__ == '__main__':
    SymptomApp().run()