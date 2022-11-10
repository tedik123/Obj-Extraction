import requests
import json


# better name please
class DataSender:

    def __init__(self, url):
        self.base_url = url
        # json format of our exercise data
        self.exercise_data = self.read_in_data()
        self.exercises_collection = "exercises"

    def read_in_data(self):
        with open('exercise_data.json', 'r') as file:
            data = file.read()
        return json.loads(data)

    def send_all_exercise_data(self):
        for name, data in self.exercise_data.items():
            # print(exercise["exercise_name"])
            # print(f"Sending request for exercise: {name}")
            body = {
                # note: name must be unique we don't want duplicate exercises
                "name": data["name"],
                "description": data["description"],
                "primary_muscles": data["primary_muscles"],
                "secondary_muscles": data["secondary_muscles"],
                "tertiary_muscles": data["tertiary_muscles"],
                "risked_areas": data["risked_areas"],
                "external_links": data["external_links"],
            }
            # print(f"Body is {body}")
            # need to send a json since that's what our database expects
            try:
                response = requests.post(self.base_url + self.exercises_collection, json=body)
                print(response)

            except requests.exceptions.RequestException as e:
                print("Data that failed was", name)
                print("Exception as", e)

    # this is for passing in SOME data, you must pass in the data yourself it's expected to be a dict
    def send_exercise_data(self, data: dict):
        for name, data in data.items():
            # print(f"Sending request for exercise: {name}")
            body = {
                "name": data["name"],
                "description": data["description"],
                "primary_muscles": data["primary_muscles"],
                "secondary_muscles": data["secondary_muscles"],
                "tertiary_muscles": data["tertiary_muscles"],
                "risked_areas": data["risked_areas"],
                "external_links": data["external_links"],
            }
            # print(f"Body is {body}")
            # need to send a json since that's what our database expects
            try:
                response = requests.post(self.base_url + self.exercises_collection, json=body)
                print(response)
            except requests.exceptions.RequestException as e:
                print("Data that failed was", name)
                print("Exception as", e)

    # gets all exercises from the database
    def get_all_exercises(self):
        # requests.get(url, data=body)
        response = requests.get(self.base_url + self.exercises_collection)
        print("Received response", response.text)


if __name__ == "__main__":
    base_url = "http://localhost:8081/"
    data_sender = DataSender(base_url)
    # data_sender.get_all_exercises()
    data_sender.send_all_exercise_data()
