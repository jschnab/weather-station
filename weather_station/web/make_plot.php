<?php
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph.php");
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph_line.php");
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph_date.php");
require_once("query_db.php");

// query database
$results = query_db($_GET["param"], $_GET["room"], $_GET["timescale"]);

// setup plot
$graph = new Graph(600, 400);
$graph->SetMargin(60, 40, 30, 130);
$graph->SetScale("datlin");
$graph->ygrid->SetFill(false);  // call after graph->SetScale()
$title = "Temperature in " . $_GET["room"];
$graph->title->Set($title);

// adjust time axis
$graph->xaxis->SetLabelAngle(45);
$graph->xaxis->scale->ticks->Set(4*3600);  // every 2 hours
$graph->xaxis->scale->SetDateFormat("m/d H:i");
$graph->xgrid->Show();

// plot results
$lineplot = new LinePlot($results["values"], $results["timestamps"]);
$lineplot->SetColor("blue");
$graph->Add($lineplot);
$graph->Stroke();
?>
