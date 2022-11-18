import csv
import json


# https://www.geeksforgeeks.org/convert-csv-to-json-using-python/?id=discuss

def convert_csv_to_json():
    headers_list = []
    muscles_data = {}
    exercise_data = {}
    with open('exercise_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row_index, row_values in enumerate(reader):
            # I think here I need to define the templates and fill accordingly and as needed
            # and use the formatter function to figure out how to place things...I think dunno
            # 0 is the exercise name
            exercise_name = row_values[0]
            exercise = exercise_template(exercise_name)
            # print(exercise)
            for col_index, col_value in enumerate(row_values):
                # it's a header
                if row_index == 0:
                    # these headers will be indexed by the column row so that we know what column name we're on
                    headers_list.append(col_value)
                else:
                    muscles_data = formatter(exercise, exercise_name, muscles_data, headers_list, row_index, col_index,
                                             col_value)
                    exercise_data = exercise_data | exercise
        # print(exercise_data)
        print(muscles_data)
        # print(headers_list)
    write_to_files(muscles_data, exercise_data)
    print("Finished.")


def write_to_files(muscles_data, exercise_data):
    with open("exercise_data.json", "w") as outfile:
        json.dump(exercise_data, outfile)
    with open("muscles_data.json", "w") as outfile:
        json.dump(muscles_data, outfile)


# FIXME muscles data shouldn't be returned like this i don't think it's gross
# because it's inconsistent with how exercise works
def formatter(exercise, exercise_name, muscles_data, headers_list, row_index, col_index, col_value: str):
    # print(headers_list, row_index, col_index, col_value)
    header = headers_list[col_index]
    # make it capitalized to start as well
    exercise_contents = exercise[exercise_name.title()]

    # print(header)
    match header:
        case "Exercise Name":
            # we've already assigned this
            pass
        case "Primary Muscles":
            primary_muscles = convert_csv_string_to_array(col_value)
            exercise_contents["primary_muscles"] += primary_muscles
            for muscle_name in primary_muscles:
                muscles_data = add_data_to_muscles(muscles_data, exercise_name, muscle_name, "primary_exercises")
        case "Secondary Muscles":
            secondary_muscles = convert_csv_string_to_array(col_value)
            exercise_contents["secondary_muscles"] += secondary_muscles
            for muscle_name in secondary_muscles:
                muscles_data = add_data_to_muscles(muscles_data, exercise_name, muscle_name, "secondary_exercises")
        case "Tertiary Muscles":
            tertiary_muscles = convert_csv_string_to_array(col_value)
            exercise_contents["tertiary_muscles"] += tertiary_muscles
            for muscle_name in tertiary_muscles:
                muscles_data = add_data_to_muscles(muscles_data, exercise_name, muscle_name, "tertiary_exercises")
        case "Risked Areas":
            risked_areas = convert_csv_string_to_array(col_value)
            exercise_contents["risked_areas"] += risked_areas
        case "External Links":
            links = convert_csv_string_to_array(col_value)
            exercise_contents["external_links"] = links
        case "Description":
            exercise_contents["description"] = col_value
        # default case
        case _:
            print("oh oh", header)
            raise ValueError
    return muscles_data


# converts a string to an array of values
def convert_csv_string_to_array(col_value: str):
    # makes each word start with a capital letter
    col_value = col_value.title()
    string_array = col_value.split(",")
    string_array = [primary.strip() for primary in string_array]
    # print(string_array)
    return string_array


def add_data_to_muscles(muscles_data: dict, exercise_name: str, muscle_name: str, tier: str):
    if muscle_name == "" or muscle_name is None:
        return muscles_data
    # create the new muscles template and give new information
    if muscle_name not in muscles_data:
        muscles_data = muscles_data | muscle_template(muscle_name)
    current_muscle_data = muscles_data[muscle_name]
    current_muscle_data[tier].append(exercise_name)
    # unnecessary but idk seems nice
    current_muscle_data[tier].sort()
    return muscles_data


# these are a bit repetitive, but I think more optimal for seaching
def exercise_template(exercise_name):
    return {
        exercise_name: {
            "name": exercise_name,
            "description": "",
            "primary_muscles": [],
            "secondary_muscles": [],
            "tertiary_muscles": [],
            "risked_areas": [],
            "external_links": []
        }
    }


def muscle_template(muscle_name):
    return {
        muscle_name: {
            "muscle": muscle_name,
            "primary_exercises": [],
            "secondary_exercises": [],
            "tertiary_exercises": [],
        }
    }


# I think we want the muscle name as the key then another dict with the key of exercises

if __name__ == "__main__":
    convert_csv_to_json()
