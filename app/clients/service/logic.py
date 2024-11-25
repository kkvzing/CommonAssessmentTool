"""
Logic module for processing client data and making intervention predictions.
Handles data cleaning, model predictions, and intervention combinations analysis.
"""

# Standard library imports
import os
#import json
from itertools import product

# Third-party imports 
import pickle
import numpy as np

# Constants
COLUMN_INTERVENTIONS = [
    'Life Stabilization',
    'General Employment Assistance Services',
    'Retention Services',
    'Specialized Services',
    'Employment-Related Financial Supports for Job Seekers and Employers',
    'Employer Financial Supports',
    'Enhanced Referrals for Skills Development'
]

# Load model
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, 'model.pkl')
with open(MODEL_PATH, "rb") as model_file:
    MODEL = pickle.load(model_file)

def clean_input_data(input_data):
    """
    Clean and transform input data into model-compatible format.

    Args:
        input_data (dict): Raw input data from the client

    Returns:
        list: Cleaned and formatted data ready for model input
    """
    columns = [
        "age", "gender", "work_experience", "canada_workex", "dep_num",
        "canada_born", "citizen_status", "level_of_schooling", "fluent_english",
        "reading_english_scale", "speaking_english_scale", "writing_english_scale",
        "numeracy_scale", "computer_scale", "transportation_bool", "caregiver_bool",
        "housing", "income_source", "felony_bool", "attending_school",
        "currently_employed", "substance_use", "time_unemployed",
        "need_mental_health_support_bool"
    ]
    demographics = {key: input_data[key] for key in columns}
    output = []
    for column in columns:
        value = demographics.get(column, None)
        if isinstance(value, str):
            value = convert_text(value)  # Removed 'column' from here as it wasn't used
        output.append(value)
    return output

def convert_text(text_data: str):
    """
    Convert text answers from front end into numerical values.

    Args:
        text_data (str): Text data to convert

    Returns:
        int: Converted numerical value
    """
    categorical_mappings = [
        {
            "": 0, "true": 1, "false": 0, "no": 0, "yes": 1,
            "No": 0, "Yes": 1
        },
        {
            "Grade 0-8": 1, "Grade 9": 2, "Grade 10": 3, "Grade 11": 4,
            "Grade 12 or equivalent": 5, "OAC or Grade 13": 6,
            "Some college": 7, "Some university": 8, "Some apprenticeship": 9,
            "Certificate of Apprenticeship": 10, "Journeyperson": 11,
            "Certificate/Diploma": 12, "Bachelor's degree": 13,
            "Post graduate": 14
        },
        {
            "Renting-private": 1, "Renting-subsidized": 2,
            "Boarding or lodging": 3, "Homeowner": 4,
            "Living with family/friend": 5, "Institution": 6,
            "Temporary second residence": 7, "Band-owned home": 8,
            "Homeless or transient": 9, "Emergency hostel": 10
        },
        {
            "No Source of Income": 1, "Employment Insurance": 2,
            "Workplace Safety and Insurance Board": 3,
            "Ontario Works applied or receiving": 4,
            "Ontario Disability Support Program applied or receiving": 5,
            "Dependent of someone receiving OW or ODSP": 6, "Crown Ward": 7,
            "Employment": 8, "Self-Employment": 9, "Other (specify)": 10
        }
    ]
    for category in categorical_mappings:
        if text_data in category:
            return category[text_data]

    return int(text_data) if text_data.isnumeric() else text_data

def create_matrix(row_data):
    """
    Create matrix of all possible intervention combinations.

    Args:
        row_data (list): Base data row

    Returns:
        np.array: Matrix of all possible intervention combinations
    """
    data = [row_data.copy() for _ in range(128)]
    perms = intervention_permutations(7)
    return np.concatenate((np.array(data), np.array(perms)), axis=1)

def intervention_permutations(num):
    """
    Generate all possible intervention combinations.

    Args:
        num (int): Number of interventions

    Returns:
        np.array: Matrix of all possible combinations
    """
    return np.array(list(product([0, 1], repeat=num)))

def get_baseline_row(row_data):
    """
    Create baseline row with no interventions.

    Args:
        row_data (list): Input data row

    Returns:
        np.array: Baseline row with zeros for interventions
    """
    base_interventions = np.zeros(7)
    return np.concatenate((np.array(row_data), base_interventions))

def intervention_row_to_names(row_data):
    """
    Convert intervention row to list of intervention names.

    Args:
        row_data (np.array): Row of intervention indicators

    Returns:
        list: Names of active interventions
    """
    return [COLUMN_INTERVENTIONS[i] for i, value in enumerate(row_data) if value == 1]

def process_results(baseline_pred, results_matrix):
    """
    Process model results into structured output.

    Args:
        baseline_pred (float): Baseline prediction
        results_matrix (np.array): Matrix of results

    Returns:
        dict: Processed results with baseline and interventions
    """
    result_list = [
        (row[-1], intervention_row_to_names(row[:-1]))
        for row in results_matrix
    ]
    return {
        "baseline": baseline_pred[-1],
        "interventions": result_list
    }

def interpret_and_calculate(input_data):
    """
    Main function to process input data and generate intervention recommendations.

    Args:
        input_data (dict): Raw input data from client

    Returns:
        dict: Processed results with recommendations
    """
    raw_data = clean_input_data(input_data)
    baseline_row = get_baseline_row(raw_data).reshape(1, -1)
    intervention_rows = create_matrix(raw_data)
    baseline_prediction = MODEL.predict(baseline_row)
    intervention_predictions = MODEL.predict(intervention_rows).reshape(-1, 1)
    result_matrix = np.concatenate((intervention_rows, intervention_predictions), axis=1)
    result_order = result_matrix[:, -1].argsort()
    result_matrix = result_matrix[result_order]
    top_results = result_matrix[-3:, -8:]
    return process_results(baseline_prediction, top_results)

if __name__ == "__main__":
    test_data = {
        "age": "23", "gender": "1", "work_experience": "1",
        "canada_workex": "1", "dep_num": "0", "canada_born": "1",
        "citizen_status": "2", "level_of_schooling": "2",
        "fluent_english": "3", "reading_english_scale": "2",
        "speaking_english_scale": "2", "writing_english_scale": "3",
        "numeracy_scale": "2", "computer_scale": "3",
        "transportation_bool": "2", "caregiver_bool": "1",
        "housing": "1", "income_source": "5", "felony_bool": "1",
        "attending_school": "0", "currently_employed": "1",
        "substance_use": "1", "time_unemployed": "1",
        "need_mental_health_support_bool": "1"
    }
    results = interpret_and_calculate(test_data)
    print(results)
