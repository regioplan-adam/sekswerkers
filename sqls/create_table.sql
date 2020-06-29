-- Create a new table called 'TableName' in schema 'SchemaName'
-- Drop the table if it already exists
IF OBJECT_ID('sekswerkersScraper', 'U') IS NOT NULL
DROP TABLE sekswerkersScraper
GO
-- Create the table in the specified schema
CREATE TABLE sekswerkersScraper
(
    [sk_id] INT IDENTITY(1000000,1) PRIMARY KEY NOT NULL, -- primary key column
    [id] varchar(255),
	[aanbieder] varchar(255),
	[datum] varchar(255),
	[gender] varchar(255),
	[type_ontvangst] varchar(255),
	[afkomst] varchar(255),
	[leeftijd] INT,
	[prijzen] INT,
	[escort_prijzen] INT,
	[woonplaats] varchar(255),
	[gm_code] varchar(255),    
	[scr_tag] text,
	[url] varchar(255),
	[advertentie_tekst] text,
	[timestamp] INT
);
GO