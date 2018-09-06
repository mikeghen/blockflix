# BlockFlix
This is a Flask application that implements an DVD Rental company's online transaction processing (OLTP) application. This application implements a database schema similar to loosely modeled after MySQL's Sakila sample database.

This project is designed to be used in a [Full Stack Data Engineering](http://google.com) course. There is no real front end functionality beyond a few data tables. Use this application for practicing seeding data, deploying applications, and performing ETL operations.


## Running with Docker
Build the Docker image for Blockflix:
```
docker build -t blockflix .
```
Run the application and database with Docker Compose:
```
docker-compose up
```
Access the applicaiton on port 5000:
```
http://localhost:5000
```

## Development Setup
Follow these instructions to install the application on your computer.

### Install OS Dependencies
Install these OS dependencies:
* MySQL
* Python 3
* Nodejs

### Application Installation
Download the application codebase, install the Python packages and Node.js packages:
```
git clone https://github.com/mikeghen/blockflix
cd blockflix
pip install -r requirements/dev.txt
npm install
```
Set the following Flask environment variables before running the application:
```
export FLASK_APP=autoapp.py
export FLASK_DEBUG=1
```
### Database Setup
Start by creating the application's database on your MySQL database server and database user:
```
CREATE DATABASE blockflix_development;
CREATE USER 'blockflix'@'127.0.0.1' IDENTIFIED BY 'blockflix';
GRANT ALL PRIVILEGES ON blockflix_development.* TO 'blockflix'@'localhost';
```
Run the following to create database tables for the application:
```
flask db upgrade
```

### Start the Application
Finally, run the development server with:
```
npm start
```

## Deployment
To deploy:
```
export FLASK_DEBUG=0
npm run build   # build assets with webpack
flask run       # start the flask server
```
In your production environment, make sure the ``FLASK_DEBUG`` environment
variable is unset or is set to ``0``, so that ``ProdConfig`` is used.

:information_source: We will use Elastic Beanstalk to deploy the application.

## Shell

To open the interactive shell, run ::
```
flask shell
```
By default, you will have access to the flask ``app``.


## Running Tests

To run all tests, run:
```
flask test
```

## Migrations

Whenever a database migration needs to be made. Run the following commands ::
```
flask db migrate
```
This will generate a new migration script. Then run ::
```
flask db upgrade
```
To apply the migration.

For a full migration command reference, run ``flask db --help``.


## Asset Management
Files placed inside the ``assets`` directory and its subdirectories
(excluding ``js`` and ``css``) will be copied by webpack's
``file-loader`` into the ``static/build`` directory, with hashes of
their contents appended to their names.  For instance, if you have the
file ``assets/img/favicon.ico``, this will get copied into something
like
``static/build/img/favicon.fec40b1d14528bf9179da3b6b78079ad.ico``.
You can then put this line into your header::
```
<link rel="shortcut icon" href="{{asset_url_for('img/favicon.ico') }}">
```
to refer to it inside your HTML page.  If all of your static files are
managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they
should cache all your assets forever by including the following line
in your ``settings.py``::
```
SEND_FILE_MAX_AGE_DEFAULT = 31556926  # one year
```
