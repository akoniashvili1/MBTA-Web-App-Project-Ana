from flask import Flask, render_template, request, redirect, url_for
import mbta_helper

app = Flask(__name__)


@app.route("/")
def index():
    """Render the home page with a form to input place name"""
    return render_template("index.html")


@app.route("/nearest_mbta", methods=["POST"])
def nearest_mbta():
    """Handle the form submission and find the nearest MBTA station"""
    try:
        # Get the place name from the form
        place_name = request.form.get("place_name", "").strip()
        
        if not place_name:
            return render_template("error.html", 
                                 error_message="Please enter a place name or address.")
        
        # Find the nearest MBTA station
        station_name, wheelchair_accessible = mbta_helper.find_stop_near(place_name)
        
        # Render the results page
        return render_template("mbta_station.html", 
                             place_name=place_name,
                             station_name=station_name,
                             wheelchair_accessible=wheelchair_accessible)
        
    except Exception as e:
        # Handle any errors that occur
        return render_template("error.html", 
                             error_message=f"Sorry, we couldn't find MBTA information for that location. Error: {str(e)}")


@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template("error.html", 
                         error_message="Page not found."), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template("error.html", 
                         error_message="Internal server error. Please try again."), 500


if __name__ == "__main__":
    app.run(debug=True)