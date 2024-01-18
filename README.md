# NLP Symptom Checker - Dutch
### by Christian Grech

To advice users of a medical app about plausible causes of their complaints, the urgency, and inform on where to go next, a symptom checker is required. The starting point of this symptom checker is a free text input field which helps the user select their chief complaint.

Selecting a chief complaint is not a trivial task for users. An API that allows users to describe their medical situation in their own words upon which the API suggests a list of the most suitable chief complaints. Since multiple chief complaints can be valid for a patient's description, we interpret the task as a multi-class multi-label classification task.


## Data

There are two data files:

* user_inputs.csv, containing texts describing medical complaints, entered by users of
our app.
* labels.csv, the corresponding chief complaints, annotated by a medical expert.

## Model training

A XG Boost classifier model is trained in the Jupyter Notebook called *Training.ipnyb*.  The model is already trained and all the artifacts are saved in the artifacts folder. An API is then created in the *app.py* file which launches the model and provides predictions.  Activate the virtual environment. If the venv folder is not available, a new virtual environment can be created using the available *requirements.txt* file.

The model takes as input the free text from users, and outputs multiple possible medical diagnoses. The API is public and can be tested as described in the ** Deploying to Google Cloud (public API) ** section


## Build Docker container locally

Run the following command to build the container from the available Dockerfile file:

    docker build -t flask-predict-api .
    
To launch the container locally run:
    
    docker run -d -p 5050:5050 flask-predict-api

## API

The API created using Flask takes as input a dictionary with the parameter text, and a list of complaints. It returns a list of labels. Here is an example with two input complaints, that can be used locally (see next section for the public API):

    curl -XPUT -H "Content-type: application/json" -d '{"text": ["2 weken heb ik een kriebelhoest waar ik niet vanaf kom. soms ook hees. Wat kan ik doen? Heb al codeiene geprobeerd, Ventolin van mijn man. beide geven geen verlichting. mijn werk vraagt dat ik de hele dag kan praten. ik heb dan hoestbuien.", "Er is een teek op mijn been. Ik ben bang dat die er al een tijdje op heeft gezeten"]}' 'http://127.0.0.1:5050/predict'

    {
        "predictions": {
            "1": [
                [
                    "Hoesten",
                    "Stemklachten of heesheid"
                ]
            ],
            "2": [
                [
                    "Tekenbeet"
                ]
            ]
        }
    }
    
    
In case of using the API for just one example, use this format: 

    curl -XPUT -H "Content-type: application/json" -d '{"text": "2 weken heb ik een kriebelhoest waar ik niet vanaf kom. soms ook hees. Wat kan ik doen? Heb al codeiene geprobeerd, Ventolin van mijn man. beide geven geen verlichting. mijn werk vraagt dat ik de hele dag kan praten. ik heb dan hoestbuien."}' 'http://127.0.0.1:5050/predict'
    
    
## Deploying to Google Cloud (public API)

Retrieve an authentication token and authenticate your Docker client to your registry. Use the Google Cloud CLI:

    gcloud builds submit --region=us-west2 --tag us-west2-docker.pkg.dev/your-space/flaskapi-docker-repo/flask-predict-api:latest

After the build completes, tag your image and push the image to this repository:

    gcloud builds submit --region=us-west2 --tag us-west2-docker.pkg.dev/your-space/flaskapi-docker-repo/flask-predict-api:latest
    
On the Cloud Run interface start a service. Make sure the service allows unauthenticated access and the right port access. Now anyone can access the API using this command:

    curl -XPUT -H "Content-type: application/json" -d '{"text": ["2 weken heb ik een kriebelhoest waar ik niet vanaf kom. soms ook hees. Wat kan ik doen? Heb al codeiene geprobeerd, Ventolin van mijn man. beide geven geen verlichting. mijn werk vraagt dat ik de hele dag kan praten. ik heb dan hoestbuien.", "Er is een teek op mijn been. Ik ben bang dat die er al een tijdje op heeft gezeten"]}' 'https://flask-predict-api-arb6xi42dq-ew.a.run.app/predict'
    
Here is an example of three complaints and the response from the terminal:
    
    curl -XPUT -H "Content-type: application/json" -d '{"text": ["2 weken heb ik een kriebelhoest waar ik niet vanaf kom. soms ook hees. Wat kan ik doen? Heb al codeiene geprobeerd, Ventolin van mijn man. beide geven geen verlichting. mijn werk vraagt dat ik de hele dag kan praten. ik heb dan hoestbuien.", "benen", "Al enkele weken last van pijn bij mijn kaak , vanaf vorige week druk op mijn oor en hoofdpijn. Vanmorgen wakker geworden met pijnlijk dik oog en hoofdpijn. Oog is dunner maar niet minder pijnlijk"]}' 'https://flask-predict-api-arb6xi42dq-ew.a.run.app/predict'
    
Response:
    {
        "predictions": {
            "1": [
                [
                    "Hoesten",
                    "Stemklachten of heesheid"
                ]
            ],
            "2": [
                [
                    "Beenklachten"
                ]
            ],
            "3": [
                [
                    "Hoofdpijn",
                    "Oogklachten of beschadigingen aan het oog"
                ]
            ]
        }
    }
    
I have attached the deployment.yaml file in this folder which currently runs the container on Google Cloud. Feel free to try the API with different texts!


## Improvements

* Improving the model, including better preprocessing and finetuning.
* Trying LLMs such as BERT, RobBERTa.....I tried some Dutch versions of these LLMs from HuggingFace but I did not have the time to finetune as I lack GPU/TPU resources.
* Scaling the deployment to Kubernetes for better load balancing/manageability.
