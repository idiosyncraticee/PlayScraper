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
$result = [];

$stmt->setFetchMode(PDO::FETCH_ASSOC);
$result['results'] = $stmt->fetchall();
//print_r($result);
//while ($row = $stmt->fetchall()) {
//foreach ($stmt as $row) {
    // do something with $row
//    extract($row);

//    $datapie[] = array($date, $rank);
//}


//http://localhost/workspace/cgi-bin/playscraper/playchart.php?appid=com.twoergo.foxbusiness&category=FINANCE&collection=topselling_free
//$data = json_encode($datapie);

$data = json_encode($result);
header('Content-type: application/json');
header('Access-Control-Allow-Origin: *');
//echo "Content-type: application/json\n";
//echo "\n";
echo $data;
//echo "\n";
?>
