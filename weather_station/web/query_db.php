<?php
function query_db($param_name, $room_name, $timescale) {
    try {
        $user = getenv("DB_USER");
        $pw = getenv("DB_PASSWD");
        $con_str = "mysql:host=localhost;dbname=weather_station";
        $sql_query1 = <<<EOT
set @std_dev := (select avg(roll_std) from ${param_name}_{$timescale}_rolling_{$room_name})
EOT;
	$sql_query2 = <<<EOT
select ts, val from ${param_name}_{$timescale}_rolling_{$room_name}
where val > roll_avg - 10 * @std_dev and val < roll_avg + 10 * @std_dev;
EOT;
        $db = new PDO($con_str, $user, $pw);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	$db->query($sql_query1);
	$results = $db->query($sql_query2);
        $timestamps = array();
        $values = array();
        while ($row = $results->fetch(PDO::FETCH_ASSOC)) {
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
