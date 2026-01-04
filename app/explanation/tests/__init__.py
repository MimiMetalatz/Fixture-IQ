# This ensures:
#   .env is loaded automatically
#   os.environ[...] works everywhere
#   no repetition

from dotenv import load_dotenv

load_dotenv()