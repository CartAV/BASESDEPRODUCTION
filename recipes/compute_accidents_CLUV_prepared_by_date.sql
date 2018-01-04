SELECT
    "dep_code",
    FIRST_VALUE("gravite") OVER (
        PARTITION BY "dep"
        ORDER BY
            "gravite" DESC
    ) AS "ville",
    FIRST_VALUE("ville") OVER (
        PARTITION BY "dep"
        ORDER BY
            "gravite" DESC
    ) AS "ville"
FROM
    (
        SELECT
            "dep" as "dep_code",
            "current_name" as "ville",
            10 * sum("tue_nb") + sum("hospitalise_nb") as "gravite"
        FROM
            "accidents_cluv_prepared"
        WHERE
            ("tue_nb" = 1)
            OR ("hospitalise_nb" = 1)
    ) "dku__beforefirstlast"
