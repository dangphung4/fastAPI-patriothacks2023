# fastAPI-patriothacks2023
## Our FastApi backend integrated with MongoDB

### Setting up a python enviornment

### Clone the Repository
```bash
git clone git@github.com:dangphung4/fastAPI-patriothacks2023.git
cd fastAPI-patriothacks2023
```

Install dependencies with :
```bash
pip install -r requirements.txt
```

Add a .env file and add the following contents to it:
```bash
MONGODB_URL= ###MONGO DB CONNECTION URL
```

How to run the server
```bash
cd app/
uvicorn main:app --reload # if you are in the app directory
uvicorn app.main:app --reload # if you are not in the app directory/ source directory
```
In order to create & run a virtual environment
type these into the terminal:
```bash
python3 -m venv env
.\env\Scripts\activate # for windows users
source ./env/bin/activate # for linux users

pip install -r requirements.txt
pip freeze > requirements.txt

deactivate # to exit virtual enviornment
```
