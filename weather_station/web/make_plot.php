<?php
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph.php");
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph_line.php");
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph_date.php");
require_once("query_db.php");

// query database
$results = time_series($_GET["param"], $_GET["room"], $_GET["timescale"]);

// setup plot
$graph = new Graph(700, 440);
$graph->SetMargin(60, 0, 0, 70);
$graph->SetScale("datlin");
$graph->ygrid->SetFill(false);  // call after graph->SetScale()
if ($_GET["room"] == "master_bedroom") {
    $room_name = "master bedroom";
}
elseif ($_GET["room"] == "living_room") {
    $room_name = "living room";
}
$title = ucwords($_GET["param"]) ." in " . $room_name;
$graph->title->Set($title);
$graph->title->SetFont(FF_DV_SANSSERIF, FS_NORMAL, 15);

// adjust time axis
$graph->xaxis->SetLabelAngle(45);
if ($_GET["timescale"] == "day") {
    $graph->xaxis->scale->ticks->Set(2*3600);  // every 2 hours
}
elseif ($_GET["timescale"] == "3days") {
    $graph->xaxis->scale->ticks->Set(6*3600);  // every 6 hours
}
elseif ($_GET["timescale"] == "week") {
    $graph->xaxis->scale->ticks->Set(12*3600);  // every 12 hours
}
$graph->xaxis->scale->SetDateFormat("m/d H:i");
$graph->xaxis->SetFont(FF_DV_SANSSERIF, FS_NORMAL, 8);

// adjust y-axis
if ($_GET["param"] == "temperature") {
    $graph->yaxis->SetTitle("Temperature (deg. Celsius)", "center");
}
if ($_GET["param"] == "humidity") {
    $graph->yaxis->SetTitle("Relative humidity (%)", "center");
}
$graph->yaxis->SetTitleMargin(35);
$graph->yaxis->title->SetFont(FF_DV_SANSSERIF, FS_NORMAL, 13);
$graph->yaxis->SetFont(FF_DV_SANSSERIF, FS_NORMAL, 8);
$graph->yaxis->SetLabelMargin(0);

$graph->xgrid->Show();

// plot results
$lineplot = new LinePlot($results["values"], $results["timestamps"]);
$lineplot->SetColor("blue");
$graph->Add($lineplot);
$graph->Stroke();
?>
