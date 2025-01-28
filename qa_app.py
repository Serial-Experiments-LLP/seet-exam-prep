from dash import Dash, html, dcc, Output, Input, no_update, callback_context
import json
import dash
from dash.dependencies import State
import dash_bootstrap_components as dbc
import random


def answer_processing(q_json):
    choices = q_json['choices']
    answer = q_json['answer']
    options = []
    for i in choices:
        if i in answer:
            options.append({"label": html.Div([i], style={'color': 'Green', 'font-size': 20}), 
                            "value": i})
        else:
            options.append({"label": i, "value": i})
        
    return options



app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            html.H1("AWS CSA Preparation")
        ]),
        dbc.Row(id="question_row"),
        dbc.Row(id="choice_row"),
        dbc.Row([
            dbc.Col([
                dbc.Button("Submit", id="submit-btn", color='primary', n_clicks=0),
            ],width="auto"),
            dbc.Col([
                dbc.Button("Next Question", id="next-btn", color='secondary', n_clicks=0),
            ],width="auto")
        ]),
        dbc.Row(id="explanation_row",style={"display":"none"})
    ], id="question_container"),
    dbc.Container([
        dbc.Row([
            html.P("Congratulations. You've passed")
        ])
    ],id="completion_container" ,style={"display":"none"}),
    dcc.Store(id="question_counter", data=1),
    dcc.Store(id="correct_answer",data=1),
    # dcc.Store(id="selected_option_store",data=1),
])

# temporarily we are hardcoding the data file to load
# later change this to a dropdown to choos the question bank

with open('question_bank/sample_question_bank.json', 'r') as file:
    questions = json.load(file)

# randomizint the list
random.shuffle(questions)
total_questions = len(questions)

##whether to display completion or question
@app.callback(
    Output("question_container","style"),
    Output("completion_container","style"),
    Input("question_counter","data")
)
def main_display(question_counter):
    if question_counter > total_questions:
        return {'dispaly':'none'},{}
    return no_update,{'display':'none'}


# display question
@app.callback(
    Output("question_row","children"),
    Output("choice_row","children"),
    Output("correct_answer","data"),
    # Output("selected_option_store","data"),
    Input("question_counter","data"),
    Input("submit-btn","n_clicks"),
    State("correct_answer","data"),
    # State("selected_option_store","data")
)
def display_question(question_counter, submit_nclicks, correct_answer_options):
    if question_counter > total_questions:
        return  [], []
    ctx = callback_context
    if not ctx.triggered:
        component_id = "None triggered"
    else:
        component_id = ctx.triggered[0]['prop_id'].split(".")[0]

    index = question_counter -1
    question_dict = questions[index]
    question = question_dict['question']
    question_html = html.P(question)
    
    print(component_id)
    if component_id == "question_counter":

        correct_answer = answer_processing(question_dict)

        print(correct_answer)
        choice_component = dbc.RadioItems(
            options=[{"label": choice, "value": [choice]} for choice in question_dict["choices"]],
            value=None,
            style={"display": "block"},
        )
        if len(question_dict["answer"]) > 1:
            choice_component = dbc.Checklist(
                options=[{"label": choice, "value": choice} for choice in question_dict["choices"]],
                value=[],
                style={"display": "block"},
            ) 
        
        
        return question_html, choice_component, correct_answer
    
    elif component_id=="choice_row":
        
        return no_update, no_update, no_update
    
    elif component_id=="submit-btn":
        choice_component = dbc.RadioItems(
            options=correct_answer_options,
            value=None,
            style={"display": "block"},
        )
        if len(question_dict["answer"]) > 1:
            choice_component = dbc.Checklist(
                options=correct_answer_options,
                value=[],
                style={"display": "block"},
            )

        return no_update, choice_component, no_update
    else:
        return no_update, no_update, no_update
# updating question counter
@app.callback(
    Output("question_counter","data"),
    Input("next-btn","n_clicks"),
    State("question_counter","data")
)
def question_count_updater(next_button_clicks,question_counter):
    if next_button_clicks:
        new_question_counter = question_counter+1
        return new_question_counter
    return question_counter


# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
