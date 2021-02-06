<?php
function time_series($param_name, $room_name, $timescale) {
    try {
        $user = getenv("DB_USER");
        $pw = getenv("DB_PASSWD");
        $con_str = "mysql:host=localhost;dbname=weather_station";
        $sql_query1 = <<<EOT
set @std_dev := (select avg(roll_std) from ${param_name}_{$timescale}_rolling_{$room_name})
EOT;
	if ($timescale == "day") {
	    $sql_query2 = <<<EOT
select ts, val from ${param_name}_{$timescale}_rolling_{$room_name}
where val > roll_avg - 10 * @std_dev and val < roll_avg + 10 * @std_dev;
EOT;
	}
	elseif ($timescale == "3days") {
	    $sql_query2 = <<<EOT
with temp as (select ts, val from ${param_name}_{$timescale}_rolling_{$room_name}
where val > roll_avg - 10 * @std_dev and val < roll_avg + 10 * @std_dev)
select ts as ts, avg(val) over(order by temp.ts rows between 60 preceding
and current row) as val from temp;
EOT;
	}
	elseif ($timescale == "week") {
	    $sql_query2 = <<<EOT
with temp as (select ts, val from ${param_name}_{$timescale}_rolling_{$room_name}
where val > roll_avg - 10 * @std_dev and val < roll_avg + 10 * @std_dev)
select ts as ts, avg(val) over(order by temp.ts rows between 60 preceding
and current row) as val from temp;
EOT;

	}

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


function current_param($param_name, $room_name) {
    try {
        $user = getenv("DB_USER");
        $pw = getenv("DB_PASSWD");
        $con_str = "mysql:host=localhost;dbname=weather_station";
	$sql_query = <<<EOT
	select x.timestamp ts, x.value val, l.name loc
	from $param_name x
	join location l
	on x.location_id = l.id
	where x.timestamp in (
	    select max(x.timestamp)
	    from $param_name x
	    join location l
	    on x.location_id = l.id
	    and l.name = ?
	)
	and l.name = ?
EOT;
        $db = new PDO($con_str, $user, $pw);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	$stmt = $db->prepare($sql_query);
	$stmt->execute(array($room_name, $room_name));
    }

    catch (PDOException $e) {
        printf("Error: %s\n", $e->getMessage());
    }

    $value = $stmt->fetch(PDO::FETCH_ASSOC)["val"];
    return number_format($value, 1);
}
?>
