-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE IF EXISTS tournament;
DROP VIEW IF EXISTS Standings;
DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Players;
-- Create Database for tournament project

CREATE DATABASE tournament;

-- Create Tables needed for tracking tournament matches

CREATE TABLE Players (
 ID serial PRIMARY KEY,
 Name varchar(50),
 Date_Created timestamp DEFAULT current_timestamp
);

CREATE TABLE Matches (
 ID serial PRIMARY KEY,
 Winner integer references Players(ID),
 Looser integer references Players(ID),
 Match_Date timestamp DEFAULT current_timestamp
);

--Create a view that shows current standings
CREATE VIEW Standings AS
WITH Wins as(
 SELECT 
		Players.ID,
		Name,
		COALESCE(COUNT(Winner), 0) AS Wins
	FROM Players 
	LEFT JOIN Matches 
	ON Players.ID = Matches.Winner
	GROUP BY Players.ID,Name
  ), Losses AS (
 SELECT 
		Players.ID,
		Name,
		COALESCE(COUNT(Looser),0) AS Losses
	FROM Players 
	LEFT JOIN Matches 
	ON Players.ID = Matches.Looser
	GROUP BY Players.ID,Name
	), Combined AS(
	SELECT ID, Name, Wins, 0 AS Losses FROM Wins
	UNION ALL
	SELECT ID, Name, 0 AS Wins, Losses From Losses
	)
	SELECT ID,
		   Name,
		   SUM(Wins) AS Wins,
		   SUM(Losses) AS Losses,
		   SUM(Wins) + SUM(Losses) AS Matches
	FROM Combined
	GROUP BY ID, Name


