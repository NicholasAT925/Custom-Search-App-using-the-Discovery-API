from flask import Flask, render_template, request
from markupsafe import escape
import os
import yaml
import vertexai
from typing import List

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

####################################################################################
# Set the DATA_STORE_ID and PROJECT_ID variables for your project
####################################################################################
LOCATION = "global"
DATA_STORE_ID = "cymbal-programming-data-store_1749436409296"
PROJECT_ID = "qwiklabs-gcp-04-98693275d574"

app = Flask(__name__)

# Helper function that reads from the config file. 
def get_config_value(config, section, key, default=None):
    """
    Retrieve a configuration value from a section with an optional default value.
    """
    try:
        return config[section][key]
    except:
        return default

# Open the config file (config.yaml)
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Read application variables from the config fle
TITLE = get_config_value(config, 'app', 'title', 'Ask Google')
SUBTITLE = get_config_value(config, 'app', 'subtitle', 'Your friendly Bot')

# The Home page route
@app.route("/", methods=['POST', 'GET'])
def main():
    responses = []

    # The user clicked on a link to the Home page
    # They haven't yet submitted the form
    if request.method == 'GET':
        search_query = ""

    # The user asked a question and submitted the form
    # The request.method would equal 'POST'
    else: 
        search_query = request.form['input']

        # Search the Data Storw passing in the user's question
        # You need to implement the search_data_store function. See below.
        response = search_data_store(PROJECT_ID, LOCATION, DATA_STORE_ID, search_query)

        # The Response needs formatted to be displayed in the HTML template
        # You need to implement the format_response function. See below
        responses = format_response(response)

        
    # Display the home page with the required variables set
    model = {"title": TITLE, "subtitle": SUBTITLE,
             "input": search_query, 
             "responses": responses}
    return render_template('index.html', model=model)

####################################################################################
#
# See the following URL for implementing this function
# https://cloud.google.com/generative-ai-app-builder/docs/preview-search-results#genappbuilder_search-python
#
####################################################################################
def search_data_store(
    project_id: str,
    location: str,
    data_store_id: str,
    search_query: str,
) -> List[discoveryengine.SearchResponse]:

    client = discoveryengine.SearchServiceClient()

    # Construct the full serving config path
    serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}/servingConfigs/default_search"

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=10,
    )

    results = client.search(request=request)

    # See the docs to implement this search function
    return list(results)


####################################################################################
#
# The discoveryengine.SearchResponse is Documented here:
# https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchResponse
#
# Hint 1: Return a collection of objects with the fields: title, snippet, and url
# Hint 2: To enumerate the results return in the response use the loop: for result in response.results
# Hint 3: In the loop, the following snippets will retrive the required data:
#    result.document.derived_struct_data["htmlTitle"]
#    result.document.derived_struct_data["snippets"][0]["htmlSnippet"]
#    result.document.derived_struct_data["formattedUrl"]
#    
####################################################################################
# def format_response(response):
#     results = []

#     # Implement a loop below to return a collection of 
#     # objects with title, snippet, and url properties
#     # some dummy code is shown below

#     title = results.document.derived_struct_data["htmlTitle"]
#     snippet = results.document.derived_struct_data["snippets"][0]["htmlSnippet"]
#     url = results.document.derived_struct_data["formattedUrl"]
    
#     element = {
#         "title": title,
#         "snippet": snippet,
#         "url": url
#     }
#     results.append(element)
#     return results

def format_response(response):
    results = []

    for result in response:
        try:
            doc_data = result.document.derived_struct_data

            title = doc_data.get("htmlTitle", "No Title")
            snippet = doc_data.get("snippets", [{}])[0].get("htmlSnippet", "No Snippet")
            url = doc_data.get("formattedUrl", "#")

            element = {
                "title": title,
                "snippet": snippet,
                "url": url
            }
            results.append(element)

        except Exception as e:
            # Optionally log or handle error
            continue

    return results

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
