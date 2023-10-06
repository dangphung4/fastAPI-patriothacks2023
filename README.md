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
uvicorn main:app --reload # if you are in the app directory
uvicorn app.main:app --reload # if you are not in the app directory/ source directory
```

