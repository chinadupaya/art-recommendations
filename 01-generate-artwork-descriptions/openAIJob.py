from openai import OpenAI
client = OpenAI()

batch_input_file = client.files.create(
  file=open("openai_batch_requests.jsonl", "rb"),
  purpose="batch"
)

# create the  batch
batch_input_file_id = batch_input_file.id

client.batches.create(
    input_file_id=batch_input_file_id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={
      "description": "nightly eval job"
    }
)

# check status of batch
from openai import OpenAI
client = OpenAI()

client.batches.retrieve("batch_abc123")