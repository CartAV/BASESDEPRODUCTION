SELECT 
    "dep" AS "dep",
    MIN("null_current_city_code_current_name_dku_fst") AS "null_current_city_code_current_name_first",
    SUM("null_current_city_code_count") AS "null_current_city_code_count"
  FROM (
    SELECT 
        "dep",
        "current_city_code",
        "current_name",
        "null_current_city_code_current_name",
        "null_current_city_code_count",
        FIRST_VALUE("null_current_city_code_current_name") OVER (PARTITION BY "dep", CASE 
          WHEN "current_city_code" IS NULL THEN '0'
          ELSE '1'
        END ORDER BY "current_name" ASC NULLS FIRST ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS "null_current_city_code_current_name_dku_fst"
      FROM (
        SELECT 
            "dep",
            "current_city_code",
            "current_name",
            CASE 
              WHEN "current_city_code" IS NULL THEN "current_name"
            END AS "null_current_city_code_current_name",
            CASE 
              WHEN "current_city_code" IS NULL THEN 1
              ELSE 0
            END AS "null_current_city_code_count"
          FROM "accidents_cluv_prepared"
          WHERE ("tue_nb" = 1) OR ("hospitalise_nb" = 1)
        ) "dku__beforefirstlast"
    ) "dku__beforegrouping"
  GROUP BY "dep"