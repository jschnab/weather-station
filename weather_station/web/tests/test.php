<?php
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph.php");
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph_line.php");
require_once("/usr/share/jpgraph-4.3.4/src/jpgraph_date.php");

$ydata = array(11, 3, 8, 12, 5, 1, 9, 13, 5, 7);
$graph = new Graph(350, 250);
$graph->SetScale("textlin");
$lineplot = new LinePlot($ydata);
$lineplot->SetColor("blue");
$graph->Add($lineplot);
$graph->Stroke();
?>
