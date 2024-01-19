#Imports necessary classes/modules
from operator import or_
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from sqlalchemy import null
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta

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
    seedType = db.Column(db.String(250), nullable=False)
    germinate_time = db.Column(db.Integer, nullable=False)
    planting_depth = db.Column(db.String(250))
    plant_spacing = db.Column(db.String(250))
    maturity_time = db.Column(db.Integer, nullable=False)
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
    plantMaturity = db.Column(db.Integer)
    maturityDate = db.Column(db.Date, nullable=False)
    plantGermination = db.Column(db.Integer)
    germinationDate = db.Column(db.Date, nullable=False)
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

#Function to retrieve details from Seed Library
def getSeedInfo(seedName):
    seed = Seed.query.filter_by(name=seedName).first()
    if seed:
        return {
            'maturity': seed.maturity_time,
            'germination': seed.germinate_time,
            'sunRequirement': seed.sun_requirement
        }
    else:
        return None

#Routes for the Web App
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/")
def home():
    return render_template("home.html")

# Route for account details, update password, update security question
@app.route("/account/", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        if "password" in request.form:
            # Handle password change
            current_password = request.form["currentPassword"]
            new_password = request.form["newPassword"]
            confirm_password = request.form["confirmPassword"]

            if current_password == current_user.password and new_password == confirm_password:
                current_user.password = new_password  
                db.session.commit()
            else:
                pass
        elif "question" in request.form:
            # Handle security question update
            question = request.form["passwordQuestion"]
            answer = request.form["passwordAnswer"]
            # Update the user's security question and answer in the database
            db.session.commit()
        return redirect(url_for('account'))
    return render_template("account.html", user=current_user)

# Route to delete account
@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    # Code to delete the user's account
    db.session.delete(current_user)
    db.session.commit()
    # Log the user out and redirect to home
    logout_user()
    return redirect(url_for('home'))

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
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/calendar')
def index():
    events = Event.query.all()
    return render_template('calendar.html', events=events)

@app.route('/add_event', methods=['POST'])
def add_event():
    title = request.form['title']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')

    new_event = Event(title=title, start_date=start_date, end_date=end_date)

    try:
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('calendar'))
    except:
        return 'Error adding event'

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

    
    return render_template("calendar.html")

# myPlants Page Routes:

@app.route("/myPlants/")
@login_required
def myPlants():
    user_plants = Plant.query.filter_by(user_id=current_user.id).all()
    user_seeds = Seed.query.filter_by(user_id=current_user.id).all()
    return render_template("myPlants.html",user_plants=user_plants, user_seeds=user_seeds)

@app.route('/filter_plants', methods=['GET'])
@login_required
def filter_plants():
    selected_type = request.args.get('type', '')

    #Fetch filter plants based on the selected type
    if selected_type == 'All Plants' :
        user_plants = Plant.query.filter_by(user_id=current_user.id).all()
    else:
        user_plants = Plant.query.filter_by(user_id=current_user.id, plantType=selected_type).all()

    # Render the template with the filtered Plants
    rendered_html = render_template("filtered_plants.html", user_plants=user_plants)

    #Return the filtered HTML as a JSON response
    return jsonify(html=rendered_html)

@app.route('/search_plants', methods=['GET'])
@login_required
def search_plants():
    search_query = request.args.get('query', '').strip()

    # Fetch plants that match the search query
    user_plants = Plant.query.filter(
        or_(
            Plant.plantName.ilike(f"%{search_query}%"),
            Plant.plantType.ilike(f"%{search_query}%"),
            Plant.plantSunRequirement.ilike(f"%{search_query}%"),
            Plant.plantPlacement.ilike(f"%{search_query}%"),
        ),
        Plant.user_id == current_user.id
    ).all()

    # Render the template with the filtered Plants
    rendered_html = render_template("filtered_plants.html", user_plants=user_plants)

    # Return the filtered HTML as a JSON response
    return jsonify(html=rendered_html)


@app.route("/remove_plants", methods=["POST"])
@login_required
def remove_plants():
    try:
        # Get the plant IDs from the JSON request
        data = request.get_json()
        plant_ids = data.get('plantIds', [])

        # Remove the selected plants from the database
        Plant.query.filter(Plant.id.in_(plant_ids)).delete(synchronize_session=False)
        db.session.commit()

        # Return success response
        return jsonify(success=True)
    except Exception as e:
        print(f"Error: {e}")
        # Return error response
        return jsonify(success=False)

@app.route('/get_seeds/<seedType>')
@login_required
def get_seeds(seedType):
    # Fetch seeds only for the logged-in user and the selected plant type
    user_seeds = Seed.query.filter_by(user_id=current_user.id, seedType=seedType).all()

    # Convert the seed data to a format that can be easily converted to JSON
    seed_data = [{'name': seed.name} for seed in user_seeds]

    return jsonify(seed_data)

@app.route('/addSeedPlant', methods=['POST'])
@login_required
def addSeedPlant():
    # Get data from the addPlantSeed form
    selectedPlantType = request.form.get('selectedPlantType')
    seedName = request.form.get('selectedSeedName')
    seedDate = request.form.get('seedPlantDate')
    seedPlace = request.form.get('seedPlantPlace')

    #Function to convert seedDate to seedPlantDate which can be stored in db
    seedPlantDate = datetime.strptime(seedDate, '%Y-%m-%d').date()

    # Fetch additional information based on the selected seed
    seed_info = getSeedInfo(seedName)

    seedPlantMaturity="0"
    seedPlantGermination="0"
    seedSun="none"

    if seed_info:
        seedPlantMaturity = seed_info['maturity']
        seedPlantGermination = seed_info['germination']
        seedSun = seed_info['sunRequirement']

    notSeedling=0
    seedMaturityDate = seedPlantDate + timedelta(weeks=int(seedPlantMaturity))
    seedGerminationDate = seedPlantDate + timedelta(days=int(seedPlantGermination))

      # Print the received data for debugging
    print(f"addPlantName: {seedName}")
    print(f"addPlantType: {selectedPlantType}")
    print(f"addPlantDate: {seedPlantDate}")
    print(f"addPlantGermination: {seedPlantGermination}")
    print(f"addPlantMaturity: {seedPlantMaturity}")
    print(f"addPlantSun: {seedSun}")
    print(f"addPlantPlace: {seedPlace}")

    # Create a new plant with the form data
    new_plant = Plant(
        plantName=seedName,
        plantType=selectedPlantType,
        plantDate=seedPlantDate,
        plantPlacement=seedPlace,
        plantMaturity=seedPlantMaturity,
        maturityDate=seedMaturityDate,
        plantGermination= seedPlantGermination,
        germinationDate=seedGerminationDate,
        plantSunRequirement=seedSun,
        newSeedling=notSeedling,
        user_id=current_user.id
    )

    # Add the new plant to the database
    db.session.add(new_plant)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()

    # Redirect to the my plants page or another appropriate page
    return redirect(url_for('myPlants'))

@app.route('/add_plant', methods=['POST'])
@login_required
def add_plant():
    #Get data from form
    addPlantName = request.form.get('seedlingPlantName')
    addPlantType = request.form.get('seedlingPlantType')
    addPlantDate = request.form.get('seedlingPlantDate')
    addPlantMaturity = request.form.get('seedlingmaturityTime')
    addPlantSun = request.form.get('seedlingSunRequirement')
    addPlantPlace = request.form.get('seedlingPlantPlace')
    addPlantDate = request.form.get('seedlingPlantDate')

    plantDateAdded = datetime.strptime(addPlantDate, '%Y-%m-%d').date()

    #Convert the date string to a datetime object
    #plant_date = datetime.strptime(addPlantDate, '%Y-%m-%d').date()
    # Check if addPlantDate is not None
    if addPlantDate:
        # Convert the date string to a datetime object
        plant_date = datetime.strptime(addPlantDate, '%Y-%m-%d').date()
    else:
        # Handle the case where addPlantDate is None (or not provided)
        print("Error: 'seedlingPlantDate' is missing or has an invalid value.")
        return jsonify(success=False, error="Invalid 'seedlingPlantDate'")

    addMaturityDate = plantDateAdded + timedelta(weeks=int(addPlantMaturity))
    addPlantGermination = None
    addGerminationDate = plantDateAdded
    addNewSeedling = 1

    #Create newPlant from above
    newPlant = Plant (
        plantName=addPlantName,
        plantType=addPlantType,
        plantDate=plant_date,
        plantMaturity=addPlantMaturity,
        maturityDate=addMaturityDate,
        plantGermination= addPlantGermination,
        germinationDate=addGerminationDate,
        plantSunRequirement=addPlantSun,
        plantPlacement=addPlantPlace,
        newSeedling=addNewSeedling,
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

@app.route('/filter_seeds', methods=['GET'])
@login_required
def filter_seeds():
    selected_season = request.args.get('season', '')
    
    # Fetch filtered seeds based on the selected season
    if selected_season == 'All Seasons':
        user_seeds = Seed.query.filter_by(user_id=current_user.id).all()
    else:
        user_seeds = Seed.query.filter_by(user_id=current_user.id, when_to_plant=selected_season).all()

    # Render the template with the filtered seeds
    rendered_html = render_template("filtered_seeds.html", user_seeds=user_seeds)

    # Return the filtered HTML as a JSON response
    return jsonify(html=rendered_html)

@app.route('/search_seeds', methods=['GET'])
@login_required
def search_seeds():
    search_query = request.args.get('query', '').strip()

    # Fetch seeds that match the search query
    user_seeds = Seed.query.filter(
        or_(
            Seed.name.ilike(f"%{search_query}%"),
            Seed.seedType.ilike(f"%{search_query}%"),
            Seed.sun_requirement.ilike(f"%{search_query}%"),
            Seed.when_to_plant.ilike(f"%{search_query}%"),
        ),
        Seed.user_id == current_user.id
    ).all()

    # Render the template with the filtered seeds
    rendered_html = render_template("filtered_seeds.html", user_seeds=user_seeds)

    # Return the filtered HTML as a JSON response
    return jsonify(html=rendered_html)

@app.route("/remove_seeds", methods=["POST"])
@login_required
def remove_seeds():
    try:
        # Get the seed IDs from the JSON request
        data = request.get_json()
        seed_ids = data.get('seedIds', [])

        # Remove the selected seeds from the database
        Seed.query.filter(Seed.id.in_(seed_ids)).delete(synchronize_session=False)
        db.session.commit()

        # Return success response
        return jsonify(success=True)
    except Exception as e:
        print(f"Error: {e}")
        # Return error response
        return jsonify(success=False)

# Route for adding seed form submission
@app.route('/add_seed', methods=['POST'])
@login_required
def add_seed():
    #Get data from form
    seed_name = request.form.get('addSeedName')
    seedType = request.form.get('addSeedType')
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
        seedType=seedType,
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
