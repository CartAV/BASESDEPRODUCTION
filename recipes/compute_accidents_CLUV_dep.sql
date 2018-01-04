SELECT 
    "current_name" AS "current_name",
    "dep" AS "dep",
    SUM("tue_nb") AS "tue_nb_sum",
    COUNT(*) AS "count"
  FROM "accidents_cluv_prepared"
  WHERE "date" >= '2015-01-01 00:00:00+00' AND "nom_circonscription_police" != '' AND ("nom_circonscription_police" IS NOT NULL)
  GROUP BY "current_name", "dep"