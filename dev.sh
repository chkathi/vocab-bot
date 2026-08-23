#!/bin/bash
source .venv/bin/activate
cd backend && python3 app.py &
FLASK_PID=$!

sleep 2

cd vocab_learner_frontend && npm run dev

kill $FLASK_PID