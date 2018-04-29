import web

db = web.database(dbn = 'sqlite', db = 'AuctionBase')

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    query_string = 'select Time from CurrentTime'
    results = query(query_string)
    return results[0].Time

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    query_string = 'select * from Items where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    try: return result[0]
    except IndexError: return None

def getUserByID(user_id):
    query_string = 'select * from Users where UserID = $userID'
    result = query(query_string, {'userID': user_id})
    try: return result[0]
    except IndexError: return None

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
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








