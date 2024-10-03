import mysql.connector
import json

# Connect to the MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='techtic',
    database='scrap'
)

cursor = connection.cursor(dictionary=True)
query = '''SELECT 
    JSON_OBJECT(
        'id', artist_data.id,
        'name', artist_data.title,
        'counry_artist_id', artist_data.counry_artist_id,
        'nationality', artist_data.nationality,
        'art_movement', artist_data.art_movement,
        'field', artist_data.field,
        'influenced_on', artist_data.influenced_on,
        'influenced_by', artist_data.influenced_by,
        'official_site', artist_data.official_site,
        'description', artist_data.description,
        'birth_date', artist_data.birth_date,
        'death_date', artist_data.death_date,
        'link', artist_data.link,
        'image_path', artist_data.image_path,
        'artworks', (
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'art_id', artworks.art_id,
                    'name', artworks.name,
                    'title', artworks.title,
                    'artist_name', artworks.artist_name,
                    'added_date', artworks.added_date,
                    'tags', artworks.tags,
                    'image_url', artworks.image_url
                )
            )
            FROM artworks
            WHERE artworks.artist_id = artist_data.id
        )
    ) AS artist_with_artworks
FROM artist_data;'''  
# Modify the query as per your requirement
cursor.execute(query)

# Fetch all rows from the query result
rows = cursor.fetchall()

# Convert the result into JSON format
json_data = json.dumps(rows, indent=4)

# Write the JSON data to a file
with open('artist_data.json', 'w') as file:
    file.write(json_data)

# Close the connection
cursor.close()
connection.close()

print("JSON data has been written to artist_data.json")
