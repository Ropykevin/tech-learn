from flask import Flask, render_template, request, jsonify, flash, session, redirect, url_for, abort
import firebase_admin
from firebase_admin import credentials, auth
import requests
from flask_cors import CORS
from firebase_admin import firestore
from firebase_admin import credentials
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient
import json



app = Flask(__name__, template_folder='../templates')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# API base URLs
base_url_journeys = 'http://167.71.54.75:8084/'
base_url_company_user = 'http://167.71.54.75:8082/'
base_url_userprogress = 'http://167.71.54.75:8081/'

CORS(app) 



# @app.route('/')
# def index():
#     if current_user.is_authenticated:
#         return f'Hello, {current_user.name}!'
#     return 'You are not logged in.'


@app.route('/')
def index():
    try:
        response = requests.get(f'{base_url_journeys}/categories')
        response.raise_for_status()
        categories = response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        categories = []
    return render_template('client/index.html', categories=categories)


@app.route('/<int:category_id>/journeys')
def category_journeys(category_id):
    try:
        response = requests.get(
            f'{base_url_journeys}/categories/{category_id}/journeys')
        response.raise_for_status()
        journeys = response.json()
        print("alaa",journeys)

        response_cat = requests.get(f'{base_url_journeys}/categories')
        response_cat.raise_for_status()
        categories = response_cat.json()
        
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        journeys = []
        categories = []

    return render_template('client/courseTopics.html', journeys=journeys, categories=categories)


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


@app.route('/data', methods=['GET'])
def get_data():
    journey_id = request.args.get('journey_id', type=int)
    section_id = request.args.get('section_id', type=int)

    context = {
        'journey': None,
        'sections': None,
        'topics': None,
        'section': None,
        'all_categories': None,
        'category': None,
        'catIds': [],
        'CategoryTopic': [],
        'course': None
    }

    if journey_id is not None:
        journey_url = f'{base_url_journeys}/journeys/{journey_id}'
        journey = fetch_data(journey_url)
        context['journey'] = journey
        print(f"journey {context}")

        if section_id is not None:
            sections_url = f'{
                base_url_journeys}/journeys/{journey_id}/sections'
            sections = fetch_data(sections_url)
            context['sections'] = sections
            print(f"sections {context}")


        return render_template('client/courseTopics.html', **context)

    if section_id is not None:
        topics_url = f"{base_url_journeys}/sections/{section_id}/topics"
        section_url = f"{base_url_journeys}/sections/{section_id}"

        topics = fetch_data(topics_url)
        section = fetch_data(section_url)
        context['topics'] = topics
        context['section'] = section

        # You can also fetch all categories and course details if needed
        # Example: context['all_categories'] = fetch_data(f'{base_url_journeys}/categories')
        # Example: context['course'] = fetch_data(f'{base_url_journeys}/courses/{course_id}')

        return render_template('client/courseTopics.html', **context)

    return "No valid parameter"


@app.route('/journeys/<int:journey_id>', methods=['GET'])
def get_journey(journey_id):
    try:
        # Fetch journey details
        response = requests.get(f'{base_url_journeys}/journeys/{journey_id}')
        response.raise_for_status()
        journey = response.json()

        # Fetch sections for the journey
        section_response = requests.get(
            f'{base_url_journeys}/journeys/{journey_id}/sections')
        section_response.raise_for_status()
        sections = section_response.json()

        # Fetch topics for each section
        for section in sections:
            section_id = section["id"]
            topics_response = requests.get(
                f'{base_url_journeys}/sections/{section_id}/topics')
            topics_response.raise_for_status()
            section['topics'] = topics_response.json()
            topics = section['topics']

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        journey = {}
        sections = []

        section_id = section["id"]
        section_id = section["id"]
    return render_template('client/topicContent.html', journey=journey, sections=sections, section=section, section_id=section_id)

# @app.route('/journeys/<int:journey_id>/sections')
# def get_sections_by_journey_id(journey_id):
#     try:
#         response = requests.get(
#             f'{base_url_journeys}/journeys/{journey_id}/sections')
#         response.raise_for_status()
#         sections = response.json()

#         journey_response = requests.get(
#             f'{base_url_journeys}/journeys/{journey_id}')
#         journey_response.raise_for_status()
#         journey = journey_response.json()
#     except requests.RequestException as e:
#         print(f"An error occurred: {e}")
#         sections = []
#         journey = {}


#     return render_template('client/sections.html', sections=sections, journey=journey)

@app.route('/sections/<int:section_id>/topics/<int:topic_id>')
def topic_content(section_id, topic_id):
    try:
        # Fetch the current topic
        response = requests.get(
            f'{base_url_journeys}/sections/{section_id}/topics/{topic_id}')
        response.raise_for_status()
        content = response.json()
        # print("rada",content)
        section_response = requests.get(
            f'{base_url_journeys}/sections/{section_id}/topics')
        section_response.raise_for_status()
        topics = section_response.json()
        topic_index = next((i for i, t in enumerate(
            topics) if t['id'] == topic_id), -1)
        prev_topic = topics[topic_index - 1] if topic_index > 0 else None
        next_topic = topics[topic_index +
                            1] if topic_index < len(topics) - 1 else None

        return render_template('client/section_topics.html', topic=content, prev_topic=prev_topic, next_topic=next_topic, topics=topics)
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        abort(404)



@app.route('/sections/<int:section_id>/topics')
def get_topics_by_section_id(section_id):
    topics_api_url = f"{base_url_journeys}/sections/{section_id}/topics"
    response = requests.get(topics_api_url)
    topics = response.json()
    section_api_url = f"{base_url_journeys}/sections/{section_id}"
    section_response = requests.get(section_api_url)
    section = section_response.json()
    return render_template('client/section_topics.html', section=section, topics=topics)

@app.route('/sections/<int:section_id>/levels/<int:level_id>/topics')
def get_topics_by_level_id(section_id, level_id):
    try:
        api_url = f'{
            base_url_journeys}/sections/{section_id}/levels/{level_id}/topics'
        response = requests.get(api_url)
        response.raise_for_status()
        topics = response.json()

        level_response = requests.get(
            f'{base_url_journeys}/sections/{section_id}/levels/{level_id}')
        level_response.raise_for_status()
        level = level_response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        topics = []
        level = {}

    return render_template('client/section_topics.html', section_id=section_id, level=level, topics=topics)


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/sections/<int:section_id>/levels')
def get_levels_by_section_id(section_id):
    try:
        api_url = f'{base_url_journeys}/sections/{section_id}/levels'
        response = requests.get(api_url)
        response.raise_for_status()
        levels = response.json()

        section_response = requests.get(
            f'{base_url_journeys}/sections/{section_id}')
        section_response.raise_for_status()
        section = section_response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        levels = []
        section = {}

    return render_template('client/levels.html', levels=levels, section=section)
