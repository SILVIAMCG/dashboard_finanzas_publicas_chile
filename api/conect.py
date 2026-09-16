import os
import bcchapi
from dotenv import load_dotenv

load_dotenv()

siete = bcchapi.Siete(token=os.getenv("API_TOKEN"))

