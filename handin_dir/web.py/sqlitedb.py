###########################################################################################
# Authors: Benjamin Charles 9071177506
#          Paul Heyrman     9071315551
#          Noah Krause      9071587712
###########################################################################################
# Description: This file provides the interactions between the front-end website and the
#              database. It calls functions to execute SQLite queries against the database
#              with parameters recieved from auctionbase.py and returns the results to be
#              displayed in HTML. 
###########################################################################################
import web

db = web.database(dbn = 'sqlite', db = 'AuctionBase')

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()

# Returns the current time from your database
def getTime():
    query_string = 'select Time from CurrentTime'
    results = query(query_string)
    return results[0].Time

# Returns a single item specified by the Item's ID in the database
def getItemById(item_id):
    query_string = 'select * from Items where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    try: return result[0]
    except IndexError: return None

# Returns category based on ID
def getCategoryById(item_id):
    query_string = 'select group_concat(Category,", ") as Category from Categories where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    try: return result[0]
    except IndexError: return None

# Select bid by ID
def getBidById(item_id):
    query_string = 'select UserID as "ID of Bidder", Time as "Time of Bid", Amount as "Price of Bid" from Bids where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    try: return result
    except IndexError: return None

# Select winner by itemID and Max Bid
def getWinnerById(item_id):
    query_string = 'select * from Bids where ItemID = $itemID and Amount = (select Max(Amount) from Bids where ItemID = $itemID)'
    result = query(query_string, {'itemID': item_id})
    try: return result[0]
    except IndexError: return None

# return user info by ID
def getUserById(user_id):
    query_string = 'select * from Users where UserID = $userID'
    result = query(query_string, {'userID': user_id})
    try: return result[0]
    except IndexError: return None


# Wrapper method around web.py's db.query method
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time
def update_auction_time(curr_time):
    t = transaction()
    try: db.update('CurrentTime', where = 'Time = $cTime', vars = { 'cTime': getTime() }, Time = curr_time)
    except Exception as timeEx: 
        t.rollback() 
        print(str(timeEx))
        raise Exception
    else: t.commit()

#Place a new bid on the specified item for the specifed amount by the user in question
def new_bid(curr_item, curr_user, curr_amount):
    t = transaction()
    try: db.insert('Bids', UserID = curr_user, ItemID = curr_item, Amount = curr_amount, Time = getTime())
    except Exception as bidEx: 
        t.rollback()
        return False
    else: 
        t.commit()
        return True
        

def auction_search(itemID, userID, category, description, minPrice, maxPrice, status):

    if description is None: description = '%%'
    else: description = '%' + description + '%'
    if minPrice == '': minPrice = 0;
    else: minPrice = int(minPrice)
    if maxPrice == '': maxPrice = 999999999999999999;
    else: maxPrice = int(maxPrice)

    #query will depend on status of the auction
    if status == 'open':
        query_string = 'select *, group_concat(category,", ") as Category from Items, Categories, CurrentTime where (Categories.ItemID = Items.ItemID) AND (IFNULL($category, "") = "" OR $category = Categories.category) AND (IFNULL($itemID, "") = "" OR $itemID = Items.ItemID) AND (IFNULL($userID, "") = "" OR $userID = Items.Seller_UserID) AND (Items.Description LIKE $description) AND (IFNULL(Items.Currently, Items.First_Bid) >= $minPrice) AND (IFNULL(Items.Currently, Items.First_Bid) <= $maxPrice) AND (Items.Started <= CurrentTime.Time AND Items.Ends >= CurrentTime.Time) group by Items.ItemID'
    if status == 'close':
        query_string = 'select *, group_concat(category,", ") as Category from Items, Categories, CurrentTime where (Categories.ItemID = Items.ItemID) AND (IFNULL($category, "") = "" OR $category = Categories.category) AND (IFNULL($itemID, "") = "" OR $itemID = Items.ItemID) AND (IFNULL($userID, "") = "" OR $userID = Items.Seller_UserID) AND (Items.Description LIKE $description) AND (IFNULL(Items.Currently, Items.First_Bid) >= $minPrice) AND (IFNULL(Items.Currently, Items.First_Bid) <= $maxPrice) AND (Items.Ends < CurrentTime.Time) group by Items.ItemID'
    if status == 'notStarted': 
        query_string = 'select *, group_concat(category,", ") as Category from Items, Categories, CurrentTime where (Categories.ItemID = Items.ItemID) AND (IFNULL($category, "") = "" OR $category = Categories.category) AND (IFNULL($itemID, "") = "" OR $itemID = Items.ItemID) AND (IFNULL($userID, "") = "" OR $userID = Items.Seller_UserID) AND (Items.Description LIKE $description) AND (IFNULL(Items.Currently, Items.First_Bid) >= $minPrice) AND (IFNULL(Items.Currently, Items.First_Bid) <= $maxPrice) AND (Items.Started > CurrentTime.Time) group by Items.ItemID'
    if status == 'all':
        query_string = 'select *, group_concat(category,", ") as Category from Items, Categories, CurrentTime where (Categories.ItemID = Items.ItemID) AND (IFNULL($category, "") = "" OR $category = Categories.category) AND (IFNULL($itemID, "") = "" OR $itemID = Items.ItemID) AND (IFNULL($userID, "") = "" OR $userID = Items.Seller_UserID) AND (Items.Description LIKE $description) AND (IFNULL(Items.Currently, Items.First_Bid) >= $minPrice) AND (IFNULL(Items.Currently, Items.First_Bid) <= $maxPrice) group by Items.ItemID'
    
    result = query(query_string, {'category': category, 'itemID': itemID, 'userID': userID, 'description': description, 'minPrice': minPrice, 'maxPrice': maxPrice});
    try: return result
    except IndexError: return None