#!/usr/bin/python3
"""
View for Place objects that handles all default RESTful API actions.
"""

from flask import jsonify, abort, request
from models import storage
from models.place import Place
from models.city import City
from models.state import State
from models.amenity import Amenity
from models.user import User
from api.v1.views import app_views


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places_by_city(city_id):
    """Retrieves the list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a Place"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if not request.json:
        abort(400, description="Not a JSON")
    if 'user_id' not in request.json:
        abort(400, description="Missing user_id")
    if 'name' not in request.json:
        abort(400, description="Missing name")
    user_id = request.json['user_id']
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    data = request.get_json()
    data['city_id'] = city_id
    place = Place(**data)
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """Updates a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.json:
        abort(400, description="Not a JSON")
    data = request.get_json()
    ignore_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """Retrieves all Place objects depending on the JSON in the request body"""
    if not request.json:
        abort(400, description="Not a JSON")
    search_criteria = request.get_json()
    places = set()

    if not search_criteria or (not search_criteria.get('states') and
                               not search_criteria.get('cities') and
                               not search_criteria.get('amenities')):
        places = set(storage.all(Place).values())
    else:
        if 'states' in search_criteria and search_criteria['states']:
            for state_id in search_criteria['states']:
                state = storage.get(State, state_id)
                if state:
                    for city in state.cities:
                        places.update(city.places)
        if 'cities' in search_criteria and search_criteria['cities']:
            for city_id in search_criteria['cities']:
                city = storage.get(City, city_id)
                if city:
                    places.update(city.places)

    if 'amenities' in search_criteria and search_criteria['amenities']:
        amenities = [storage.get(Amenity, amenity_id)
                     for amenity_id in search_criteria['amenities']]
        amenities = [amenity for amenity in amenities if amenity is not None]
        places = {place for place in places
                  if all(amenity in place.amenities for amenity in amenities)}

    return jsonify([place.to_dict() for place in places])
