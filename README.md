# Content Aggregator
Content aggregator that collects content from various sources and displays them in one place. Users can customize their feeds to only show content from certain sources or topics. Key features include automated content scraping from RSS feeds and web pages, a user-friendly interface for managing sources, and personalized recommendations.

# Installation
```shell
$ git clone https://github.com/MenachemBerkovich/Content-Aggregator.git
```

# Requirements
## Environment:
- MySQL Server installation with a database called `content_aggregator_db`.

- Required tables in the `content_aggregator_db` database:
### users_info:
```shell
+---------------------------+----------------+
| COLUMN_NAME               | COLUMN_TYPE    |
+---------------------------+----------------+
| addresses                 | json           |
| id                        | int            |
| last_password_change_date | varchar(19)    |
| password                  | varbinary(255) |
| sending_schedule          | int            |
| sending_time              | varchar(8)     |
| subscriptions             | json           |
| username                  | varchar(8)     |
+---------------------------+----------------+
```
### feeds_info:
```shell
+-------------+-------------+
| COLUMN_NAME | COLUMN_TYPE |
+-------------+-------------+
| categories  | json        |
| id          | int         |
| items_size  | int         |
| rating      | float(7,2)  |
| type        | text        |
| url         | text        |
+-------------+-------------+

```
## Libraries
See the ```requirements.txt``` file for the required Python libraries.

# Usage 
1. Navigate to the downloaded Content-Aggregator folder.
2. Make sure all the necessary configurations are set in the ```/lib/config.py``` file:
```python
SQL_USERNAME: str = os.environ["SQL_USERNAME"]

SQL_HOST: str = os.environ["SQL_HOST"]

SQL_PASSWORD: str = os.environ["SQL_PASSWORD"]

DATABASE_NAME: str = os.environ["DATABASE_NAME"]
```
3. Run the following command:
```shell
$ python3 contentaggregator
```
4. You should see the following output:
```shell
ready started server on 0.0.0.0:3000, url: http://localhost:3000
```
5. Open ```http://localhost:3000``` in your web browser to access the user-friendly GUI.
6. Keep the application running, in order to receive system messages, as it is currently running locally.

# Notes
Right now, the application supports email sending and XML-Based Feed only.

# Contact
For any questions or inquiries, feel free to reach out via email: bermen.system@gmail.com
