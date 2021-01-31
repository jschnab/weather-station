<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
	<link rel="stylesheet" href="styles.css">
        <title>Home Environment Monitoring</title>
    </head>
    <body>
    <div id="layout">
    <nav>
    <ul>
<?php
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
echo "<li><a href='index.php?param=summary&timescale=$timescale'>Summary</a></li>";
echo "</ul>";
echo "</nav>";
echo "<div id='selectors'>";
echo "<form action='index.php' method='GET'>";
echo "<input type='hidden' name='param' value='$param'>";
echo "<select name='timescale' id='timescale-select' onchange='this.form.submit()'>";
if ($timescale == "day") {
    echo "<option value='day' selected>Last day</option>";
}
else {
    echo "<option value='day'>Last day</option>";
}
if ($timescale == "3days") {
    echo "<option value='3days' selected>Last 3 days</option>";
}
else {
    echo "<option value='3days'>Last 3 days</option>";
}
if ($timescale == "week") {
    echo "<option value='week' selected>Last week</option>";
}
else {
    echo "<option value='week'>Last week</option>";
}
echo "</select>";
echo "</form>";
echo "</div>";
echo "<div id='plots'>";
echo "<img id='plotA' src='make_plot.php?param=$param&room=living%20room&timescale=$timescale'/>";
echo "<img id='plotB' src='make_plot.php?param=$param&room=master%20bedroom&timescale=$timescale'/>";
?>
</div> <!-- plots -->
</div> <!-- layout -->
</body>
</html>
