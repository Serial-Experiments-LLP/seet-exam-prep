from dash import Dash, html, dcc, Output, Input, no_update, callback_context, State
import json
# import dash
# from dash.dependencies import State
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
            html.H1("AWS CSA Preparation", style={"textAlign": "center",'background-color':'orange'})
        ]),
        dbc.Row(id="question_row"),
        dbc.Row(id="choice_row"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Button("Previous", id="previous-btn", color='info', n_clicks=0),
            ],width="auto"),
            dbc.Col([
                dbc.Button("Submit", id="submit-btn", color='primary', n_clicks=0),
            ],width="auto"),
            dbc.Col([
                    dbc.Button("Next Question", id="next-btn", color='secondary', n_clicks=0),
            ],width="auto")
        ]),
        dbc.Row(id="explanation_row",style={"display":"none"})
    ], id="question_container"),
    html.Br(),
    dbc.Container([
        dbc.Row([
            dbc.Col([
            # html.P("Congratulations. You've passed")
            dbc.Button("Submit Test", id="test_submit-btn", color='success', n_clicks=0),
            ],width="auto"),])
    ],id="completion_container" ,style={"display":"none"}),
    html.Div(id="completion_message", style={"font-weight": "bold", "color": "green","text-align":"center"}),
    dcc.Store(id="question_counter", data=1),
    dcc.Store(id="correct_answer",data=0),
    dcc.Store(id='submitted',data=False),
])

# temporarily we are hardcoding the data file to load
# later change this to a dropdown to choose the question bank

with open('question_bank/sample_question_bank.json', 'r') as file:
    questions = json.load(file)

# randomizint the list
random.shuffle(questions)
total_questions = len(questions)

##whether to display completion or question
@app.callback(
    Output("question_container","style"),
    # Output("completion_container","style"),
    Input("question_counter","data")
)
def main_display(question_counter):
    if question_counter > total_questions:
        return {'dispaly':'none'}
    return no_update


# display question
@app.callback(
    Output("question_row","children"),
    Output("choice_row","children"),
    Output("correct_answer","data"),
    Output("explanation_row", "children"),
    Output("explanation_row","style"),
    Input("question_counter","data"),
    Input("submit-btn","n_clicks"),
    State("correct_answer","data"),
)

def display_question(question_counter, submit_nclicks, correct_answer_options):
    if question_counter > total_questions:
        return  [], [], [], {}
    ctx = callback_context
    if not ctx.triggered:
        component_id = "None triggered"
    else:
        component_id = ctx.triggered[0]['prop_id'].split(".")[0]

    index = question_counter -1
    question_dict = questions[index]
    question = question_dict['question']
    question_html = html.P(question)
    
    if component_id == "question_counter":

        # shuffled_options = question_dict["choices"]
        # random.shuffle(shuffled_options)

        correct_answer = answer_processing(question_dict)

        choice_component = dbc.RadioItems(
            options=[{"label": choice, "value": [choice]} for choice in question_dict['choices']],
            value=None,
            style={"display": "block"},
        )
        if len(question_dict["answer"]) > 1:
            choice_component = dbc.Checklist(
                options=[{"label": choice, "value": choice} for choice in question_dict['choices']],
                value=[],
                style={"display": "block"},
            ) 

        return question_html, choice_component, correct_answer, no_update, {"display": "none"}
    
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

        # explanation link to display after submit button click
        explanation_link = html.Div([html.Br(),
                                "Read explanation: ",
                                html.A(question_dict["url"], href=question_dict["url"], target="_blank", style={"color": "blue", "text-decoration": "underline"})
                            ])
    
        return no_update, choice_component, no_update, explanation_link, {"display": "block"}
    else:
        return no_update
    

# updating question counter
@app.callback(
    Output("question_counter","data"),
    Output("completion_container","style"),
    Input("next-btn","n_clicks"),
    Input("previous-btn","n_clicks"),
    State("question_counter","data")
)
def question_count_updater(next_button_clicks, previous_btn_clicks, question_counter):
    ctx = callback_context
    if not ctx.triggered:
        button_id = "None triggered"
    else:
        button_id = ctx.triggered[0]['prop_id'].split(".")[0]

    if button_id == 'next-btn' and question_counter < total_questions:
        question_counter +=1
    elif button_id == 'previous-btn' and question_counter>1:
        question_counter -=1

    completion_style = {'display':'block'} if question_counter == total_questions else {'display':'none'}
    return question_counter, completion_style


# to hide or show Next and Previous buttons
@app.callback(
    Output("previous-btn", "style"), 
    Output("next-btn", "style"),
    Input("question_counter", "data")
)
def hide_buttons(question_counter):
    prev_style = {"display": "none"} if question_counter == 1 else {"display": "inline-block"}
    next_style = {"display": "none"} if question_counter == total_questions else {"display": "inline-block"}
    return prev_style, next_style


# test submission
@app.callback(
    Output("completion_message","children"),
    Output("test_submit-btn", "disabled"), 
    Output("submitted", "data"), 
    Input("test_submit-btn", "n_clicks"),
    State("submitted", "data"),
    prevent_initial_call=True
)
def submit_test(n_clicks, submitted):
    if submitted:
        return no_update

    return "Activity Completed!.", True, True  


# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
