from flask import Flask, request, render_template
from geopy.geocoders import Nominatim
from datetime import datetime
import geopy.geocoders
import pandas as pd
import joblib

app = Flask(__name__)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/images')
def download_file():
    return

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/work.html')
def work():
    return render_template('work.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/result.html', methods = ['POST'])
def predict():
    rfc = joblib.load('crime_prediction.ipynb')

    if request.method == 'POST':
        try:
            address = request.form['Location']
            geolocator = Nominatim(user_agent="http")
            location = geolocator.geocode(address,timeout=None)
            lat = [location.latitude]
            log = [location.longitude]
        except:
            try:
                lat = [float(request.form['Latitude'])]
                log = [float(request.form['Longitude'])]
            except:
                return render_template('index.html', nudge = f'input latitude and longitude')


        latlong = pd.DataFrame({'latitude':lat,'longitude':log})

        if len(request.form['timestamp']) == 0:
            latlong['timestamp'] = str(datetime.now())
        else:
            latlong['timestamp'] = request.form['timestamp']
        data = latlong
        cols = data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        data = data[cols]
        data['timestamp'] = pd.to_datetime(data['timestamp'].astype(str), errors='coerce')

        column_1 = data.iloc[:,0]
        DT = pd.DataFrame({"year": column_1.dt.year,
                "month": column_1.dt.month,
                "day": column_1.dt.day,
                "hour": column_1.dt.hour,
                "dayofyear": column_1.dt.dayofyear,
                "week": column_1.dt.isocalendar().week,
                "weekofyear": column_1.dt.isocalendar().week,
                "dayofweek": column_1.dt.dayofweek,
                "weekday": column_1.dt.weekday,
                "quarter": column_1.dt.quarter,
                })
        data = data.drop('timestamp',axis=1)
        final = pd.concat([DT,data],axis=1)
        X = final.iloc[:,[1,2,3,4,6,10,11]].values
        my_prediction = rfc.predict(X)
        if my_prediction[0][0] == 1:
            precaution = 'Carry a weapon'
        elif my_prediction[0][1] == 1:
            precaution = 'Walk with friends or in a group, never have large amount of money or other valuables'
        elif my_prediction[0][2] == 1:
            precaution = 'Call police or ask people around'
        elif my_prediction[0][3] == 1:
            precaution = 'Always be aware of your surroundings and walk confidently, do not stop to talk to strangers'
        elif my_prediction[0][4] == 1:
            precaution = 'Do not go alone'
        else:
            my_prediction='Your place is safe. No crime expected at current timestamp!'
            precaution = 'all is well!'


    return render_template('result.html', prediction = my_prediction, precaution = precaution)


if __name__ == '__main__':
    app.run(debug = 0)