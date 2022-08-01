from googleapiclient import discovery
import json
API_KEY = 'AIzaSyB59cHvqbHCMLEqlFvE2H75CoNZDngadDo'

from flask import Flask, request, render_template, redirect, url_for, flash 
app = Flask(__name__)
app.config['SECRET_KEY'] = '215c98f152ba721fef23b0d0c0ce3218efa91ca07b1eab4c'

comments = []

# Home page displays usage instructions
@app.route('/')
def index():
    return render_template('index.html')

# Deals with the comment submission and redirects to results
@app.route('/test/', methods=('GET', 'POST'))
def test():
    if request.method == 'POST':
        if not request.form['comment']:
            flash('Please enter a comment')
        else: 
            comment = str(request.form['comment'])
            return redirect(url_for('results', comment=comment))
    return render_template('test.html')

@app.route('/results/')
def go_to_results():
    return render_template('results.html', comments=comments)
    
    # redirect(url_for('results', comment=comments[len(comments)]))

# API call retrieves toxicity score of the comment entered
@app.route('/results/<comment>')
def results(comment):

    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    analyze_request = {
        'comment': { 'text': comment },
        # if I try to pass <comment> for the text field, it breaks, but analyze_request doesn't seem 
        # to take parameters
        'languages':["en"],
        'requestedAttributes': {'TOXICITY': {}}
    }

    # API call
    response = client.comments().analyze(body=analyze_request).execute()
    data = json.dumps(response)
    response_str = json.loads(data)
    score = response_str["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

    percentage = round(score * 100, 2)
    percentage = str(percentage)+ "%"
    # Flash toxicity score
    flash('This comment is ' + percentage + ' likely to be toxic')
    # Add comment and score to the "database" here
    comments.insert(0, {'comment': comment, 'score': percentage})

    # Return all comments and toxicity scores
    return render_template('results.html', comments=comments)

if __name__ == '__main__':
  app.run(debug=True)
