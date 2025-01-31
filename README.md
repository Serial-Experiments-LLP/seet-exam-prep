# Overview
This app helps in revising your test material with your own set of multiple choice questions.

# Setup

Requirements for your own use:

- Python installed on your machine. I've tested on python 3.13.0. I guess this code will work with python 3.10+ versions.
- You should know how to run python scripts in a virtual environment.
- Your own set of questions prepared in the required json structure.

Start by cloning this repository from your terminal.

```
git clone https://github.com/Serial-Experiments-LLP/seet-exam-prep.git
```

Navigate into the folder

```
cd seet-exam-prep
```

Create a virtual environment

```
python -m venv venv
```

If using linux or mac, create a virutal environment with `python3 -m venv venv`. If you don't have the venv package installed on your machine you will get the instructions to install it along with the error message.

Once virtual environment is created, activate it.

to activate virtual environment on windows
```
venv/Scripts/activate
```

to acvivate virtual environment on linux/mac
```
source venv/bin/activate
```

Once you have activated the virtual environment, install the required packages.

You can install with the provided requirements.txt file

```
pip install -r requirements.txt
```

There are actually only two packages required for this app to work - dash and dash-bootstrap-components. If the python version you have is not letting you install the packages mentioned in requirements.txt you can try intalling the packages directly by running `pip install dash dash-bootstrap-components`

Now you are done setting up the app. You can now test it by running the following command.

```
python test_prep.py
```

Copy the url that is generated and open it in your browser. You can use any of the sample tests provided to see how the app works.

# Your own question sets

You can create your own set of questions, prepare them in the json format that the app reads and place the json file in the question_bank folder.

Below is the structure for a question bank that the app supports.

```
{
    "test_name": "A name that will feature in the dropdown for the user to select",
    "questions":[
        {
            "question": "A question?",
            "choices": [
                "choice 1",
                "choice 2",
                "choice 3"
            ],
            "answer": ["choice 2"],
            "explanation": "Reason why the answer is correct",
            "url": "http://example.com"
        }
    ]
}
```

Let's look at each of the key and value pairs in this json.

- **test_name**: This is the title of the test. When the app starts it reads all the files in the question_bank folder and populates the dropdown with the test_name values.
- **questions**: This will be a list of all the question. Each question is a dictionary/json.
- **question**: This field is the question that the user needs to answer.
- **choices**: This will be a list of choices. There can be as many choices as you want.
- **answer**: This is a list of correct choices. Ensure the exact text (case sensitive) as in the correct choices are used in the answer list
- **explanation**: This is an optional field. You can add an explanation that will be shown to the user when he/she clicks the submit button.
- **url**: This is an optional field. You can also provide a reference url where there is detailed explanation or references for the user to check.

You can refer to the sample question_banks that are provided to get an idea.

# Limiting the number of questions dispalyed from a question bank

Sometimes you might have a lot of questions in one json file. If you want to restrict the number of questions shown for that json file you can do it by changing the "question_limit" value in the test_prep.py file. It is at the beginning right after the imports.

# Generating questions using AI

I created this app so that I can prepare for my AWS certifications. Typing out all the questions along with their choices as well as explanation is a time consuming task. So I took the help of ChatGPT (openAI api actually).

In the prompt.txt file you will find the prompt I used to generate questions from some reading material. What I did was copy the text in AWS documentation and paste it below the INPUT TEXT heading (one chapter at a time). I then modify how many questions I want ChatGPT to generate and it generates accordingly. These questions I pasted in the json file.

You will notice that there is no url in the prompt. That's because these LLMs try to access the url even though the actual text has been provided. This creates some problems and you don't get an output. I couldn't stop the LLM from accessing the URL. Maybe reframing the prompt might help. Anyway, I included the urls for each question manually later in the json file.

I found that the quality of questions is better when I used Gemini Pro. Since I already had access to OpenAI API I used that. It's upto you. A different prompt and LLM might give you good results.
