<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
	<link rel="stylesheet" href="styles.css">
        <title>Home Environment Monitoring</title>
    </head>
    <body>
    <div id="layout-summary">
    <nav>
    <ul>
<?php
require_once("query_db.php");
if (isset($_GET["param"])) {
    $param = $_GET["param"];    
}
else {
    $param = "temperature";
}
if (isset($_GET["timescale"])) {
    $timescale = $_GET["timescale"];    
}
else {
    $timescale = "day";
}
echo "<li><a href='index.php?param=temperature&timescale=$timescale'>Temperature</a></li>";
echo "<li><a href='index.php?param=humidity&timescale=$timescale'>Humidity</a></li>";
echo "<li><a href='summary.php'>Summary</a></li>";
echo "</ul>";
echo "</nav>";
echo "<div id='summary-tables'>";
echo "<section class='summary-section' id='living-room'>";
echo "<h1 class='summary-room-name'>Living Room</h1>";
echo "<table>";
echo "<tr>";
echo "<td>Current temperature</td>";
echo "<td class='value'>" . current_param("temperature", "living room") . " &deg;C</td>";
echo "</tr>";
echo "<tr>";
echo "<td>Current humidity</td>";
echo "<td class='value'>" . current_param("humidity", "living room") . " %</td>";
echo "</tr>";
//echo "<tr>";
//echo "<td>Average day temperature</td>";
//echo "<td>" . average_day_param("temperature", "living room") . "</td>";
//echo "</tr>";
echo "</table>";
echo "</section>";
echo "<section class='summary-section' id='master-bedroom'>";
echo "<h1 class='summary-room-name'>Master Bedroom</h1>";
echo "<table>";
echo "<tr>";
echo "<td>Current temperature</td>";
echo "<td class='value'>" . current_param("temperature", "master bedroom") . " &deg;C</td>";
echo "</tr>";
echo "<tr>";
echo "<td>Current humidity</td>";
echo "<td class='value'>" . current_param("humidity", "master bedroom") . " %</td>";
echo "</tr>";
?>
</div> <!-- summary-tables -->
</div> <!-- layout -->
</body>
</html>
