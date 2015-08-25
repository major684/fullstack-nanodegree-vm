#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
	# Connect to database
	conn = connect()
	cur = conn.cursor()
	# Truncate all records from matches table
	cur.execute("TRUNCATE TABLE Matches;")
	conn.commit()
	# Close communication with the database
	cur.close()
	conn.close()
	
def deletePlayers():
    """Remove all the player records from the database."""
	# Connect to database
	conn = connect()
	cur = conn.cursor()
	# Truncate all records from Players table
	cur.execute("TRUNCATE TABLE Players;")
	conn.commit()
	# Close communication with the database
	cur.close()
	conn.close()
	
def countPlayers():
    """Returns the number of players currently registered."""
	# Connect to database
	conn = connect()
	cur = conn.cursor();
	# Get number of players registered in players table
	cur.execute("SELECT Count(*) FROM Players;")
	results = cur.fetchall()
	# Close communication with the database
	cur.close()
	conn.close()
	return results

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
	# Connect to database
	conn = connect()
	cur = conn.cursor()
	# Insert data into table
	cur.execute("INSERT INTO Players (Name) VALUES (%s)",
				(name))
	conn.commit()
	# Close communication with the database
	cur.close()
	conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
	# Connect to database
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT ID, Name, Wins, Matches FROM Standings;")
	results = cur.fetchall()
	# Close communication with the database
	cur.close()
	conn.close()
	return results
	
def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
 	# Connect to database
	conn = connect()
	cur = conn.cursor()
	# Insert data into table
	cur.execute("INSERT INTO Matches (Winner, Loser) VALUES (%s, %s)",
				(winner, loser))
	conn.commit()
	# Close communication with the database
	cur.close()
	conn.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
	# Connect to database
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT ID, Name, Wins FROM Standings ORDER BY Wins ASC;")
	results = cur.fetchall()
	# Close communication with the database
	cur.close()
	conn.close()
	# Initialize empty list
	swiss = []
	# Set counter to iterate through rows
	i = 0
	# Iterate through rows and set results to variable
    while i < len(results):
        playerAid = results[i][0]
        playerAname = results[i][1]
        playerBid = results[i+1][0]
        playerBname = results[i+1][1]
        swiss.append((playerAid,playerAname,playerBid,playerBname))
	# Set counter to select next pair
        i=i+2
	return swiss

