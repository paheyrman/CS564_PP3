#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib')
import os                            

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/add_bid', 'place_bid',
        '/appbase', 'appbase',
        '/search', 'auction_search',
        '/items', 'selected_item',
        '/', 'curr_time')

class selected_item:
     def GET(self):
        post_params = web.input()
        auction_id = post_params['id']
        val = sqlitedb.auction_search(auction_id, "", "", "", "", "", "")
        Name = val[0]['Name']
        Category = val[0]['Category']
        Ends = val[0]['Ends']
        Started = val[0]['Started']
        Number_of_Bids = val[0]['Number_of_Bids']
        Seller = val[0]['Seller_UserID']
        Description = val[0]['Description']
        print(Name)


        return render_template('items.html', id = auction_id, search_result = val, Name = Name, Category = Category, Ends = Ends, Started = Started, Number_of_Bids = Number_of_Bids, Seller = Seller, Description = Description)

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)


class select_time:
    # Another GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss']
        enter_name = post_params['entername']

        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        try: sqlitedb.update_auction_time(selected_time)
        except Exception as timeEx: 
            update_message = 'Unable to update time, time value selected is not valid'
            print(str(timeEx))
        return render_template('select_time.html', message = update_message)


class place_bid:

    def GET(self):
        return render_template('add_bid.html')

    def POST(self):
        post_params = web.input()
        itemID = post_params['itemID']
        userID = post_params['userID']
        Amount = post_params['price']

        #Verify the correct search criteria was entered
        if itemID == '' or userID == '' or Amount == '':
            #If not entered, prompt user to conduct a new search with the appropriate values entered
            return render_template('add_bid.html', message = 'Invalid search criteria, ensure ItemID, UserID, Amount are valid.')
        else:
            #If entered, obtain the item and user information specified by the search criteria
            curr_item = sqlitedb.getItemById(itemID)
            curr_user = sqlitedb.getUserById(userID)

        #Verify the item is valid in the database
        if curr_item is None:
            return render_template('add_bid.html', message = 'Unable to find item, ItemID is invalid.')
        #Verify the user is valid in the database
        elif curr_user is None:
            return render_template('add_bid.html', message = 'Unable to find user, UserID is invalid.')
        #Vefify the user is not bidding on an item they are also selling
        elif curr_user == curr_item.Seller_UserID:
            return render_template('add_bid.html', message = 'Unable to place bid, users may not bid on items they are selling.')
        #Verify the auction has not concluded
        elif string_to_time(sqlitedb.getTime()) >= string_to_time(curr_item.Ends):
            return render_template('add_bid.html', message = 'Unable to place bid, auction has ended.')
        #Verify the auction has begun
        elif string_to_time(sqlitedb.getTime()) < string_to_time(curr_item.Started):
            return render_template('add_bid.html', message = 'Unable to place bid, auction has not started.')
        #Verify a valid bid amount was entered
        elif Amount < 0 or Amount <= curr_item.First_Bid or Amount <= curr_item.Currently:
            return render_template('add_bid.html', message = 'Unable to place bid, amount specified is invalid.')
        #Verify the item has a buy price, if buy price is met close the auction
        elif curr_item.Buy_Price is not None and Amount >= curr_item.Buy_Price:
            curr_item.Number_of_Bids += 1
            curr_item.Currently = Amount
            sqlitedb.close_auction(itemID,userID,Amount)
            successful_purchase = '(Congratulations! You have purchased item: %s for amount: %s.)' % (curr_item.Name,Amount)
            return render_template('add_bid.html', message = 'successful_purchase')
        #Verified no errors exist, place a new bid on the item for the amount specified
        else:
            curr_item.Number_of_Bids += 1
            curr_item.Currently = Amount
            sqlitedb.new_bid(itemID,userID,Amount)
            successful_bid = '(Congratulations! You have placed a bid on item: %s of amount: %s.)' % (curr_item.Name,Amount)
            return render_template('add_bid.html', message = 'successful_bid')


class auction_search:

    def GET(self):
        return render_template('search.html')

    def POST(self):
        post_params = web.input()
        itemID = post_params['itemID']
        userID = post_params['userID']
        category = post_params['category']
        description = post_params['description']
        minPrice = post_params['minPrice']
        maxPrice = post_params['maxPrice']
        status = post_params['status']

        val = sqlitedb.auction_search(itemID, userID, category, description, minPrice, maxPrice, status)
        return render_template('search.html', search_result = val)
###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()

