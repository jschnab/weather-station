<!doctype html>
<html lang="en">
    <head>
        <meta charset=utf-8>
        <title>Environment Monitoring</title>
    </head>
    <body>
    <?php
    require_once("/var/share/jpgraph-4.3.4/src/jpgraph.php");
    require_once("/var/share/jpgraph-4.3.4/src/jpgraph_line.php");
    printf("Temperature in %s<br><br>", $_POST["room"]);
    try {
        $db = new PDO("mysql:host=localhost;dbname=weather_station", getenv("DB_USER"), getenv("DB_PASSWD"));
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $results = $db->query("select t.timestamp ts, t.value val, l.name loc from temperature t join location l on t.location_id = l.id limit 10");
        printf("<table cellpadding='3'>");
        printf("<tr><th>Timestamp</th> <th>Value</th> <th>Location</th></tr>");
        while ($row = $results->fetch(PDO::FETCH_ASSOC)) {
            $row_text = "<tr><td>%s</td> <td>%.2f</td> <td>%s</td></tr>";
            printf($row_text, $row["ts"], $row["val"], $row["loc"]);
        }
    }
    catch (PDOException $e) {
        printf("Error: %s\n", $e->getMessage());
    }
    ?>
    </body>
</html>
