#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database

# app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#print(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.String(200))

    show = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.String(200))

    show = db.relationship('Show', backref='artist', lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id))
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id))


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  '''
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  '''
  try:
    results = Venue.query.outerjoin(Show, Venue.id == Show.venue_id).order_by(Venue.state, Venue.city).all()
  except:
    abort(500)

  formatted_result = []
  empty = False
  if results:
    iter_results = iter(results)
    rec = next(iter_results)
    now = datetime.datetime.now()
    while not empty:
      city = rec.city
      state = rec.state
      tmp = {
              "city": city,
              "state": state,
              "venues": []
      }
      while empty == False and city == rec.city and state == rec.state:
        upcoming_show = 0
        for show in rec.show:
          if show.artist:
            if show.start_time > now:
              upcoming_show = upcoming_show + 1
        tmp["venues"].append({
                              "id": rec.id,
                              "name": rec.name,
                              "num_upcoming_shows": upcoming_show
        })
        try:
          rec = next(iter_results)
        except:
          empty = True

      formatted_result.append(tmp)

  data = formatted_result
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  '''
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  '''

  search_term = request.form['search_term']
  formatted_result = {
        'count': 0,
        'data': []
  }

  if search_term and not search_term.isspace():
    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).outerjoin(Show, Venue.id == Show.venue_id).all()
    formatted_result = {
          'count': len(results),
          'data': []
    }
    now = datetime.datetime.now()
    for venue in results:
      upcoming_show = 0
      for show in venue.show:
        if show.artist:
          if show.start_time > now:
            upcoming_show = upcoming_show + 1
      formatted_result['data'].append({
                                      'id': venue.id,
                                      'name': venue.name,
                                      'num_upcoming_shows': upcoming_show})
  response = formatted_result
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  '''
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  '''

  # Raise error if no venue_id
  try:
    result = Venue.query.filter(Venue.id == venue_id).outerjoin(Show, Show.venue_id == Venue.id).all()
  except:
    abort(500)
  
  if not result:
    abort(404)
  else:
    formatted_result = {
              'id': result[0].id,
              'name': result[0].name,
              'genres': result[0].genres.split(','),
              'address': result[0].address,
              'city': result[0].city,
              'state': result[0].state,
              'phone': result[0].phone,
              'website': result[0].website,
              'facebook_link': result[0].facebook_link,
              'seeking_talent': result[0].seeking_talent,
              'seeking_description': result[0].seeking_description,
              'image_link': result[0].image_link,
              'past_shows': [],
              'upcoming_shows': [],
              'past_shows_count': 0,
              'upcoming_shows_count': 0
    }
    for show in result[0].show:
      if show.artist:
        now = datetime.datetime.now()
        if show.start_time <= now:
          formatted_result['past_shows'].append({
                                'artist_id': show.artist.id,
                                'artist_name': show.artist.name,
                                'artist_image_link': show.artist.image_link,
                                'start_time': str(show.start_time)
          })
        else:
          formatted_result['upcoming_shows'].append({
                                'artist_id': show.artist.id,
                                'artist_name': show.artist.name,
                                'artist_image_link': show.artist.image_link,
                                'start_time': str(show.start_time)
          })
    formatted_result['past_shows_count'] = len(formatted_result['past_shows'])
    formatted_result['upcoming_shows_count'] = len(formatted_result['upcoming_shows'])

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  data = formatted_result
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']

  try:
    venue = Venue(name = name,
                  city = city,
                  state = state,
                  address = address,
                  phone = phone,
                  genres = ','.join(genres),
                  facebook_link = facebook_link)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.filter(Venue.id == venue_id).all()
  except:
    abort(500)
  
  if venue:
    try:
      name = venue[0].name
      print(name)
      db.session.delete(venue[0])
      db.session.commit()
    except:
      abort(500)
  else:
    abort(404)

  #return None
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  '''
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  '''
  try:
    results = Artist.query.all()
  except:
    abort(500)

  formatted_result = []
  for artist in results:
    formatted_result.append({'id': artist.id, 'name': artist.name})
  data = formatted_result
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  '''
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  '''
  search_term = request.form['search_term']
  formatted_result = {
        'count': 0,
        'data': []
  }
  if search_term and not search_term.isspace():
    results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).outerjoin(Show, Artist.id == Show.artist_id).all()
    formatted_result = {
          'count': len(results),
          'data': []
    }
    now = datetime.datetime.now()
    for artist in results:
      upcoming_show = 0
      for show in artist.show:
        if show.venue:
          if show.start_time > now:
            upcoming_show = upcoming_show + 1
      formatted_result['data'].append({
                                      'id': artist.id,
                                      'name': artist.name,
                                      'num_upcoming_shows': upcoming_show})
  response = formatted_result
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  '''
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  '''

  try:
    result = Artist.query.filter(Artist.id == artist_id).outerjoin(Show, Show.artist_id == Artist.id).all()
  except:
    abort(500)

  if not result:
    abort(404)
  else:
    formatted_result = {
              'id': result[0].id,
              'name': result[0].name,
              'genres': result[0].genres.split(','),
              'city': result[0].city,
              'state': result[0].state,
              'phone': result[0].phone,
              'website': result[0].website,
              'facebook_link': result[0].facebook_link,
              'seeking_venue': result[0].seeking_venue,
              'seeking_description': result[0].seeking_description,
              'image_link': result[0].image_link,
              'past_shows': [],
              'upcoming_shows': [],
              'past_shows_count': 0,
              'upcoming_shows_count': 0
    }
    for show in result[0].show:
      if show.venue:
        now = datetime.datetime.now()
        if show.start_time <= now:
          formatted_result['past_shows'].append({
                                'venue_id': show.venue.id,
                                'venue_name': show.venue.name,
                                'venue_image_link': show.venue.image_link,
                                'start_time': str(show.start_time)
          })
        else:
          formatted_result['upcoming_shows'].append({
                                'venue_id': show.venue.id,
                                'venue_name': show.venue.name,
                                'venue_image_link': show.venue.image_link,
                                'start_time': str(show.start_time)
          })
    formatted_result['past_shows_count'] = len(formatted_result['past_shows'])
    formatted_result['upcoming_shows_count'] = len(formatted_result['upcoming_shows'])

  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  data = formatted_result
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  '''
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  '''
  # TODO: populate form with fields from artist with ID <artist_id>

  try:
    artist = Artist.query.filter(Artist.id == artist_id).all()[0]
  except:
    abort(500)

  if artist:
    formatted_result = {
          'id': artist.id,
          'name': artist.name,
          'genres': artist.genres.split(','),
          'city': artist.city,
          'state': artist.state,
          'phone': artist.phone,
          'website': artist.website,
          'facebook_link': artist.facebook_link,
          'seeking_venue': artist.seeking_venue, 
          'seeking_description': artist.seeking_description,
          'image_link': artist.image_link
    }
  else:
    abort(404)
  form = ArtistForm(name=formatted_result['name'], 
                    city=formatted_result['city'],
                    state=formatted_result['state'], 
                    phone=formatted_result['phone'],
                    genres=formatted_result['genres'],
                    facebook_link=formatted_result['facebook_link']
                    )
  return render_template('forms/edit_artist.html', form=form, artist=formatted_result)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:
    artist = Artist.query.filter(Artist.id == artist_id).all()[0]
  except:
    abort(500)

  if artist:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = request.form['facebook_link']
  else:
    abort(404)

  try:
    db.session.commit()
  except:
    abort(500)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>

  try:
    venue = Venue.query.filter(Venue.id == venue_id).all()[0]
  except:
    abort(500)

  if venue:
    formatted_result = {
          'id': venue.id,
          'name': venue.name,
          'genres': venue.genres.split(','),
          'address': venue.address,
          'city': venue.city,
          'state': venue.state,
          'phone': venue.phone,
          'website': venue.website,
          'facebook_link': venue.facebook_link,
          'seeking_talent': venue.seeking_talent,
          'seeking_description': venue.seeking_description,
          'image_link': venue.image_link
    }
  else:
    abort(404)

  form = VenueForm(name=formatted_result['name'],
                   city=formatted_result['city'],
                   state=formatted_result['state'],
                   address=formatted_result['address'],
                   phone=formatted_result['phone'],
                   genres=formatted_result['genres'],
                   facebook_link=formatted_result['facebook_link']
                   )

  return render_template('forms/edit_venue.html', form=form, venue=formatted_result)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    venue = Venue.query.filter(Venue.id == venue_id).all()[0]
  except:
    abort(500)

  if venue:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.facebook_link = request.form['facebook_link']
  else:
    abort(404)
  
  try:
    db.session.commit()
  except:
    abort(500)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link'] 

  try:
    artist = Artist(name = name,
                    city = city,
                    state = state,
                    phone = phone,
                    genres = ','.join(genres),
                    facebook_link = facebook_link)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + name + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]

  try:
    shows = Show.query.all()
  except:
    abort(500)

  formatted_result = []
  if shows:
    for show in shows:
      if show.venue_id and show.artist_id:
        formatted_result.append({
                  'venue_id': show.venue_id,
                  'venue_name': show.venue.name,
                  'artist_id': show.artist_id,
                  'artist_name': show.artist.name,
                  'artist_image_link': show.artist.image_link,
                  'start_time': str(show.start_time)
        })      
  #print(formatted_result)
  #input('stop')
  return render_template('pages/shows.html', shows=formatted_result)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  #input('stop')
  #print(f'{artist_id} {venue_id} {start_time}')

  try:
    artist_id = int(artist_id)
    venue_id = int(venue_id)
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
  except:
    flash('An error occurred. Show could not be listed') 

  try:
    artist = Artist.query.filter(Artist.id == artist_id).all()
  except:
    abort(500)

  try:
    venue = Venue.query.filter(Venue.id == venue_id).all()
  except:
    abort(500)

  if artist and venue:
    try:
      show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      flash('An error occurred. Show could not be listed') 
  else:
    abort(404)

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    port = int(os.environ.get('PORT', 7002))
    app.run(host='0.0.0.0', port=port)
