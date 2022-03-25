"""Entry point for example chatbot application using Infermedica API.
Example:
    To start the application simply type::
        $ python3 chat.py APP_ID:APP_KEY
    where `APP_ID` and `APP_KEY` are Application Id and Application Key from
    your Infermedica account respectively.
Note:
    If you don't have an Infermedica account, please register at
    https://developer.infermedica.com.
"""
import argparse
import uuid

import conversation
import apiaccess


def get_auth_string(auth_or_path):
    """Retrieves authentication string from string or file.
    Args:
        auth_or_path (str): Authentication string or path to file containing it
    Returns:
        str: Authentication string.
    """
    if ":" in auth_or_path:
        return auth_or_path
    try:
        with open(auth_or_path) as stream:
            content = stream.read()
            content = content.strip()
            if ":" in content:
                return content
    except FileNotFoundError:
        pass
    raise ValueError(auth_or_path)


def new_case_id():
    """Generates an identifier unique to a new session.
    Returns:
        str: Unique identifier in hexadecimal form.
    Note:
        This is not user id but an identifier that is generated anew with each
        started "visit" to the bot.
    """
    return uuid.uuid4().hex





def run():
    """Runs the main application."""
  
    auth="719f2ba6:3aa363e21546a0fb03daed12aae8f3a8"
    a= None
    auth_string = get_auth_string(auth)
    case_id = new_case_id()
    

    # Read patient's age and sex; required by /diagnosis endpoint.
    # Alternatively, this could be done after learning patient's complaints
    age, sex = conversation.read_age_sex()
    print(f"Ok, {age} year old {sex}.")
    age = {'value':  age, 'unit': 'year'}

    # Query for all observation names and store them. In a real chatbot, this
    # could be done once at initialisation and used for handling all events by
    # one worker. This is an id2name mapping.
    naming = apiaccess.get_observation_names(age, auth_string, case_id, a)

    # Read patient's complaints by using /parse endpoint.
    mentions = conversation.read_complaints(age, sex, auth_string, case_id, a)

    # Keep asking diagnostic questions until stop condition is met (all of this
    # by calling /diagnosis endpoint) and get the diagnostic ranking and triage
    # (the latter from /triage endpoint).
    evidence = apiaccess.mentions_to_evidence(mentions)
    evidence, diagnoses, triage = conversation.conduct_interview(evidence, age,
                                                                 sex, case_id,
                                                                 auth_string,
                                                                 a)

    # Add `name` field to each piece of evidence to get a human-readable
    # summary.
    apiaccess.name_evidence(evidence, naming)

    # Print out all that we've learnt about the case and finish.
    print()
    conversation.summarise_all_evidence(evidence)
    conversation.summarise_diagnoses(diagnoses)
    conversation.summarise_triage(triage)


if __name__ == "__main__":
    run()