# AccommodationRecommendation
Accommodation Recommendation System using PyMongo

### About the project
This project aims to build a basic recommendation system with a menu driven program by designing queries in MongoDB by combining it with Python. The menu that we create will contain various queries from which the customer can choose one, and then input the values of the criteria based on which they want the recommendation to be filtered. Each output will consist of the total number and the list of records in the collection satisfying the given criteria. The customer is again displayed the menu so that they can either go for another filtering method if required, or quit.

### Dataset
The project is done on [Airbnb](https://en.wikipedia.org/wiki/Airbnb)'s publicly available [dataset](https://github.com/ashmeetchhabra/AirBnB-Data-analysis-and-recommendation-system/blob/master/airbnb500.csv) of New York City. Other datasets are available for exploration [here](http://insideairbnb.com/). The dataset used here has a single collection called "listing", and consists of 499 listings(rows) and 19 fields(columns) each.
- id, name, host_id, host_name, neighbourhood_group, neighbourhood, latitude, longitude, room_type, price, minimum_nights, number_of_reviews, last_review, reviews_per_month, calculated_host_listings_count, availability_365, review_val, rating, text_review

Sample data:

![SampleData](https://user-images.githubusercontent.com/67685791/120346170-c1069e80-c318-11eb-899f-325ceb1b0e63.png)

### Connection and import
Initially, the database is imported to MongoDB using the mongoimport command or MongoDB Compass application. Connection is then established between Python and Mongo using the Pymongo driver, with the help of the MongoClient class instance. After the coding, it is supposed to look like this:

![Connection and import](https://user-images.githubusercontent.com/67685791/120346702-3e321380-c319-11eb-9583-c7bea6f18b07.png)

Here, “accomodation” is the database name and “listing” is the collection name.

The menu has 10 queries and an option to quit.

![Menu](https://user-images.githubusercontent.com/67685791/120347654-1abb9880-c31a-11eb-8359-75c8efa7d397.png)

For each query, a separate function has been written, with some interlinked based on the logic. The listing id (feature "id") is the key of the documents, apart from the system generated feature "\_id".
