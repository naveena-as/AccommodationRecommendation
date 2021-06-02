import pymongo
import sys
from datetime import datetime
from pprint import pprint

connection = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
database = connection['accomodation']
collection = database['listing']

# Function to get listing id
""" Function returns the listing ID, either by taking input from user or by
determining using other factors, in cases where it is unknown to the user.
Function to be used in other queries as well. Based on the assumption that any
customer/host will be aware of the Neighbourhood Group,
Neighbourhood, Room type, Host Name and Price of the listing they are
interested in. """
def GetListingId(ch):
    if ch == '1':
        listing_id = int(input("Enter listing ID : "))
    elif ch == '2':
        print("Enter the following details")
        neighbourhood_group = input("Neighbourhood Group : ")
        neighbourhood = input("Neighbourhood Area : ")
        room_type = input("Room Type : ")
        host_name = input("Host Name : ")
        price = int(input("Price : "))
        print("\n")
        query = {'$and':[   {"neighbourhood_group":neighbourhood_group},
                            {"neighbourhood":neighbourhood},
                            {"room_type":room_type},
                            {"host_name":host_name},
                            {"price":price}]}
        result = collection.find(query, {"_id":0,"id":1})
        list_result = list(result)
        listing_id = int(list_result[0]["id"])
        if not list_result:
            listing_id = "No such listing exists"
    return listing_id

# Function to display results
"""Function determines the number and order (ascending/descending) of
the results to be displayed. Takes ‘count’ value (number of records
satisfying the conditions) and ‘sort’ (default value ‘0’, sort=1 implies
that it is required to sort the output). Limiting the number of documents
printed only if the total count is more than 5. If less than 5, print all
documents in the ascending order."""
def DisplayResult(count,sort=0):
    print(count,"results found")
    if count > 5:
        n = int(input("Number of records to be displayed : "))
        if sort == 1:
            order = int(input("Order : Descending(-1)\tAscending/No preference(1) : \t"))
        else:
            order = 1
    elif count == 0:
        sys.exit("Sorry, there are no listings satisfying the given conditions")
    else:
        n = count
        order = 1
    return n, order

# Query 1
""" Query to search and display results by category : Neighbourhood Group,
Neighbourhood Area or Room type. Takes a number representing the
criteria to be filtered on, as the parameter. Option provided to sort the
results in ascending or descending order as well by making a call to the
SortBy() function written in query 1. """
def SortBy(query={}, count=None):
    dict_map = {
    	1:"availability_365",
    	2:"price",
    	3:"rating",
    	4:"minimum_nights",
    	5:"number_of_reviews"}
    sort_by = int(input("Enter criteria:\n1.Availability\n2.Price\n3.Rating\n4.Minimum nights\n5.No. of reviews\n"))
    order = int(input("Order of result?\n1.High to low\t2.Low to high\t"))
    if sort_by < 1 or sort_by > 5 or order < 1 or order > 2:
        sys.exit("Invalid entry!")
    sort_by_col = str(dict_map.get(sort_by))
    if order == 1:
        order = -1
    elif order == 2:
        order = 1
    if count != None:
        print("\n",count,"results found")
        if count > 5:
            n = int(input("Number of records to be displayed : "))
            result = collection.find(query,{"_id":0}).sort(sort_by_col,order).limit(n)
        else:
            n = count
            result = collection.find(query,{"_id":0}).sort(sort_by_col)
    else:
        count = collection.count_documents(query)
        print("Total number of records : ", count)
        n = int(input("Number of records to be displayed : "))
        result = collection.find(query,{"_id":0}).sort(sort_by_col,order).limit(n)
    list_result = list(result)
    print("Displaying top", n, "results\n")
    for results in list_result:
        pprint(results)


# Query 2
""" Query to find all listings provided by a particular host. Takes Host Name
as parameter. Option provided to sort the results in ascending or
descending order by making a call to the SortBy() function written in
query 1. If not to be sorted, number of documents displayed to be limited
using the DisplayResult() function. """
def ListByMainCategory(criteria_num):
    dict_map = {
        1:"neighbourhood_group",
        2:"neighbourhood",
        3:"room_type"
    }
    criteria = str(dict_map.get(criteria_num))
    if criteria_num == 1:
            keyword = input("Bronx/ Brooklyn/ Manhattan/ Queens/ Staten Island: ")
    elif criteria_num == 2:
        keyword = input("Enter neighbourhood: ")
    elif criteria_num == 3:
        keyword = input("Private room (or) Shared room (or) Entire home/apt: ")
    else:
        sys.exit("Invalid entry!")
    query = {criteria: keyword,
             "availability_365" : {'$not': {'$lt':'1'}}}
    count = int(collection.count_documents(query))
    ch = int(input("Do you want to sort the results?\n1.Yes\t2.No\t"))
    if ch == 1:
        SortBy(query,count)
    elif ch == 2:
        n, order = DisplayResult(count)
        result = collection.find(query,{"_id":0}).sort(criteria,order).limit(n)
        list_result = list(result)
        if not list_result:
            print("No listing with", criteria, "as", keyword, "present")
        else:
            for results in list_result:
                pprint(results)

# Query 3
""" Query to recursively search and filter accomodations based on different
categories like Neighbourhood Group, Neighbourhood Area and Room
Type. Input desired value to which the field is mapped and recursively
filter results to find the accomodations that best suit your preferences of
all the categories. Option to sort according to selected criteria or limit the
number of records to be displayed. """
def ListByHost(host_name):
    query = {'host_name': host_name}
    count = collection.count_documents(query)
    ch = int(input("Do you want to sort the results?\n1.Yes\t2.No\t"))
    if ch==1 :
        SortBy(query=query, count=count)
    else:
        count = int(collection.count_documents(query))
        n, order = DisplayResult(count)
        result = collection.find(query,{"_id":0}).sort("host_name",order).limit(n)
        list_result = list(result)
        if not list_result:
            print("No listing with ", host_name, " as host name")
        else:
            for results in list_result:
                pprint(results)

# Query 4
""" Query to recursively filter and find records based on lower and upper
bound values of price, rating and number of reviews, that the user wishes
to find listings for. Option to sort results and decide how many records to
display. Recursive conditions are combined using the $and function.
Number of records satisfying the criterias at each stage is displayed as well. """
def ListByCategory():
    flag = True
    dict_map = {
        1:"neighbourhood_group",
        2:"neighbourhood",
        3:"room_type"
    }
    query_list = []
    while flag:
        criteria_num = int(input("\nChoose category:\n1.Neighbourhood group\t\t2.Neighbourhood\t\t3.Room type\n"))
        criteria = str(dict_map.get(criteria_num))
        if criteria_num == 1:
            keyword = input("Bronx/ Brooklyn/ Manhattan/ Queens/ Staten Island: ")
        elif criteria_num == 2:
            keyword = input("Enter neighbourhood: ")
        elif criteria_num == 3:
            keyword = input("Private room (or) Shared room (or) Entire home/apt: ")
        else:
            print("Invalid entry!")
            continue
        query_list.append({criteria:keyword})
        query = {"$and":query_list}
        count = int(collection.count_documents(query))
        ch = int(input("Do you want to sort the results?\n1.Yes\t2.No\t"))
        if ch == 1:
            SortBy(query,count)
        elif ch == 2:
            n, order = DisplayResult(count)
            result = collection.find(query, {"_id":0}).sort(criteria,order).limit(n)
            list_result = list(result)
            for results in list_result:
                pprint(results)
        flag = bool(int(input("Do you want to add another criterion?\tYes(1)\tNo(0)\t: ")))
    if not list_result:
        return "No listing satisfies all conditions"

# Query 5
""" Query to determine the range of price of listings in a particular area. Can
filter based on either Neighbourhood Group alone, or Neighbourhood
Group and Area. Helps the customer in determining how affordable is life
in a particular city for him/her. """
def ListByRange():
    flag = True
    dict_map = {
        1:"price",
        2:"rating",
        3:"number_of_reviews"
    }
    query_list = []
    while flag:
        criteria_num = int(input("\nChoose category:\n1.Price (10$-50$)\t\t2.Rating (1-4.3)\t3.Number of Reviews (1-386)\n"))
        criteria = str(dict_map.get(criteria_num))
        a = float(input("Enter lower bound : "))
        b = float(input("Enter higher bound : "))
        if criteria_num == 1 or criteria_num == 3:
            a = int(a)
            b = int(b)
        if criteria_num < 1 or criteria_num > 3:
            sys.exit("Invalid entry!")
        query_list.append({criteria:{'$lte':b, '$gte':a}})
        query = {"$and":query_list}
        count = int(collection.count_documents(query))
        ch = int(input("Do you want to sort the results?\n1.Yes\t2.No\t"))
        if ch == 1:
            SortBy(query,count)
        elif ch == 2:
            n, order = DisplayResult(count)
            result = collection.find(query,{"_id":0}).sort(criteria,order).limit(n)
            list_result = list(result)
            if not list_result:
                print("No listing with", criteria, "as", keyword, "present")
            else:
                for results in list_result:
                    pprint(results)
        flag = bool(int(input("Do you want to add another criterion?\tYes(1)\tNo(0)\t: ")))

# Query 6
""" Query to display listings based on a keyword in the title. Helps in
filtering based on factors that do not come under any other categories
available. Enables searching based on characteristics of the listing.
Option to sort results and decide how many records to display. Keyword
search is case insensitive and performed using the $regex function. """
def PriceRange(neighbourhood_group):
    print("Enter neighbourhood area in",neighbourhood_group,"\nEnter 0 to skip")
    neighbourhood = input()
    if neighbourhood != '0':
        query = {"neighbourhood_group":neighbourhood_group,"neighbourhood":neighbourhood}
    else:
        query = {"neighbourhood_group":neighbourhood_group}
    result = list(collection.aggregate([
        {'$match':{'$and':[query]}},
        {'$group':{'_id':None, 'minPrice':{'$min':'$price'}, 'maxPrice':{'$max':'$price'}}}]))
    minPrice = result[0]["minPrice"]
    maxPrice = result[0]["maxPrice"]
    print("Price range : ", minPrice, "$ -", maxPrice, "$")

# Query 7
""" Query to sort the records in ascending or descending order based on
selected criteria: Availability, Price, Rating, Minimum Nights or Number
of reviews. Takes query and count as default parameters, since this
function can be used in other queries as well, with different filtration and
count logics. Option to limit the number of documents displayed. """
def ListByKeyword(keyword):
    query = {"name":{'$regex':"(?i).*"+keyword+".*"}}
    count = int(collection.count_documents(query))
    ch = int(input("Do you want to sort the results?\n1.Yes\t2.No\t"))
    if ch == 1:
            SortBy(query,count)
    elif ch == 2:
        n, order = DisplayResult(count, sort=1)
        result = collection.find(query,{"_id":0}).sort("name",order).limit(n)
        list_result = list(result)
        if not list_result:
            print("No listing with", keyword, "present in title")
        else:
            for results in list_result:
                pprint(results)

# Query 8
""" Query for customer to give rating for a specific accommodation. Listing
ID is determined with the help of GetListingId function. Input the rating
you wish to give (out of 5) and it will be updated in the database. This
update also affects other fields such as number of reviews, review value,
reviews per month and last review. The new rating will be average of
all the ratings, number of reviews will be incremented by 1, and last
review (date) will be that of the current date. """
def UpdateRating(ch):
    listing_id = GetListingId(ch)
    if type(listing_id) != int:
        sys.exit(listing_id)
    new_rating = float(input("Enter your rating : "))
    cursor = collection.find({"id":listing_id},{"_id":0})
    print("Current record : ", list(cursor)[0])

    rating_cursor = collection.find({"id":listing_id},{"rating":1})
    number_of_reviews_cursor = collection.find({"id":listing_id},{"number_of_reviews":1})
    review_val_cursor = collection.find({"id":listing_id},{"review_val":1})
    reviews_per_month_cursor = collection.find({"id":listing_id},{"reviews_per_month":1})
    current_rating = float(list(rating_cursor)[0]["rating"])
    current_number_of_reviews = int(list(number_of_reviews_cursor)[0]["number_of_reviews"])
    current_review_val = float(list(review_val_cursor)[0]["review_val"])
    current_reviews_per_month = float(list(reviews_per_month_cursor)[0]["reviews_per_month"])
    avg_rating = (current_review_val + new_rating)/(current_number_of_reviews + 1)
   
    now = datetime.now()
    update_query = {'$set':{   "rating":str(avg_rating),
                                "review_val":str(current_review_val + new_rating),
                                "number_of_reviews":str(current_number_of_reviews+1),
                                "reviews_per_month":str((current_reviews_per_month+1)/30),
                                "last_review":now.strftime("%m/%d/%Y")
                            }
                    }
    collection.update_one({"id":listing_id}, update_query)
    print("\nThank you for your valuable feedback!")
    print("Old rating of listing", listing_id, ":", current_rating)
    print("New rating of listing", listing_id, ":", avg_rating)
    record = collection.find({"id":listing_id},{"_id":0})
    print("\nUpdated Record : ",list(record)[0])

# Query 9
""" Query gives better places for accommodation in the same
neighbourhood based on the selected place of stay. Listing ID
determined with the help of GetListingId() function. Better listings are
selected based on the logic that they will have higher rating and lower
price, compared to the given one. Option to further choose the category 
based on which to display the better recommendations: Price or Ratings.
Option to limit the number of documents to be printed. """
def RecommendBetter(ch):
    listing_id = GetListingId(ch)
    if type(listing_id) != int:
        sys.exit(listing_id)
    query = {"id":listing_id}
    result = collection.find(query,{"_id":0})
    pprint(list(result)[0])
    neighbourhood_cursor = collection.find(query,{"neighbourhood":1})
    neighbourhood = str(list(neighbourhood_cursor)[0]["neighbourhood"])
    price_cursor = collection.find(query,{"price":1})
    price = int(list(price_cursor)[0]["price"])
    rating_cursor = collection.find(query,{"rating":1})
    rating = float(list(rating_cursor)[0]["rating"])
    new_query = {'$and':[{"neighbourhood": neighbourhood},
                        {"price": {'$lt':price}},
                        {"rating": {'$gt':rating}}]    }
    count = int(collection.count_documents(new_query))
    n, order = DisplayResult(count, sort=1)
    sort_by = input("Sort by price or rating?")
    new_result = collection.find(new_query, {"_id":0}).sort(sort_by,order).limit(n)
    list_result = list(new_result)
    if not list_result:
       print("Sorry, no better recommendations found")
    else:
       print("\n",n,"/",count,"cheaper and better listing(s) found\n")
       for results in list_result:
           pprint(results)

# Query 10
""" Query to add a new record (for hosts). Takes the values for all fields that
are to be filled by the host, including host and listing ID. But fields
related to the rating, last review, etc. are left empty, since these are to be
filled by the customer who stayed there. The same record will be added in the 
database as well. Function “insert_one()” is used for the insertion of a new record. """
def AddListing():
    id = int(input("Listing ID : "))
    name = input("Title : ")
    host_id = int(input("Host ID : "))
    host_name = input("Host name : ")
    neighbourhood_group = input("Neighbourhood group : ")
    neighbourhood = input("Neighbourhood : ")
    latitude = float(input("Latitude : "))
    longitude = float(input("Longitude : "))
    room_type = input("Room type : ")
    price = int(input("Price : "))
    minimum_nights = int(input("Minimum number of nights to be booked for : "))
    availability_365 = int(input("Number of days available for booking (out of 365) : "))
    collection.insert_one({
        'id':id,
        'name':name,
        'host_id':host_id,
        'host_name':host_name,
        'neighbourhood_group':neighbourhood_group,
        'neighbourhood':neighbourhood,
        'latitude':latitude,
        'longitude':longitude,
        'room_type':room_type,
        'price':price,
        'minimum_nights':minimum_nights,
        'number_of_reviews':"",
        'last_review':"",
        'reviews_per_month':"",
        'calculated_host_listings_count':"",
        'availability_365':availability_365,
        'review_val':"",
        'rating':"",
        'text_review':""
    })


flag = True
print("\n*** WELCOME TO ACCOMMODATION RECOMMENDATION SYSTEM! ***")
while flag:
    print("\n ---- PLEASE ENTER YOUR CHOICE ----")
    print("1. Sort listings")
    print("2. Search availability by category")
    print("3. View listings of same host at all locations")
    print("4. Filter recursively based on categories")
    print("5. Filter recursively based on range")
    print("6. See price range of listings in a neighbourhood group")
    print("7. Search by keyword(s)")
    print("8. Give your rating for a listing")
    print("9. Get better recommendations for a listing")
    print("10. Add a new listing (for hosts)")
    print("11. Quit")
    i = input("\nYour choice:  ")
    if i == '1':
        SortBy()
    elif i == '2':
        criteria_num = int(input("\nChoose category:\n1.Neighbourhood group\t\t2.Neighbourhood\t\t3.Room type\n"))
        ListByMainCategory(criteria_num)
    elif i == '3':
        host_name = input("Enter the name of the host you want to search listings of :  ")
        ListByHost(host_name)
    elif i == '4':
        ListByCategory()
    elif i == '5':
        ListByRange()
    elif i == '6':
        neighbourhood_group = input("Enter neighbourhood group : ")
        PriceRange(neighbourhood_group)
    elif i == '7':
        keyword = input("Enter keyword(s) : ")
        ListByKeyword(keyword)
    elif i == '8':
        ch = input("Do you know the listing ID?\n1.Yes\t2.No\n")
        UpdateRating(ch)
    elif i == '9':
        ch = input("Do you know the listing ID?\n1.Yes\t2.No\n")
        RecommendBetter(ch)
    elif i == '10':
        AddListing()
    elif i == '11':
        print("Thank you, have a good day!")
        flag = False
    else:
        sys.exit("Invalid Entry!")