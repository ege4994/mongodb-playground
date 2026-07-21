# mongodb-playground

A small Python + [pymongo] playground for experimenting with MongoDB indexes and reading
`explain()` output in **MongoDB Compass**.

This is the sample project behind my series of Medium articles on MongoDB indexes. Seed the
data below and you can reproduce every example from them on your own machine, with the same
numbers.

## What you get

A `playground` database with a single `users` collection of **50,000 documents**. The data is
generated with a fixed random seed, so everyone gets the exact same dataset and therefore the
exact same document counts in `explain()`.

Each document looks like this:

```json
{
  "user_id": 0,
  "name": "Katherine Lovelace",
  "email": "katherine.lovelace.0@example.com",
  "age": 54,
  "status": "active",
  "city": "Istanbul",
  "country": "TR",
  "role": "engineer",
  "score": 733,
  "signup_date": "2023-08-14T00:00:00Z"
}
```

The fields are shaped to make index behaviour visible: `email` is unique (great for
equality lookups), `status` is low-cardinality and weighted so roughly 60% of documents are
`"active"`, and `age`/`score`/`signup_date` are useful for range and sort examples.

## Prerequisites

Compass is only a **GUI client** — it needs a running MongoDB **server**. This project runs
one in Docker:

```bash
docker run -d \
  --name mongo-playground \
  -p 127.0.0.1:27017:27017 \
  -v mongo-playground-data:/data/db \
  --restart unless-stopped \
  mongo:7
```

The named volume keeps your data across restarts. Note the `127.0.0.1:` in the port mapping: it
binds MongoDB to localhost only. This server has no authentication, so you really don't want it
reachable from the network. Compass connects from the same machine, so nothing is lost. Any Docker setup works; this project was
built with [Colima], which needs to be started after every reboot:

```bash
colima start                    # start the VM
docker start mongo-playground   # only needed if the container isn't already up
```

Useful checks: `docker ps` and `colima status`.

Then point Compass at `mongodb://localhost:27017`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The only dependency is `pymongo`.

## Seed the data

Scripts import a shared `db.py`, so run them from inside the `scripts/` directory:

```bash
cd scripts
../.venv/bin/python ping.py   # verify the connection first
../.venv/bin/python seed.py   # create the 50,000 documents
```

> **Warning:** `seed.py` drops the `users` collection before reseeding it. That's intentional
> (it guarantees a clean, reproducible starting point), but don't run it if you have index
> experiments in progress that you want to keep.

You can pass a custom document count, though the article's numbers assume the default:

```bash
../.venv/bin/python seed.py 200000
```

After seeding, `users` has only the default `_id` index. That's the starting point for every
example.

## Reproduce the examples

The examples in the article are done by hand in Compass, which is the whole point — you get to
watch the plan change:

1. Open **playground → users** in Compass.
2. Paste the filter into the query bar. Some examples also need the **Sort** or **Project**
   fields, which live under **Options**.
3. Click **Explain** and read the plan, either as a Visual Tree or as Raw Output.
4. Add the index for that example under the **Indexes** tab.
5. Click **Explain** again and compare.

One convention worth keeping: **drop every index except `_id` before starting a new example.**
Otherwise MongoDB may pick a leftover index from a previous experiment and the plan won't match
what you expect.

## Configuration

Both scripts read these environment variables:

```bash
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DB="playground"
```

[pymongo]: https://pymongo.readthedocs.io/
[Colima]: https://github.com/abiosoft/colima
