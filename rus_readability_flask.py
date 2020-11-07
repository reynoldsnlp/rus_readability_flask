"""Flask webapp to compute readability of a text."""
from math import isnan
import sys

from flask import Flask
from flask import request
from flask import render_template
import joblib
import udar
from udar.features import ALL


app = Flask(__name__)
application = app  # our hosting requires `application` in passenger_wsgi


# load model
rf = joblib.load('rf.joblib')
print(len(rf.feature_importances_), 'features in RF model.', file=sys.stderr)
# load features
with open('rf.features') as f:
    feature_names = [line.strip() for line in f]
feature_extractor = ALL.new_extractor_from_subset(feature_names)


def absent():
    """Used as default in defaultdict's."""
    return 0


def get_CEFR_level(text):
    """Extract features and predict CEFR readability level."""
    text = text.replace('\r', '')
    doc = udar.Document(text, depparse=True)
    feature_names, feature_vector = feature_extractor(doc)
    feature_vector = [0 if isnan(x) else x for x in feature_vector]
    levels = rf.predict([feature_vector])
    return ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'][levels[0]]


# passenger sets '/' to be the path registered in cPanel
@app.route('/', methods=['GET', 'POST'])
def freq_form_post():
    """Build Russian readability page."""
    if request.method == 'GET':
        return render_template("readability_form.html")
    elif request.method == 'POST':
        level = get_CEFR_level(request.form['text'])
        return render_template('readability_form.html', level=level)


if __name__ == "__main__":
    app.debug = True
    app.run()
