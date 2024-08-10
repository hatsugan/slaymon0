from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
import logging
import ast

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Utility function to parse list from string
def parse_list_from_string(list_str):
    try:
        return ast.literal_eval(list_str)
    except (ValueError, SyntaxError):
        return list_str  # In case the list_str isn't a valid list

# Function to load slays from CSV into a dictionary
def load_slays_dict(file_name):
    with open(file_name, "r") as f:
        reader = csv.DictReader(f)
        dictionary = {}
        for row in reader:
            # Ensure these are lists, not strings
            row['species_moves'] = parse_list_from_string(row['species_moves'])
            row['species_traits'] = parse_list_from_string(row['species_traits'])

            # Convert other numerical fields to integers or floats if necessary
            row['biomass'] = float(row['biomass'])
            row['body_strength'] = int(row['body_strength'])
            row['body_durability'] = int(row['body_durability'])
            row['body_speed'] = int(row['body_speed'])

            dictionary[row['name']] = row
    logger.debug(f"Final Slays Dictionary: {dictionary}")  # Print the final dictionary

    dictionary = dict(sorted(dictionary.items(), key=lambda item: item[1]['formal_name']))

    return dictionary

# Function to load traits from CSV into a dictionary
def load_traits_dict(file_name):
    with open(file_name, "r") as f:
        reader = csv.DictReader(f)
        dictionary = {}
        for row in reader:
            row['trait_tags'] = parse_list_from_string(row['trait_tags'])
            row['additional_moves'] = parse_list_from_string(row['additional_moves'])
            row['cost'] = int(row['cost'])
            row['strength_modifier'] = int(row['strength_modifier'])
            row['hardness_modifier'] = int(row['hardness_modifier'])
            row['durability_modifier'] = int(row['durability_modifier'])
            row['speed_modifier'] = float(row['speed_modifier'])
            dictionary[row['formal_name']] = row
    logger.debug(f"Final Slays Dictionary: {dictionary}")  # Print the final dictionary

    dictionary = dict(sorted(dictionary.items()))

    return dictionary

def slays_dict_calculated(slays_dictionary, traits_dictionary):
    for slay_name, slay in slays_dictionary.items():
        traits_cost = 0
        for trait in slay['species_traits']:
            trait_cost = traits_dictionary[trait]['cost']
            traits_cost += trait_cost
        slay['biomass_cost'] = slay['biomass'] + (traits_cost * slay['biomass'] / 20)
    return slays_dictionary

def reload_slaipedia():
    slays_dictionary = load_slays_dict("slaipedia/slays.csv")
    traits_dictionary = load_traits_dict("slaipedia/traits.csv")
    slays_dictionary = slays_dict_calculated(slays_dictionary, traits_dictionary)
    return slays_dictionary, traits_dictionary

# Route for the index page
@app.route('/')
def index():
    logger.debug('Index route hit')
    return render_template('slaipedia.html')

# Route to view traits
@app.route('/traits')
def traits_viewer():
    logger.debug('Traits route hit')
    return render_template('traits.html', traits=traits_dict)

# Route to view slays
@app.route('/slays')
def slays_viewer():
    logger.debug('Slays route hit')
    # Reload the slays and traits dictionaries
    slays_dict, traits_dict = reload_slaipedia()
    logger.debug(f"Slays Dictionary: {slays_dict}")
    return render_template('slays.html', slays_dict=slays_dict, traits_dict=traits_dict)

# Route to edit a specific slay
@app.route('/slay_editor/<slay_name>', methods=['GET', 'POST'])
def slay_editor(slay_name):
    slay = slays_dict.get(slay_name)
    traits = traits_dict

    if request.method == 'POST':
        # Update the slay's stats
        slay['biomass'] = float(request.form['biomass'])
        slay['body_strength'] = int(request.form['body_strength'])
        slay['body_durability'] = int(request.form['body_durability'])
        slay['body_speed'] = int(request.form['body_speed'])

        # Update the slay's traits
        selected_traits = request.form.getlist('selected_traits')
        slay['species_traits'] = selected_traits

        # Debugging information to verify form data
        logger.debug(f"Form data: {request.form}")
        logger.debug(f"Updated slay before saving: {slay}")

        # Save the updated slay
        save_slays_dict("slaipedia/slays.csv", slays_dict)

        return redirect(url_for('slays_viewer'))

    return render_template('slay_editor.html', slay=slay, all_traits=traits)


def save_slays_dict(file_name, dictionary):
    fieldnames = [
        'name', 'formal_name', 'species_moves', 'species_traits', 'biomass', 'body_strength',
        'body_durability', 'body_speed'
    ]

    with open(file_name, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for slay_name, slay in dictionary.items():
            slay_copy = slay.copy()
            slay_copy.pop('biomass_cost', None)  # Remove 'biomass_cost' if it exists

            # Ensure species_moves and species_traits are properly formatted
            if isinstance(slay_copy['species_moves'], list):
                slay_copy['species_moves'] = str(slay_copy['species_moves'])
            if isinstance(slay_copy['species_traits'], list):
                slay_copy['species_traits'] = str(slay_copy['species_traits'])

            logger.debug(f"Saving slay: {slay_name} with data: {slay_copy}")
            writer.writerow(slay_copy)


if __name__ == '__main__':
    slays_dict, traits_dict = reload_slaipedia()
    app.run(debug=True)
