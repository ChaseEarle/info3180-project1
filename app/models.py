from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, FileField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from . import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key' # Change this to a stronger secret key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/database_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    photo = db.Column(db.String(255), nullable=False)


class PropertyForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    type = SelectField('Type', choices=[('House', 'House'), ('Apartment', 'Apartment')], validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    bedrooms = IntegerField('Number of Bedrooms', validators=[InputRequired()])
    bathrooms = IntegerField('Number of Bathrooms', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    price = StringField('Price', validators=[InputRequired()])
    photo = FileField('Photo', validators=[InputRequired()])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/properties/create', methods=['GET', 'POST'])
def create_property():
    form = PropertyForm()
    if request.method == 'POST' and form.validate():
        property = Property(title=form.title.data, type=form.type.data, description=form.description.data,
                            bedrooms=form.bedrooms.data, bathrooms=form.bathrooms.data, location=form.location.data,
                            price=form.price.data)
        photo = form.photo.data
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(app.config['UPLOAD_FOLDER'] + '/' + filename)
            property.photo = filename
        db.session.add(property)
        db.session.commit()
        flash('Property was successfully added.', 'success')
        return redirect(url_for('list_properties'))
    return render_template('create_property.html', form=form)


@app.route('/properties')
def list_properties():
    properties = Property.query.all()
    return render_template('list_properties.html', properties=properties)


@app.route('/properties/<int:property_id>')
def view_property(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('view_property.html', property=property)


if __name__ == '__main__':
    app.run(debug=True)

