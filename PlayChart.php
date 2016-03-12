<?php

//$appid = "com.venmo";
$appid = htmlspecialchars($_GET["appid"]);
$category = htmlspecialchars($_GET["category"]);
$collection = htmlspecialchars($_GET["collection"]);

//$pdo = new PDO('sqlite:/home/chris/playstore.db');
$pdo = new PDO('sqlite:/Users/chris/workspace/cgi-bin/PlayScraper/playstoreX.db');

$stmt = $pdo->prepare('SELECT date,rank FROM rank_data WHERE appid=:appid AND category=:category AND collection=:collection ORDER BY date ASC');
//$stmt = $pdo->prepare('SELECT date,rank FROM rank_data WHERE appid = :appid');
$stmt->execute(array('appid' => $appid, 'category' => $category, 'collection' => $collection));

$datapie = array();

//$result->setFetchMode(PDO::FETCH_ASSOC);

foreach ($stmt as $row) {
    // do something with $row
    extract($row);

    $datapie[] = array($date, $rank);
}



$data = json_encode($datapie);
header('Content-type: application/json');
//echo "Content-type: application/json\n";
//echo "\n";
echo $data;
//echo "\n";
?>
