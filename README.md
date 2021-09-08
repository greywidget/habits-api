# Habits API

Keep track of your daily habits.

Inspired by the excellent book [Atomic Habits](https://jamesclear.com/atomic-habits) by James Clear

Please set your `DATABASE_URL` environment variable:

```
cp .env-template .env
# update DATABASE_URL in .env
```

To run the `uvicorn` webserver:

```
uvicorn habits.main:app --reload
```

Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to use the app!
