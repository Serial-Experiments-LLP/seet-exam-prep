from dash import Dash, html, dcc, Output, Input, no_update, callback_context, State
import dash_bootstrap_components as dbc
import random
import os
import json

"""
Change this value to limit the number of questions presented from a json file.
For example if your json file has 200 questions but you want to revise only 50 of them
at a time then you mention 50 below.

0 and a number greater than the actual number of questions will show all questions in the json file.
"""
question_limit = 0

app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR], suppress_callback_exceptions=True)

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

test_options = []
for each_file in os.listdir("question_bank"):
    if each_file.endswith(".json"):
        filepath = f"question_bank/{each_file}"
        with open(filepath, 'r', encoding='utf8') as f:
            json_data = json.load(f)
        if "test_name" in json_data:
            test_name = json_data['test_name']
            test_options.append(
                {"label":test_name, "value":filepath}
            )

navbar = dbc.NavbarSimple(
    brand="Test Prepper",
    brand_href="#",
    color="dark",
    dark=True,
)


test_selection_dropdown = dcc.Dropdown(
    options = test_options,
    id = "test_selection_dropdown",
    placeholder="Please choose a test and click start test",
    
)

blank_question_content = [
    html.Div(id="question_row", style={"display":"none"}),
    dbc.Checklist(id="answer_choices", style={"display":"none"}),
    dbc.Button(id="submit-btn", style={"display":"none"}),
    dbc.Button(id="next-btn", style={"display":"none"}),
    html.Div(id="explanation_row", style={"display":"none"}),
    html.Div(id="url_row", style={"display":"none"}),
]


question_content = [
    dbc.Row(id="question_row"),
    dbc.Row([
        dbc.Checklist(
            id="answer_choices",
            style={"display":"block"},
            inputCheckedClassName="border border-success bg-success",
        )
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Submit", id="submit-btn", color='success', n_clicks=0, disabled=True),
        ],width="auto"),
        dbc.Col([
                dbc.Button("Next Question", id="next-btn", color='info', n_clicks=0),
        ],width="auto")
    ], className="mt-2"),
    dbc.Row(id="explanation_row", style={"display":"none"}, className="mt-2"),
    dbc.Row(id="url_row", style={"display":"none"}, className="mt-2")
]


app.layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col([
                test_selection_dropdown
            ], width=4),
            dbc.Col([
                dbc.Button("Start Test", id="start_test_button", color="success", disabled=True)
            ], width="auto"),
        ], className="mt-2"),
        html.Div(blank_question_content, id="question_div", className="mt-2"),
    ]),
    dcc.Store(id="question_counter", data=0),
    dcc.Store(id="question_bank"),
    dcc.Store(id="question_bank_length", data=0),
    dcc.Store(id="correct_answer", data=None)
])

# Populating the question div
@app.callback(
    Output("question_div", "children"),
    Input("test_selection_dropdown", "value"),
    Input("start_test_button", "n_clicks"),
    Input("question_counter", "data"),
    State("question_bank_length", "data")
)
def question_div_populator(test_selection_dropdown_value, start_test_nclicks, question_counter, question_bank_length):
    ctx = callback_context
    if not ctx.triggered:
        component_id = "None triggered"
    else:
        component_id = ctx.triggered[0]['prop_id'].split(".")[0]
    
    if component_id == "test_selection_dropdown":
        return blank_question_content
    elif component_id == "start_test_button":
        if not test_selection_dropdown_value:
            return blank_question_content
        else:
            return question_content
    elif component_id == "question_counter":
        if question_counter >= question_bank_length:
            return [html.H2("Awesome! You have completed the test.", className="mt-4")]+blank_question_content
        else:
            return no_update
    else:
        return no_update


# disable start test button when test dropdown is blank
@app.callback(
    Output("start_test_button", "disabled"),
    Input("test_selection_dropdown", "value"),
    Input("question_row", "children")  
)
def start_test_button_toggler(test_selection_dropdown_value, question_row_children):
    if test_selection_dropdown_value and question_row_children is None:
        return False
    return True

# Populating the question data when the start test button is clicked
# or if the dropdown value changes
@app.callback(
    Output("question_counter", "data"),
    Output("question_bank", "data"),
    Output("question_bank_length", "data"),
    Input("start_test_button", "n_clicks"),
    Input("test_selection_dropdown", "value"),
    Input("next-btn", "n_clicks"),
    State("question_counter", "data"),
)
def background_data_manager(start_test_button_clicks, test_selection_dropdown_value, next_button_clicks, question_counter):
    ctx = callback_context
    if not ctx.triggered:
        component_id = "None triggered"
    else:
        component_id = ctx.triggered[0]['prop_id'].split(".")[0]
    
    if component_id == "test_selection_dropdown":
        return 0, None, 0
    elif component_id == "start_test_button":
        if not test_selection_dropdown_value:
            return no_update
        with open(test_selection_dropdown_value, 'r', encoding='utf8') as f:
            json_data = json.load(f)
        question_bank = json_data['questions']
        random.shuffle(question_bank)

        # if there is a limit mentioned then restrict the number of questions as per limit
        if question_limit > 0 and question_limit < len(question_bank):
            question_bank = question_bank[:question_limit]
        
        question_bank_length = len(question_bank)
        return 0, question_bank, question_bank_length
    elif component_id == "next-btn":
        updated_question_counter = question_counter+1
        return updated_question_counter, no_update, no_update
    else:
        return no_update


# Question populator
@app.callback(
    Output("question_row", "children"),
    Output("answer_choices", "options"),
    Output("answer_choices", "value"),
    Output("explanation_row", "children"),
    Output("url_row", "children"),
    Input("question_counter", "data"),
    Input("submit-btn", "n_clicks"),
    State("question_bank", "data"),
    State("question_bank_length", "data"),
    State("answer_choices", "value"),
)
def single_question_populator(question_counter, submit_button_clicks, question_bank, question_bank_length, selected_choices):
    
    if question_counter>=question_bank_length or not question_bank:
        return no_update
    
    ctx = callback_context
    if not ctx.triggered:
        component_id = "None triggered"
    else:
        component_id = ctx.triggered[0]['prop_id'].split(".")[0]
    
    question_dict = question_bank[question_counter]
    
    question = question_dict['question']
    question_html = html.H4(question)
    correct_answer_options = answer_processing(question_dict)
    
    explanation = ""
    if "explanation" in question_dict:
        explanation = question_dict['explanation']
    explanation_html = html.P(explanation, style={"margin-bottom":0})

    url = ""
    if "url" in question_dict:
        url = question_dict['url']
    url_html = html.A(url, href=url, target="_blank", style={"color": "blue", "text-decoration": "underline"})

    options = [{"label": choice, "value": choice} for choice in question_dict['choices']]
    value = []
    if component_id=="submit-btn":
        options = correct_answer_options
        value = selected_choices

    return question_html, options, value, explanation_html, url_html
    

# toggling display of explanation and url
@app.callback(
    Output("explanation_row", "style"),
    Output("url_row", "style"),
    Input("submit-btn", "n_clicks"),
    Input("next-btn", "n_clicks")
)
def display_explanation(submit_clicks, next_clicks):
    ctx = callback_context
    if not ctx.triggered:
        component_id = "None triggered"
    else:
        component_id = ctx.triggered[0]['prop_id'].split(".")[0]
    
    if component_id=="submit-btn":
        return {}, {}
    elif component_id=="next-btn":
        return {"display":"none"},{"display":"none"}
    else:
        return no_update


# toggling the submit button
@app.callback(
    Output("submit-btn", "disabled"),
    Input("answer_choices", "value")
)
def submit_toggler(selected_choices):
    if selected_choices:
        return False
    return True

if __name__ == '__main__':
    app.run_server(debug=True)