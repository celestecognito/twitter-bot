name: Run Twitter Bot

on:
  schedule:
    - cron: '*/30 * * * *'  # runs every 30 minutes
  workflow_dispatch:  # allows manual trigger

jobs:
  run-bot:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests-oauthlib openai==0.28 schedule
    
    - name: Run bot
      env:
        CONSUMER_KEY: ${{ secrets.CONSUMER_KEY }} 
        CONSUMER_SECRET: ${{ secrets.CONSUMER_SECRET }}
        ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
        ACCESS_TOKEN_SECRET: ${{ secrets.ACCESS_TOKEN_SECRET }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: python gitbot.py
