import os
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model

load_dotenv()

api_key = os.getenv("WATSONX_APIKEY")
project_id = os.getenv("WATSONX_PROJECT_ID")
url = os.getenv("WATSONX_URL")

print("API Key loaded:", bool(api_key))
print("Project ID loaded:", bool(project_id))
print("URL:", url)

credentials = Credentials(
    url=url,
    api_key=api_key
)

model = Model(
    model_id="ibm/granite-4-h-small",
    credentials=credentials,
    project_id=project_id
)

response = model.generate_text(
    prompt="In one sentence, explain why monitoring building energy consumption is important for sustainability."
)

print("\nGranite response:")
print(response)