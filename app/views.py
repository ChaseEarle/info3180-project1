"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file contains the routes for your application.
"""
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.utils import secure_filename
import os
from models import db, Property
from app import app
from flask import Flask,render_template, request, redirect, url_for
app = Flask(__name__)


###
# Routing for your application.
###
@app.route('/properties/create', methods=['GET', 'POST'])
def add_property():
    form = PropertyForm()
    if form.validate_on_submit():
        new_property_id = get_new_property_id()
        photo_filename = save_property_photo(form.photo.data, new_property_id)
        new_property = Property(id=new_property_id, title=form.title.data, description=form.description.data, num_bedrooms=form.num_bedrooms.data, num_bathrooms=form.num_bathrooms.data, location=form.location.data, price=form.price.data, property_type=form.property_type.data, photo_filename=photo_filename)
        db.session.add(new_property)
        db.session.commit()
        flash('Property added successfully!')
        return redirect(url_for('list_properties'))
    return render_template('add_property.html', form=form)


@app.route('/properties')
def properties():
    properties = Property.query.all()
    return render_template('properties.html', properties=properties)


@app.route('/properties/<int:propertyid>')
def property_detail(propertyid):
    property = Property.query.get_or_404(propertyid)
    return render_template('property_detail.html', property=property)


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


###
# The functions below should be applicable to all Flask apps.
###

# Display Flask WTF errors as Flash messages
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

class PropertyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    bedrooms = IntegerField('No. of Bedrooms', validators=[DataRequired()])
    bathrooms = IntegerField('No. of Bathrooms', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    property_type = SelectField('Property Type', choices=[('house', 'House'), ('apartment', 'Apartment')], validators=[DataRequired()])
    photo = FileField('Photo')