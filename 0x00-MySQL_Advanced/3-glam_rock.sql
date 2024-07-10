--lists all Glam rock bands ranked by their longevity
SELECT band_name,
       CASE 
           WHEN split IS NULL THEN 2022 - formed
           ELSE split - formed
       END AS lifespan
FROM bands
WHERE main_style = 'Glam rock'
ORDER BY lifespan DESC;