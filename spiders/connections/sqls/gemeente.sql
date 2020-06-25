SELECT 
    gemeente, 
    woonplaats, 
    plaatsen_en_buurtschappen, 
    gemeentecode 
FROM plaatsenGemeentenNL
GROUP BY 
    gemeente, 
    woonplaats, 
    plaatsen_en_buurtschappen, 
    gemeentecode