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

def getUserById(user_id):
    query_string = 'select * from Users where UserID = $userID'
    result = query(query_string, {'userID': user_id})
    try: return result[0]
    except IndexError: return None

def getCategoryById(item_id):
    query_string = 'select Category from Categories where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    try: return result
    except IndexError: return None


# Wrapper method around web.py's db.query method
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time
def update_auction_time(curr_time):
    t = transaction()
    try: db.update('CurrentTime', where = 'Time = $Time', vars = { 'Time': getTime() }, Time = curr_time)
    except Exception as timeEx: 
        t.rollback() 
        print(str(timeEx))
        raise Exception
    else: t.commit()

#Place a new bid on the specified item for the specifed amount by the user in question
def new_bid(curr_item, curr_user, cur_amount):
    t = transaction()
    try: db.insert('Bids', UserID = curr_user, ItemID = curr_item, Amount = curr_amount, Time = getTime())
    except Exception as bidEx: 
        t.rollback 
        print(str(bidEx))
    else: t.commit()

#Close the auction if the item's buy price has been met, update the item's feilds to reflect the change
def close_auction(curr_item, curr_user, curr_amount):
    t = transaction()
    try: db.update('Items', where = 'ItemID = $ItemID', ItemID = curr_item, Ends = getTime(), Buy_Price = curr_amount)
    except Exception as bidEx: 
        t.rollback 
        print(str(bidEx))
    else: t.commit()


def auction_search(itemID, userID, category, description, minPrice, maxPrice, status):

    if description is None: description = '%%'
    else: description = '%' + description + '%'
    if minPrice == '': minPrice = 0;
    if maxPrice == '': maxPrice = 999999999999999999;

    ####
    #if status == 'close':
    #    query_string = 'select *, group_concat(category,", ") as Category from Items, Categories where (Categories.ItemID = Items.ItemID) AND (IFNULL($category, "") = "" OR $category = Categories.category) AND (IFNULL($itemID, "") = "" OR $itemID = Items.ItemID) AND (IFNULL($userID, "") = "" OR $userID = Items.Seller_UserID) AND (Items.Description LIKE $description) AND (IFNULL(Items.Currently, Items.First_Bid) >= $minPrice) AND (IFNULL(Items.Currently, Items.First_Bid) <= $maxPrice AND (Items.Ends < getTime()) group by Items.ItemID'
    #elif status == 'open':
    #    query_string = 'select *, group_concat(category,", ") as Category from Items, Categories where (Categories.ItemID = Items.ItemID) AND (IFNULL($category, "") = "" OR $category = Categories.category) AND (IFNULL($itemID, "") = "" OR $itemID = Items.ItemID) AND (IFNULL($userID, "") = "" OR $userID = Items.Seller_UserID) AND (Items.Description LIKE $description) AND (IFNULL(Items.Currently, Items.First_Bid) >= $minPrice) AND (IFNULL(Items.Currently, Items.First_Bid) <= $maxPrice AND (Items.Ends > getTime()) AND (Items.Started < getTime()) group by Items.ItemID'
    #elif status == 'notStarted':
    #    query_string = 'select *, group_concat(category,", ") as Category from Items, Categories where (Categories.ItemID = Items.ItemID) AND (IFNULL($category, "") = "" OR $category = Categories.category) AND (IFNULL($itemID, "") = "" OR $itemID = Items.ItemID) AND (IFNULL($userID, "") = "" OR $userID = Items.Seller_UserID) AND (Items.Description LIKE $description) AND (IFNULL(Items.Currently, Items.First_Bid) >= $minPrice) AND (IFNULL(Items.Currently, Items.First_Bid) <= $maxPrice) AND (Items.Started > getTime()) group by Items.ItemID'
    #else:
    
    query_string = 'select *, group_concat(category,", ") as Category from Items, Categories where (Categories.ItemID = Items.ItemID) AND (IFNULL($category, "") = "" OR $category = Categories.category) AND (IFNULL($itemID, "") = "" OR $itemID = Items.ItemID) AND (IFNULL($userID, "") = "" OR $userID = Items.Seller_UserID) AND (Items.Description LIKE $description) AND (IFNULL(Items.Currently, Items.First_Bid) >= $minPrice) AND (IFNULL(Items.Currently, Items.First_Bid) <= $maxPrice) group by Items.ItemID'

    result = query(query_string, {'category': category, 'itemID': itemID, 'userID': userID, 'description': description, 'minPrice': minPrice, 'maxPrice': maxPrice });
    try: return result
    except IndexError: return None








