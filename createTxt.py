import json

# Load JSON data from the file
with open('artist_data.json', 'r') as json_file:
    json_data = json_file.read()

# Remove all backslashes
cleaned_data = json_data.replace('\\', '')

# Write the cleaned data to a .txt file
with open('artist_data.txt', 'w') as txt_file:
    txt_file.write(cleaned_data)