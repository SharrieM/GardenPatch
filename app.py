#Imports necessary classes/modules
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

#Creates Flask App
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads/seed_images'
#Where the database to connect to is n n  bnn gbg/bb/
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
#Choose a secret key5 
app.config["SECRET_KEY"] = "GPKey"
#Initialize the database
db = SQLAlchemy()

#Set up the Login Manager
#This is needed so users can log in and out
login_manager = LoginManager()
login_manager.init_app(app)

#To store user information, a table needs to be created. 
#Create User class and make it a subclass of db.Model.
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    hemisphere = db.Column(db.String(20), nullable=False)
    seeds = db.relationship('Seed', backref='user', lazy=True)      #Relationship for Seed table
    plants = db.relationship('Plant', backref='user', lazy=True)

#Create Seed class, a subclass of db.Model
class Seed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    plant_type = db.Column(db.String(250), nullable=False)
    germinate_time = db.Column(db.String(250))
    planting_depth = db.Column(db.String(250))
    plant_spacing = db.Column(db.String(250))
    maturity_time = db.Column(db.String(250))
    sun_requirement = db.Column(db.String(250))
    when_to_plant = db.Column(db.String(250))
    image_filename = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  #User ID from Users table

#Create Plants class, a subclass of db.Model
class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plantName = db.Column(db.String(250), nullable=False)
    plantType = db.Column(db.String(250), nullable=False)
    plantDate = db.Column(db.Date, nullable=False)
    plantMaturity = db.Column(db.String(250))
    maturityDate = db.column(db.String(250), nullable=True)
    plantGermination = db.Column(db.String(250), nullable=True)
    germinationDate = db.Column(db.String(250), nullable=True)
    plantSunRequirement = db.Column(db.String(250))
    plantPlacement = db.Column(db.String(250))
    newSeedling = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   #User ID from Users table

#Initializes Flask-SQLAlchemy extension with flask App.
db.init_app(app)

#Then create the database table
with app.app_context():
    db.create_all()

#User loader callback, returns user object from id
@login_manager.user_loader
def loader_user(user_id) :
        return Users.query.get(user_id)

# Define the helper function to save image
def save_image(file):
    if file:
        filename = secure_filename(file.filename)

        # Ensure the target directory exists
        upload_folder = 'static/uploads/seed_images'
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print("File Path:", file_path)
        file.save(file_path)
        return filename
    return None


#Routes for the Web App
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/account/")
@login_required
def account():
    return render_template("account.html")

@app.route('/loginregister/')
def loginregister():        
    return render_template("loginregister.html")

# Registration form display
@app.route('/register', methods=["GET"])
def show_register_form():
    return render_template("loginregister.html")

# Registration route
@app.route('/register', methods=["POST"])
def register():
    if request.method == "POST":
        username = request.form.get("regUsername")
        password = request.form.get("regPassword")
        confirm_password = request.form.get("confirmPassword")
        hemisphere = request.form.get("hemisphere")

        # Check if password and confirm password match
        if password != confirm_password:
            return render_template("loginregister.html")

        # Check if the username is already taken
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            return render_template("loginregister.html")

        # Create a new user
        user = Users(username=username, password=password, hemisphere=hemisphere)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("home"))
    
# Login form display
@app.route('/login', methods=["GET"])
def show_login_form():
    return render_template("loginregister.html")
  
# Login route
@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("home"))

    return render_template("loginregister.html")

@app.route("/tasks/")
@login_required
def tasks():
    return render_template("tasks.html")

@app.route("/calendar/")
@login_required
def calendar():
    return render_template("calendar.html")

@app.route("/myPlants/")
@login_required
def myPlants():
    user_seeds = Seed.query.filter_by(user_id=current_user.id).all()
    return render_template("myPlants.html", user_seeds=user_seeds)

@app.route('/add_plant', methods=['POST'])
@login_required
def add_plant():
    #Get data from form
    addPlantName = request.form.get('seedlingPlantName')
    addPlantType = request.form.get('seedlingPlantType')
    addPlantDate = request.form.get('seedlingPlantDate')
    addPlantMaturity = request.form.get('plantMaturityTime')
    addPlantSun = request.form.get('seedlingSunRequirement')
    addPlantPlace = request.form.get('seedlingPlantPlace')
    addPlantDate = request.form.get('seedlingPlantDate')

    #Convert the date string to a datetime object
    plant_date = datetime.strptime(addPlantDate, '%Y-%m-%d').date()

    #Create newPlant from above
    newPlant = Plant (
        plantName=addPlantName,
        plantType=addPlantType,
        plantDate=plant_date,
        plantMaturity=addPlantMaturity,
        plantSunRequirement=addPlantSun,
        plantPlacement=addPlantPlace,
        newSeedling=1,
        user_id=current_user.id
    )
     # Add the new seed to the database
    db.session.add(newPlant)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()

    # Redirect to the my plants page
    return redirect(url_for('myPlants'))

@app.route("/seedlibrary/")
@login_required
def seedLibrary():
    user_seeds = Seed.query.filter_by(user_id=current_user.id).all()
    return render_template("seedLibrary.html", user_seeds=user_seeds)

# Route to reload the seed library content
@app.route('/reloadSeedLibrary')
@login_required
def reloadSeedLibrary():
    # Fetch seeds only for the logged-in user
    user_seeds = Seed.query.filter_by(user_id=current_user.id).all()

    # Render the seed library content as HTML
    seedLibraryhtml = render_template('seedLibraryContent.html', user_seeds=user_seeds)
    
    return seedLibraryhtml

# Route for adding seed form submission
@app.route('/add_seed', methods=['POST'])
@login_required
def add_seed():
    #Get data from form
    seed_name = request.form.get('addSeedName')
    plant_type = request.form.get('addSeedType')
    germinate_time = request.form.get('addSeedGermination')
    planting_depth = request.form.get('addSeedDepth')
    plant_spacing = request.form.get('addSeedSpacing')
    maturity_time = request.form.get('addSeedMaturity')
    sun_requirement = request.form.get('addSeedSun')
    when_to_plant = request.form.get('addSeedSeason')
    
    # Get the image file
    image_file = request.files.get('addSeedImage')

    # Debug print
    #print(f"Image File: {image_file}")

    # Save the image file
    image_filename = save_image(image_file)

    # Debug print
    #print(f"Image Filename: {image_filename}")

    # Create a new seed with the form data
    new_seed = Seed(
        name=seed_name,
        plant_type=plant_type,
        germinate_time=germinate_time,
        planting_depth=planting_depth,
        plant_spacing=plant_spacing,
        maturity_time=maturity_time,
        sun_requirement=sun_requirement,
        when_to_plant=when_to_plant,
        image_filename=image_filename,
        user_id=current_user.id
    )

    # Add the new seed to the database
    db.session.add(new_seed)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()

    # Redirect to the seed library page
    return redirect(url_for('seedLibrary'))
