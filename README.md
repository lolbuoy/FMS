## Server

1. Cd into `server` and activate environment with `source ./bin/activate`

2. Install dependencies with `pip install -r requirements.txt`

3. Create a `.env` file and set the Redis DB url and poll interval here
```
REDIS_URL=redis://x.x.x.x:6379/0
REDIS_POLL_INTERVAL=3
```

4. Run the server by `python app/src.py`