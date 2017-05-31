# alexa-skill-chef-compliance

Alexa skill for Chef Compliance.  This allows the Amazon Echo to interact with a publicly accessible Chef Compliance server

## Setup

For this demo, I did the following:
- Installed Chef Compliance with an externally accessible IP.  I used the AWS Marketplace
- On the Compliance server
  - Add a user
  - Add an environment
  - Add at least one node
  - Run at least one scan
- In the [AWS Console](https://console.aws.amazon.com/lambda)
  - Create a new Lambda Service based on the Python 2.7 alexa-skills-kit-color-expert-python blueprint
  - Verify it is in a Region supported by Alexa Skills (us-east-1 in my case)
  - Paste the lambda code from the repo
  - Add 4 Environment variables
    - API_URL: https://ec2-aa-bb-cc-dd.compute-1.amazonaws.com/api
    - USER: *Not implemented*
    - AUTH_TOKEN: *Get this by logging into the Compliance server, then clicking the user’s avatar, then About
    - REFRESH_TOKEN: *Not implemented*
  - Role: Choose and existing role
  - Existing role: service-role/Lambda_basic_execution
  - Trigger: Alexa skill
  - Save
  - We’ll setup the tests after we create the skill
  - Copy the Lambda’s ARN to link from the Alexa skill
- In the [Amazon Developer Console](https://developer.amazon.com/home.html)
  - Create a new Alexa Skill
  - Name (and Invocation name): Chef Compliance
  - Configuration:
    - Endpoint: *paste the ARN of the lambda function*
    - No account linking or special permissions
    - Interaction model:
      - There are 2 UIs and a raw JSON method to define the interaction model.  The JSON is included in this repo.
    - Testing:
      - Enable the skill for testing.  Then you should be able  to see it available for use on any Echo registered to this account.
      - Enter an utterance into the test field and click “Ask Chef Compliance”.  This will generate and display the JSON request as well as the response from the Lambda function.
      - Copy the JSON Lambda Request
      - Go back to the Lambda, then select Actions --> Configure Test Event.  Select one and replace the data with your paste buffer contents.
      - Click Save and test to store that scenario and exercise the Lambda function.
      - You can modify the *”intent”: “name”* to test different scenarios
      - Once the Lambda is working well, switch back to the Skill and test using the defined voice Utterances.
      - Finally, go to your Echo and test the end-to-end path with voice.
        - Be sure to look at the Alexa app, also, to see the extra detail printed on some of the response cards.
- Optionally, get the ID of the Alexa Skill and place it in the Lambda code that checks the source of requests, uncommenting that code.  This will ensure the Lambda can only be run from the defined Alexa Skill.

## Sample utterances

There are several ways to interact with the Echo:

- Alexa, ask Chef Compliance “what version am I running?”
- Alexa, start Chef Compliance
  - How many users are there?
  - List my reports
  - How was the last run?
  - exit.
- Alexa, tell Chef Compliance, “Get my status”

## Things NOT implemented

- Generating Auth_tokens and using Refresh_tokens from the username/password.
- Setup a site so the user can login with Amazon credentials and save their Chef Compliance URL, username and password. Then add Account Linking to the Alexa Skill so it can lookup the Chef Compliance info based on the owner of the Echo.
- Add intents that trigger actions wihtin Chef Compliance.
  Note: Skills do not yet support dynamic “slots”.  A slot is a list of preferred variable values within an utterance (Ex, the COLOR in “My favorite color is COLOR”) which may make it tricky to recognize the names of scan profiles and nodes.
- Send a [notification](https://www.theverge.com/2017/5/16/15647074/alexa-notifications-being-added-amazon-echo) to the Echo when a scan fails
