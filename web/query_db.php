<?php
function query_db($param_name, $room_name, $timescale) {
    if ($timescale == "day") {
        $interval = "1 day";
    }
    elseif ($timescale == "3days") {
        $interval = "3 day";
    }
    elseif ($timescale == "week") {
        $interval = "7 day";
    }
    else {
        $interval = "1 day";
    }
    try {
        $user = getenv("DB_USER");
        $pw = getenv("DB_PASSWD");
        $con_str = "mysql:host=localhost;dbname=weather_station";
        $sql_query = <<<EOT
        select x.timestamp ts, x.value val, l.name loc
        from $param_name x
        join location l
        on x.location_id = l.id
        where x.timestamp >= now() - interval $interval
        and l.name = ?
EOT;
        $db = new PDO($con_str, $user, $pw);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $stmt = $db->prepare($sql_query);
        $stmt->execute(array($room_name));
        $timestamps = array();
        $values = array();
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            array_push($timestamps, strtotime($row["ts"]));
            array_push($values, floatval($row["val"]));
        }
    }

    catch (PDOException $e) {
        printf("Error: %s\n", $e->getMessage());
    }

    return array("timestamps"=>$timestamps, "values"=>$values);
}
?>
