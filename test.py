import os
from dotenv import load_dotenv
load_dotenv()

data = os.getenv('TOKEN')
print(data)