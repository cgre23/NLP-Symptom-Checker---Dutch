from joblib import load
from flask import Flask, request
from flask_restful import Api, Resource
import pandas as pd
import nltk
from nltk.corpus import stopwords
from unidecode import unidecode
nltk.download('stopwords')

app = Flask(__name__)
api = Api(app)

# Load pipeline and model using the binary files
clf_loaded = load('artifacts/clf.joblib')
vectorizer = load('artifacts/vectorizer.pkl')
mlb = load('artifacts/mlb.pkl')
stop_words = stopwords.words('dutch')

def clean_text(df):
    regex_rules = {
        # remove linebreaks
        r'\n': ' ', 
        # remove return characters
        r'\r': ' ',  
        # remove postal code
        r'(?<!\d)\d{4}\s?[a-zA-Z]{2}(?![a-zA-Z])': '', 
        # remove email
        r'([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})': '',
        # remove phone numbers 
        r'((\+|00(\s|\s?\-\s?)?)31(\s|\s?\-\s?)?(\(0\)[\-\s]?)?|0)[1-9]((\s|\s?\-\s?)?[0-9])((\s|\s?-\s?)?[0-9])((\s|\s?-\s?)?[0-9])\s?[0-9]\s?[0-9]\s?[0-9]\s?[0-9]\s?[0-9]': '', 
        # Remove bank account info
        r'[a-zA-Z]{2}[\s.-]*[0-9]{2}[\s.-]*[a-zA-Z]{4}[\s.-]*[0-9]{2}[\s.-]*[0-9]{2}[\s.-]*[0-9]{2}[\s.-]*[0-9]{2}[\s.-]*[0-9]{2}[\s.-]*': ' ', 
        # remove URLs
        r'http\S+': '', 
        # remove .,;:-/ if not between digits
        r'(?<!\d)[.,;:\-/](?!\d)': ' ', 
        # remove remaining symbols
        r'[!?#$%&\'()*\+<=>@\\^_`{|}~"\[\]]': ' ', 
        # remove dates (day-month-year)
        r'[0-9]{1,2}[-/\s]([0-9]{1,2}|januari|februari|maart|april|juni|juli|augustus|september|oktober|november|december|jan|feb|mar|mrt|apr|mei|jun|jul|aug|sep|sept|okt|nov|dec)([-/\s][0-9]{2,4})?': ' ', 
        # remove any non-alphabetic characters
        r'[^a-zA-Z]': ' ', 
        # replace multiple spaces by one
        r'\s+': ' ', 
    }

    stopword_pattern = {'|'.join([r'\b{}\b'.format(w) for w in stop_words]): ''}

    return (df
        # convert to lowercase
        .assign(text_cleaned=lambda df_: df_.text.str.lower()) 
        # remove accents from letters and remove any non-ascii characters
        .assign(text_cleaned=lambda df_: 
                  df_.text_cleaned.apply(lambda x: unidecode(x)))
        # remove stopwords
        .assign(text_cleaned=lambda df_: 
                  df_.text_cleaned.replace(stopword_pattern, regex=True))
        # use regex rules to replace text that we are not interested in
        .assign(text_cleaned=lambda df_: 
                  df_.text_cleaned.replace(regex_rules, regex=True))
        )

# Function to test if the request contains multiple 
def islist(obj):
    return True if ("list" in str(type(obj))) else False

class Preds(Resource):
    def put(self):
        json_ = request.json
        # If there are multiple records to be predicted, directly convert the request json file into a pandas dataframe
        if islist(json_['text']):
            entry = pd.DataFrame(json_)
        # In the case of a single record to be predicted, convert json request data into a list and then to a pandas dataframe
        else:
            entry = pd.DataFrame([json_])
        # Transform request data record/s using the pipeline
        entry = clean_text(entry)
        entry = entry.drop(columns=['text'])
        entry_transformed = vectorizer.transform(entry['text_cleaned'])
        # Make predictions using transformed data
        prediction = clf_loaded.predict(entry_transformed)
        res = {'predictions': {}}
        # Create the response
        for i in range(len(prediction)):
            res['predictions'][i + 1] = mlb.inverse_transform(prediction[i].reshape(1,-1))
        return res, 200 # Send the response object

api.add_resource(Preds, '/predict')

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port=5050)





