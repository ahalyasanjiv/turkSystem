# Turk System

## How to Run Locally
*** Note that we are using Python3 rather than Python2.

1. Clone this repo
```
git clone https://github.com/jchen2186/turkSystem.git
```

2. Create and use a virtual env
```
virtualenv .venv
source .venv/bin/activate
```

3. Install the requirements
```
pip3 install -r requirements.txt
```

4. Run the development server
```
python3 routes.py
```

Updating the Requirements
```
pip3 freeze > requirements.txt
```
