from flask import Flask, request, jsonify
import requests
import json
import firebase_admin
from firebase_admin import credentials, db
import datetime

cred = credentials.Certificate(
    'appointment-e4152-firebase-adminsdk-u2enn-1b2a738620.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://appointment-e4152-default-rtdb.firebaseio.com/"
})
# ref = db.reference("/")
# ref.set({"Message":"Hello World"})

app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'


@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req['queryResult']['intent']['displayName']
    if intent_name == "question and answer":
        prompt = req['queryResult']['queryText']
        url = "https://chatgpt-gpt-3-5.p.rapidapi.com/ask"

        payload = {"query": f"{prompt}"}
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "e1ade27b09msh8d03b634f457a5bp1a3d14jsn2140c4678005",
            "X-RapidAPI-Host": "chatgpt-gpt-3-5.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        response = json.loads(response.text)
        # print(response['response'])
        message = str(response['response']) + \
            "\n You should fill form to test heart disease. For this write I want to fill form."
        dialogflow_response = {'fulfillmentMessages': [
            {
                'text': {
                    'text': [message]
                }
            }
        ]
        }
        # print(dialogflow_response)
        return jsonify(dialogflow_response)

    elif intent_name == "userDetails":
        name = req['queryResult']['parameters']['given-name']
        phoneNo = req['queryResult']['parameters']['phone-number']
        email = req['queryResult']['parameters']['email']
        outputContext = req['queryResult']
        # print(outputContext['outputContexts'][0])
        outputContext = outputContext['outputContexts'][0]
        appointment_date = outputContext['parameters']['date.original']
        appointment_time = outputContext['parameters']['time.original']

        firebase_response = {
            'name': name,
            'phone': phoneNo,
            'email': email,
            'date': appointment_date,
            'time': appointment_time,
        }
        ref = db.reference("appointment")
        # ref.set(firebase_response)
        ref.push(firebase_response)
        now = datetime.datetime.now()
        current_date = now.date()
        current_time = now.time()
        if appointment_date < current_date and appointment_time < current_time:
            return jsonify({'fulfillmentMessages': [
            {
                'text': {
                    'text': ["You should enter correct date and time"],
                }
            }
        ]
        })
        else:
            return jsonify({'fulfillmentMessages': [
            {
                'text': {
                    'text': ["Your appointment is scheduled"],
                }
            }
        ]
        })
        


app.run(host="0.0.0.0")
