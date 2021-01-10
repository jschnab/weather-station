<!doctype html>
<html lang="en">
    <head>
        <meta charset=utf-8>
        <title>Environment Monitoring</title>
    </head>
    <body>
<?php
    $room_name = htmlentities($_POST["room"]);
    if ($room_name != "master bedroom" && $room_name != "living room") {
        echo "invalid room '" . $room_name . "'";
    }
    else { echo "<img src='plot_temp.php?room=" . $room_name . "' />"; }
?>
    </body>
</html>
