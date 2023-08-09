"""Flask webapp to compute readability of a text."""
from collections import Counter
from math import isnan
import os.path
import re

from flask import Flask
from flask import request
from flask import render_template
import joblib
from markupsafe import Markup
import udar
from udar.features import ALL
from udar.features.features import _get_lexmin_dict


app = Flask(__name__)
application = app  # our hosting requires `application` in passenger_wsgi

local_dir = os.path.dirname(os.path.abspath(__file__))

CEFR_levels = ['A1', 'A2', 'B1', 'B2']  # , 'C1', 'C2']
lexmin_dict = _get_lexmin_dict()
level2classes = {"A1": "tag is-primary",
                 "A2": "tag is-link",
                 "B1": "tag is-warning",
                 "B2": "tag is-danger"}
gt2str_pos = {"N": "noun",
              "A": "adj",
              "V": "verb",
              "Adv": "adv",
              "Pron": "pronoun",
              "Pr": "prep",
              "Pcle": "particle",
              "CLB": "punc",
              "PUNCT": "punc",
              "CC": "coord conj",
              "CS": "subord conj"}

# load model
rf = joblib.load(f'{local_dir}/rf.joblib')
# print(len(rf.feature_importances_), 'features in RF model.', file=sys.stderr)
# load features
with open(f'{local_dir}/rf.features') as f:
    feature_names = [line.strip() for line in f]
feature_extractor = ALL.new_extractor_from_subset(feature_names)


def absent():
    """Used as default in defaultdict's."""
    return 0


def predict_CEFR_level(doc):
    """Extract features and predict CEFR readability level."""
    feature_names, feature_vector = feature_extractor(doc)
    feature_vector = [0 if isnan(x) else x for x in feature_vector]
    levels = rf.predict([feature_vector])
    return CEFR_levels[levels[0]]


def clean_lemma(lemma: str) -> str:
    """Remove superscript enumerators from lemmas."""
    return re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰⁻]+', '', lemma)


def get_lemma_CEFR_dist(doc):
    lemmas = {(lev, level2classes[lev]): Counter() for lev in CEFR_levels}  # (lev, lev_class): (lemma, pos): freq
    lemmas[(None, "")] = Counter()
    for sent in doc.sentences:
        for tok in sent:
            reading = tok.most_likely_reading()
            lemma = clean_lemma(reading.lemmas.pop())
            pos = {gt2str_pos.get(subr.tags[0], subr.tags[0]) for subr in reading.subreadings}.pop()
            level = lexmin_dict.get(lemma)
            lev_class = level2classes.get(level, "")
            lemmas[(level, lev_class)].update([(lemma, pos)])
    return lemmas


def tok2html_func(tok, **kwargs):
    """Pass in to udar.Doc.to_html()."""
    levels = {lexmin_dict[clean_lemma(lemma)]
              for lemma in tok.lemmas
              if clean_lemma(lemma) in lexmin_dict}
    if not levels:
        return tok.text
    else:
        if len(levels) > 1:
            print('WARNING: multiple lemmas:', tok.to_dict())
        return f'''<span class="{level2classes[levels.pop()]}">{tok.text}</span>'''


# passenger sets '/' to be the path registered in cPanel
@app.route('/', methods=['GET', 'POST'])
def root():
    """Build Russian readability page."""
    if request.method == "GET":
        return render_template("readability_form.html")
    elif request.method == "POST":
        text = request.form['text'].replace('\r', '')
        doc = udar.Document(text, depparse=True)
        level = predict_CEFR_level(doc)
        lemma_dist = get_lemma_CEFR_dist(doc)
        annotated_text = Markup(doc.to_html(tok2html_func=tok2html_func))
        return render_template('readability_report.html',
                               level=level,
                               level2classes=level2classes,
                               lemma_dist=lemma_dist,
                               annotated_text=annotated_text)
